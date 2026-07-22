from __future__ import annotations

from datetime import timedelta
from threading import RLock
from typing import Any, Protocol

from project_core.domain.contracts.interactive import (
    AnalysisCheckpoint,
    AnalysisEvent,
    AnalysisEventType,
    AnalysisJob,
    ArtifactMetadata,
    AttachmentMetadata,
    ExecutionStatus,
    InteractionResult,
    InteractionStatus,
    PendingInteraction,
    SessionSummary,
    TranscriptEntry,
    utc_now,
)


class RepositoryConflict(RuntimeError):
    pass


class RepositoryNotFound(KeyError):
    pass


_PRIVATE_KEYS = {
    "_id",
    "chain_of_thought",
    "cot",
    "internal_prompt",
    "system_prompt",
    "raw_prompt",
    "secret",
    "token",
    "sql",
    "suggested_sql",
    "sql_predicate",
    "probe_sql",
    "path",
    "parquet_path",
}


def sanitize_public_data(value: Any) -> Any:
    """Remove server-only material before an event is persisted for browser replay."""
    if isinstance(value, dict):
        return {
            str(key): sanitize_public_data(item)
            for key, item in value.items()
            if str(key).casefold() not in _PRIVATE_KEYS
        }
    if isinstance(value, list):
        return [sanitize_public_data(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_public_data(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


class AnalysisRepository(Protocol):
    def ensure_indexes(self) -> None: ...
    def create_job(self, job: AnalysisJob) -> tuple[AnalysisJob, bool]: ...
    def get_job(self, analysis_id: str, actor_id: str | None = None) -> AnalysisJob | None: ...
    def update_job(self, analysis_id: str, expected_revision: int, changes: dict[str, Any]) -> AnalysisJob: ...
    def append_event(self, analysis_id: str, event_type: AnalysisEventType, data: dict[str, Any]) -> AnalysisEvent: ...
    def list_events(self, analysis_id: str, after: int = 0, limit: int = 200) -> list[AnalysisEvent]: ...
    def save_checkpoint(self, checkpoint: AnalysisCheckpoint) -> None: ...
    def get_latest_checkpoint(self, analysis_id: str) -> AnalysisCheckpoint | None: ...
    def acquire_lease(self, analysis_id: str, worker_id: str, lease_seconds: int) -> AnalysisJob | None: ...
    def heartbeat_lease(self, analysis_id: str, worker_id: str, lease_seconds: int) -> bool: ...
    def add_interaction(self, interaction: PendingInteraction) -> PendingInteraction: ...
    def get_interaction(self, interaction_id: str) -> PendingInteraction | None: ...
    def list_interactions(self, analysis_id: str, actor_id: str) -> list[PendingInteraction]: ...
    def answer_interaction(self, interaction_id: str, actor_id: str, expected_revision: int, idempotency_key: str, response: dict[str, Any]) -> InteractionResult: ...


class MongoAnalysisRepository:
    """Mongo source of truth for durable analysis state.

    Redis is deliberately absent from this class; it is only a delivery queue.
    """

    def __init__(self, database: Any) -> None:
        self.db = database
        self.jobs = database["analysis_jobs"]
        self.events = database["analysis_events"]
        self.checkpoints = database["analysis_checkpoints"]
        self.interactions = database["analysis_interactions"]
        self.receipts = database["analysis_command_receipts"]
        self.sessions = database["analysis_sessions"]
        self.transcript = database["analysis_transcript"]
        self.attachments = database["analysis_attachments"]
        self.artifacts = database["analysis_artifacts"]

    def ensure_indexes(self) -> None:
        from pymongo import ASCENDING, DESCENDING

        self.jobs.create_index([("analysis_id", ASCENDING)], unique=True)
        self.jobs.create_index(
            [("actor_id", ASCENDING), ("idempotency_key", ASCENDING)],
            unique=True,
            partialFilterExpression={"idempotency_key": {"$type": "string"}},
        )
        self.jobs.create_index([("status", ASCENDING), ("lease_expires_at", ASCENDING)])
        self.events.create_index([("analysis_id", ASCENDING), ("sequence", ASCENDING)], unique=True)
        self.events.create_index([("created_at", ASCENDING)], expireAfterSeconds=2_592_000)
        self.checkpoints.create_index([("analysis_id", ASCENDING), ("revision", DESCENDING)])
        self.interactions.create_index([("interaction_id", ASCENDING)], unique=True)
        self.interactions.create_index([("analysis_id", ASCENDING), ("status", ASCENDING)])
        self.receipts.create_index([("actor_id", ASCENDING), ("idempotency_key", ASCENDING)], unique=True)
        self.sessions.create_index([("session_id", ASCENDING)], unique=True)
        self.sessions.create_index([("actor_id", ASCENDING), ("updated_at", DESCENDING)])
        self.transcript.create_index([("session_id", ASCENDING), ("created_at", ASCENDING)])
        self.attachments.create_index([("attachment_id", ASCENDING)], unique=True)
        self.attachments.create_index([("session_id", ASCENDING), ("actor_id", ASCENDING)])
        self.artifacts.create_index([("artifact_id", ASCENDING)], unique=True)
        self.artifacts.create_index([("analysis_id", ASCENDING), ("actor_id", ASCENDING)])

    @staticmethod
    def _dump(model: Any) -> dict[str, Any]:
        return model.model_dump(mode="python")

    def create_job(self, job: AnalysisJob) -> tuple[AnalysisJob, bool]:
        if job.idempotency_key:
            existing = self.jobs.find_one(
                {"actor_id": job.actor_id, "idempotency_key": job.idempotency_key}
            )
            if existing:
                return AnalysisJob.model_validate(existing), False
        try:
            self.jobs.insert_one(self._dump(job))
        except Exception as exc:
            if job.idempotency_key:
                existing = self.jobs.find_one(
                    {"actor_id": job.actor_id, "idempotency_key": job.idempotency_key}
                )
                if existing:
                    return AnalysisJob.model_validate(existing), False
            raise exc
        self.ensure_session(
            SessionSummary(
                session_id=job.session_id,
                actor_id=job.actor_id,
                tenant_id=job.tenant_id,
                title=job.message[:80],
            )
        )
        return job, True

    def get_job(self, analysis_id: str, actor_id: str | None = None) -> AnalysisJob | None:
        query: dict[str, Any] = {"analysis_id": analysis_id}
        if actor_id is not None:
            query["actor_id"] = actor_id
        raw = self.jobs.find_one(query)
        return AnalysisJob.model_validate(raw) if raw else None

    def update_job(
        self, analysis_id: str, expected_revision: int, changes: dict[str, Any]
    ) -> AnalysisJob:
        from pymongo import ReturnDocument

        safe_changes = {**changes, "updated_at": utc_now()}
        raw = self.jobs.find_one_and_update(
            {"analysis_id": analysis_id, "revision": expected_revision},
            {"$set": safe_changes, "$inc": {"revision": 1}},
            return_document=ReturnDocument.AFTER,
        )
        if raw is None:
            if self.jobs.find_one({"analysis_id": analysis_id}) is None:
                raise RepositoryNotFound(analysis_id)
            raise RepositoryConflict("stale_revision")
        return AnalysisJob.model_validate(raw)

    def append_event(
        self, analysis_id: str, event_type: AnalysisEventType, data: dict[str, Any]
    ) -> AnalysisEvent:
        from pymongo import ReturnDocument

        job = self.jobs.find_one_and_update(
            {"analysis_id": analysis_id},
            {"$inc": {"event_cursor": 1}, "$set": {"updated_at": utc_now()}},
            return_document=ReturnDocument.AFTER,
        )
        if job is None:
            raise RepositoryNotFound(analysis_id)
        event = AnalysisEvent(
            analysis_id=analysis_id,
            sequence=int(job["event_cursor"]),
            event_type=event_type,
            data=sanitize_public_data(data),
        )
        self.events.insert_one(self._dump(event))
        return event

    def list_events(
        self, analysis_id: str, after: int = 0, limit: int = 200
    ) -> list[AnalysisEvent]:
        cursor = (
            self.events.find({"analysis_id": analysis_id, "sequence": {"$gt": after}})
            .sort("sequence", 1)
            .limit(max(1, min(limit, 1000)))
        )
        return [AnalysisEvent.model_validate(item) for item in cursor]

    def save_checkpoint(self, checkpoint: AnalysisCheckpoint) -> None:
        self.checkpoints.update_one(
            {
                "analysis_id": checkpoint.analysis_id,
                "revision": checkpoint.revision,
                "boundary": checkpoint.boundary,
            },
            {"$set": self._dump(checkpoint)},
            upsert=True,
        )

    def get_latest_checkpoint(self, analysis_id: str) -> AnalysisCheckpoint | None:
        raw = self.checkpoints.find_one(
            {"analysis_id": analysis_id}, sort=[("created_at", -1)]
        )
        return AnalysisCheckpoint.model_validate(raw) if raw else None

    def acquire_lease(
        self, analysis_id: str, worker_id: str, lease_seconds: int
    ) -> AnalysisJob | None:
        from pymongo import ReturnDocument

        now = utc_now()
        raw = self.jobs.find_one_and_update(
            {
                "analysis_id": analysis_id,
                "status": {
                    "$in": [
                        ExecutionStatus.QUEUED.value,
                        ExecutionStatus.RETRY_SCHEDULED.value,
                        ExecutionStatus.RUNNING.value,
                        ExecutionStatus.CANCEL_REQUESTED.value,
                    ]
                },
                "$or": [
                    {"lease_expires_at": None},
                    {"lease_expires_at": {"$lte": now}},
                    {"lease_owner": worker_id},
                ],
            },
            {
                "$set": {
                    "lease_owner": worker_id,
                    "lease_expires_at": now + timedelta(seconds=lease_seconds),
                    "updated_at": now,
                },
                "$inc": {"revision": 1, "attempt": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return AnalysisJob.model_validate(raw) if raw else None

    def heartbeat_lease(
        self, analysis_id: str, worker_id: str, lease_seconds: int
    ) -> bool:
        result = self.jobs.update_one(
            {"analysis_id": analysis_id, "lease_owner": worker_id},
            {
                "$set": {
                    "lease_expires_at": utc_now() + timedelta(seconds=lease_seconds),
                    "updated_at": utc_now(),
                }
            },
        )
        return bool(result.modified_count)

    def add_interaction(self, interaction: PendingInteraction) -> PendingInteraction:
        self.interactions.insert_one(self._dump(interaction))
        return interaction

    def get_interaction(self, interaction_id: str) -> PendingInteraction | None:
        raw = self.interactions.find_one({"interaction_id": interaction_id})
        return PendingInteraction.model_validate(raw) if raw else None

    def list_interactions(
        self, analysis_id: str, actor_id: str
    ) -> list[PendingInteraction]:
        return [
            PendingInteraction.model_validate(item)
            for item in self.interactions.find(
                {"analysis_id": analysis_id, "actor_id": actor_id}
            ).sort("created_at", 1)
        ]

    def answer_interaction(
        self,
        interaction_id: str,
        actor_id: str,
        expected_revision: int,
        idempotency_key: str,
        response: dict[str, Any],
    ) -> InteractionResult:
        from pymongo import ReturnDocument

        receipt = self.receipts.find_one(
            {"actor_id": actor_id, "idempotency_key": idempotency_key}
        )
        if receipt:
            interaction = self.get_interaction(str(receipt["interaction_id"]))
            if interaction is None:
                raise RepositoryNotFound(interaction_id)
            return InteractionResult(interaction=interaction, duplicate=True)
        raw = self.interactions.find_one_and_update(
            {
                "interaction_id": interaction_id,
                "actor_id": actor_id,
                "revision": expected_revision,
                "status": InteractionStatus.PENDING.value,
            },
            {
                "$set": {
                    "status": InteractionStatus.ANSWERED.value,
                    "response": sanitize_public_data(response),
                    "answered_at": utc_now(),
                },
                "$inc": {"revision": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        if raw is None:
            if self.interactions.find_one(
                {"interaction_id": interaction_id, "actor_id": actor_id}
            ) is None:
                raise RepositoryNotFound(interaction_id)
            raise RepositoryConflict("stale_or_already_answered")
        try:
            self.receipts.insert_one(
                {
                    "actor_id": actor_id,
                    "idempotency_key": idempotency_key,
                    "interaction_id": interaction_id,
                    "created_at": utc_now(),
                }
            )
        except Exception:
            pass
        return InteractionResult(
            interaction=PendingInteraction.model_validate(raw), duplicate=False
        )

    def ensure_session(self, session: SessionSummary) -> SessionSummary:
        now = utc_now()
        insert_doc = self._dump(session)
        # updated_at must not appear in both $setOnInsert and $set (Mongo code 40).
        insert_doc.pop("updated_at", None)
        self.sessions.update_one(
            {"session_id": session.session_id},
            {
                "$setOnInsert": insert_doc,
                "$set": {"updated_at": now},
            },
            upsert=True,
        )
        raw = self.sessions.find_one({"session_id": session.session_id})
        return SessionSummary.model_validate(raw)

    def list_sessions(self, actor_id: str, limit: int = 50) -> list[SessionSummary]:
        return [
            SessionSummary.model_validate(item)
            for item in self.sessions.find({"actor_id": actor_id})
            .sort("updated_at", -1)
            .limit(max(1, min(limit, 200)))
        ]

    def get_session(self, session_id: str, actor_id: str) -> SessionSummary | None:
        raw = self.sessions.find_one({"session_id": session_id, "actor_id": actor_id})
        return SessionSummary.model_validate(raw) if raw else None

    def update_session(
        self, session_id: str, actor_id: str, changes: dict[str, Any]
    ) -> SessionSummary | None:
        from pymongo import ReturnDocument

        allowed = {key: value for key, value in changes.items() if key in {"title", "archived"}}
        raw = self.sessions.find_one_and_update(
            {"session_id": session_id, "actor_id": actor_id},
            {"$set": {**allowed, "updated_at": utc_now()}},
            return_document=ReturnDocument.AFTER,
        )
        return SessionSummary.model_validate(raw) if raw else None

    def append_transcript(self, entry: TranscriptEntry) -> None:
        self.transcript.insert_one(self._dump(entry))
        self.sessions.update_one(
            {"session_id": entry.session_id}, {"$set": {"updated_at": utc_now()}}
        )

    def list_transcript(
        self, session_id: str, actor_id: str, limit: int = 500
    ) -> list[TranscriptEntry]:
        if self.get_session(session_id, actor_id) is None:
            return []
        return [
            TranscriptEntry.model_validate(item)
            for item in self.transcript.find({"session_id": session_id})
            .sort("created_at", 1)
            .limit(max(1, min(limit, 1000)))
        ]

    def add_attachment(self, metadata: AttachmentMetadata, internal: dict[str, Any]) -> None:
        self.attachments.insert_one({**self._dump(metadata), "_internal": internal})

    def list_attachments(
        self, session_id: str, actor_id: str
    ) -> list[AttachmentMetadata]:
        return [
            AttachmentMetadata.model_validate(item)
            for item in self.attachments.find(
                {"session_id": session_id, "actor_id": actor_id}
            ).sort("created_at", 1)
        ]

    def delete_attachment(self, attachment_id: str, actor_id: str) -> bool:
        return bool(
            self.attachments.delete_one(
                {"attachment_id": attachment_id, "actor_id": actor_id}
            ).deleted_count
        )

    def add_artifact(self, metadata: ArtifactMetadata) -> None:
        self.artifacts.update_one(
            {"artifact_id": metadata.artifact_id},
            {"$set": self._dump(metadata)},
            upsert=True,
        )

    def list_artifacts(
        self, analysis_id: str, actor_id: str
    ) -> list[ArtifactMetadata]:
        return [
            ArtifactMetadata.model_validate(item)
            for item in self.artifacts.find(
                {"analysis_id": analysis_id, "actor_id": actor_id}
            ).sort("created_at", 1)
        ]

    def review_artifact(
        self, artifact_id: str, analysis_id: str, actor_id: str, action: str
    ) -> ArtifactMetadata | None:
        from pymongo import ReturnDocument

        status = {
            "approve": "approved",
            "reject": "rejected",
            "request_revision": "revision_requested",
        }[action]
        raw = self.artifacts.find_one_and_update(
            {
                "artifact_id": artifact_id,
                "analysis_id": analysis_id,
                "actor_id": actor_id,
            },
            {"$set": {"review_status": status}},
            return_document=ReturnDocument.AFTER,
        )
        return ArtifactMetadata.model_validate(raw) if raw else None


class InMemoryAnalysisRepository:
    """Deterministic repository used by focused tests; semantics mirror Mongo CAS."""

    def __init__(self) -> None:
        self.jobs: dict[str, AnalysisJob] = {}
        self.events: dict[str, list[AnalysisEvent]] = {}
        self.checkpoints: list[AnalysisCheckpoint] = []
        self.interactions: dict[str, PendingInteraction] = {}
        self.receipts: dict[tuple[str, str], str] = {}
        self.sessions: dict[str, SessionSummary] = {}
        self.transcript: dict[str, list[TranscriptEntry]] = {}
        self.attachments: dict[str, AttachmentMetadata] = {}
        self.artifacts: dict[str, ArtifactMetadata] = {}
        self._lock = RLock()

    def ensure_indexes(self) -> None:
        return None

    def create_job(self, job: AnalysisJob) -> tuple[AnalysisJob, bool]:
        with self._lock:
            if job.idempotency_key:
                for existing in self.jobs.values():
                    if (
                        existing.actor_id == job.actor_id
                        and existing.idempotency_key == job.idempotency_key
                    ):
                        return existing.model_copy(deep=True), False
            self.jobs[job.analysis_id] = job.model_copy(deep=True)
            self.ensure_session(
                SessionSummary(
                    session_id=job.session_id,
                    actor_id=job.actor_id,
                    tenant_id=job.tenant_id,
                    title=job.message[:80],
                )
            )
            return job.model_copy(deep=True), True

    def get_job(self, analysis_id: str, actor_id: str | None = None) -> AnalysisJob | None:
        job = self.jobs.get(analysis_id)
        if job is None or (actor_id is not None and job.actor_id != actor_id):
            return None
        return job.model_copy(deep=True)

    def update_job(
        self, analysis_id: str, expected_revision: int, changes: dict[str, Any]
    ) -> AnalysisJob:
        with self._lock:
            job = self.jobs.get(analysis_id)
            if job is None:
                raise RepositoryNotFound(analysis_id)
            if job.revision != expected_revision:
                raise RepositoryConflict("stale_revision")
            updated = job.model_copy(
                update={**changes, "revision": job.revision + 1, "updated_at": utc_now()}
            )
            self.jobs[analysis_id] = AnalysisJob.model_validate(updated)
            return self.jobs[analysis_id].model_copy(deep=True)

    def append_event(
        self, analysis_id: str, event_type: AnalysisEventType, data: dict[str, Any]
    ) -> AnalysisEvent:
        with self._lock:
            job = self.jobs.get(analysis_id)
            if job is None:
                raise RepositoryNotFound(analysis_id)
            job.event_cursor += 1
            event = AnalysisEvent(
                analysis_id=analysis_id,
                sequence=job.event_cursor,
                event_type=event_type,
                data=sanitize_public_data(data),
            )
            self.events.setdefault(analysis_id, []).append(event)
            return event.model_copy(deep=True)

    def list_events(
        self, analysis_id: str, after: int = 0, limit: int = 200
    ) -> list[AnalysisEvent]:
        return [
            item.model_copy(deep=True)
            for item in self.events.get(analysis_id, [])
            if item.sequence > after
        ][:limit]

    def save_checkpoint(self, checkpoint: AnalysisCheckpoint) -> None:
        self.checkpoints.append(checkpoint.model_copy(deep=True))

    def get_latest_checkpoint(self, analysis_id: str) -> AnalysisCheckpoint | None:
        items = [x for x in self.checkpoints if x.analysis_id == analysis_id]
        return items[-1].model_copy(deep=True) if items else None

    def acquire_lease(
        self, analysis_id: str, worker_id: str, lease_seconds: int
    ) -> AnalysisJob | None:
        with self._lock:
            job = self.jobs.get(analysis_id)
            now = utc_now()
            if job is None or job.status not in {
                ExecutionStatus.QUEUED,
                ExecutionStatus.RETRY_SCHEDULED,
                ExecutionStatus.RUNNING,
                ExecutionStatus.CANCEL_REQUESTED,
            }:
                return None
            if (
                job.lease_expires_at is not None
                and job.lease_expires_at > now
                and job.lease_owner != worker_id
            ):
                return None
            job.lease_owner = worker_id
            job.lease_expires_at = now + timedelta(seconds=lease_seconds)
            job.attempt += 1
            job.revision += 1
            return job.model_copy(deep=True)

    def heartbeat_lease(
        self, analysis_id: str, worker_id: str, lease_seconds: int
    ) -> bool:
        job = self.jobs.get(analysis_id)
        if job is None or job.lease_owner != worker_id:
            return False
        job.lease_expires_at = utc_now() + timedelta(seconds=lease_seconds)
        return True

    def add_interaction(self, interaction: PendingInteraction) -> PendingInteraction:
        self.interactions[interaction.interaction_id] = interaction.model_copy(deep=True)
        return interaction.model_copy(deep=True)

    def get_interaction(self, interaction_id: str) -> PendingInteraction | None:
        item = self.interactions.get(interaction_id)
        return item.model_copy(deep=True) if item else None

    def list_interactions(
        self, analysis_id: str, actor_id: str
    ) -> list[PendingInteraction]:
        return [
            item.model_copy(deep=True)
            for item in self.interactions.values()
            if item.analysis_id == analysis_id and item.actor_id == actor_id
        ]

    def answer_interaction(
        self,
        interaction_id: str,
        actor_id: str,
        expected_revision: int,
        idempotency_key: str,
        response: dict[str, Any],
    ) -> InteractionResult:
        with self._lock:
            receipt_key = (actor_id, idempotency_key)
            if receipt_key in self.receipts:
                existing = self.interactions[self.receipts[receipt_key]]
                return InteractionResult(
                    interaction=existing.model_copy(deep=True), duplicate=True
                )
            item = self.interactions.get(interaction_id)
            if item is None or item.actor_id != actor_id:
                raise RepositoryNotFound(interaction_id)
            if (
                item.revision != expected_revision
                or item.status != InteractionStatus.PENDING
            ):
                raise RepositoryConflict("stale_or_already_answered")
            item.status = InteractionStatus.ANSWERED
            item.response = sanitize_public_data(response)
            item.answered_at = utc_now()
            item.revision += 1
            self.receipts[receipt_key] = interaction_id
            return InteractionResult(
                interaction=item.model_copy(deep=True), duplicate=False
            )

    def ensure_session(self, session: SessionSummary) -> SessionSummary:
        existing = self.sessions.get(session.session_id)
        if existing is None:
            self.sessions[session.session_id] = session.model_copy(deep=True)
        else:
            existing.updated_at = utc_now()
        return self.sessions[session.session_id].model_copy(deep=True)

    def list_sessions(self, actor_id: str, limit: int = 50) -> list[SessionSummary]:
        items = [s for s in self.sessions.values() if s.actor_id == actor_id]
        return [s.model_copy(deep=True) for s in sorted(items, key=lambda x: x.updated_at, reverse=True)[:limit]]

    def get_session(self, session_id: str, actor_id: str) -> SessionSummary | None:
        item = self.sessions.get(session_id)
        if item is None or item.actor_id != actor_id:
            return None
        return item.model_copy(deep=True)

    def update_session(
        self, session_id: str, actor_id: str, changes: dict[str, Any]
    ) -> SessionSummary | None:
        item = self.sessions.get(session_id)
        if item is None or item.actor_id != actor_id:
            return None
        if "title" in changes:
            item.title = str(changes["title"])
        if "archived" in changes:
            item.archived = bool(changes["archived"])
        item.updated_at = utc_now()
        return item.model_copy(deep=True)

    def append_transcript(self, entry: TranscriptEntry) -> None:
        self.transcript.setdefault(entry.session_id, []).append(entry.model_copy(deep=True))

    def list_transcript(
        self, session_id: str, actor_id: str, limit: int = 500
    ) -> list[TranscriptEntry]:
        if self.get_session(session_id, actor_id) is None:
            return []
        return [x.model_copy(deep=True) for x in self.transcript.get(session_id, [])[:limit]]

    def add_attachment(self, metadata: AttachmentMetadata, internal: dict[str, Any]) -> None:
        self.attachments[metadata.attachment_id] = metadata.model_copy(deep=True)

    def list_attachments(
        self, session_id: str, actor_id: str
    ) -> list[AttachmentMetadata]:
        return [
            item.model_copy(deep=True)
            for item in self.attachments.values()
            if item.session_id == session_id and item.actor_id == actor_id
        ]

    def delete_attachment(self, attachment_id: str, actor_id: str) -> bool:
        item = self.attachments.get(attachment_id)
        if item is None or item.actor_id != actor_id:
            return False
        del self.attachments[attachment_id]
        return True

    def add_artifact(self, metadata: ArtifactMetadata) -> None:
        self.artifacts[metadata.artifact_id] = metadata.model_copy(deep=True)

    def list_artifacts(
        self, analysis_id: str, actor_id: str
    ) -> list[ArtifactMetadata]:
        return [
            item.model_copy(deep=True)
            for item in self.artifacts.values()
            if item.analysis_id == analysis_id and item.actor_id == actor_id
        ]

    def review_artifact(
        self, artifact_id: str, analysis_id: str, actor_id: str, action: str
    ) -> ArtifactMetadata | None:
        item = self.artifacts.get(artifact_id)
        if (
            item is None
            or item.analysis_id != analysis_id
            or item.actor_id != actor_id
        ):
            return None
        item.review_status = {
            "approve": "approved",
            "reject": "rejected",
            "request_revision": "revision_requested",
        }[action]  # type: ignore[assignment]
        return item.model_copy(deep=True)

