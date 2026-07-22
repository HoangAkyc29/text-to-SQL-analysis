from __future__ import annotations

import logging
import os
from pathlib import PurePosixPath
from threading import Event, Thread
from typing import Any
from uuid import uuid4

import redis

from project_core.domain.contracts.clarification import ClarificationReply
from project_core.domain.contracts.interactive import (
    AnalysisCheckpoint,
    AnalysisEventType,
    AnalysisJob,
    ArtifactMetadata,
    ExecutionStatus,
    InteractionCommand,
    InteractionKind,
    InteractionResult,
    PendingInteraction,
    SafeError,
    TranscriptEntry,
    utc_now,
)
from project_core.infra.analysis_queue import QueueMessage, RedisAnalysisQueue
from project_core.infra.analysis_repository import (
    AnalysisRepository,
    MongoAnalysisRepository,
    RepositoryConflict,
    RepositoryNotFound,
)
from project_core.infra.live_trial_recorder import LiveTrialRecorder

logger = logging.getLogger(__name__)


def _public_artifact_ref(raw_url: str, trace_id: str | None) -> tuple[str, str | None]:
    """Map a filesystem artifact path to a gateway download URL."""
    path = PurePosixPath(str(raw_url).replace("\\", "/"))
    name = path.name or "artifact"
    resolved_trace = trace_id
    parts = path.parts
    if "artifacts" in parts:
        idx = parts.index("artifacts")
        if idx + 1 < len(parts):
            candidate = parts[idx + 1]
            if candidate and candidate not in {"out", "in"}:
                resolved_trace = candidate
    if resolved_trace and name:
        return name, f"/artifacts/{resolved_trace}/{name}"
    return name, None


class AnalysisService:
    def __init__(
        self,
        repository: AnalysisRepository,
        queue: Any,
        recorder: LiveTrialRecorder | None = None,
    ) -> None:
        self.repository = repository
        self.queue = queue
        self.recorder = recorder or LiveTrialRecorder()

    def _mirror(
        self,
        analysis_id: str,
        event_type: AnalysisEventType | str,
        data: dict[str, Any] | None = None,
        *,
        source: str = "system",
    ) -> None:
        name = event_type.value if isinstance(event_type, AnalysisEventType) else str(event_type)
        try:
            self.recorder.append(analysis_id, name, data or {}, source=source)
        except Exception:
            logger.exception("live-trial file log failed for %s", analysis_id)

    def submit(
        self,
        *,
        session_id: str,
        message: str,
        user: dict[str, Any],
        idempotency_key: str | None = None,
        parent_analysis_id: str | None = None,
    ) -> tuple[AnalysisJob, bool]:
        job = AnalysisJob(
            session_id=session_id,
            actor_id=str(user["sub"]),
            actor_role=str(user.get("role") or ""),
            tenant_id=str(user.get("tenant_id") or ""),
            store_ids=user.get("store_ids"),
            message=message,
            idempotency_key=idempotency_key,
            parent_analysis_id=parent_analysis_id,
        )
        job, created = self.repository.create_job(job)
        if not created:
            return job, False
        self.repository.append_transcript(
            TranscriptEntry(
                session_id=session_id,
                role="user",
                content=message,
                analysis_id=job.analysis_id,
            )
        )
        self.repository.save_checkpoint(
            AnalysisCheckpoint(
                analysis_id=job.analysis_id,
                boundary="accepted",
                revision=job.revision,
                context={"session_id": session_id},
            )
        )
        payload = {
            "status": ExecutionStatus.QUEUED.value,
            "session_id": session_id,
            "message_preview": message[:240],
        }
        self.repository.append_event(
            job.analysis_id,
            AnalysisEventType.QUEUED,
            payload,
        )
        self._mirror(job.analysis_id, AnalysisEventType.QUEUED, payload, source="api")
        self.queue.enqueue(job.analysis_id, command="run")
        return self.repository.get_job(job.analysis_id) or job, True

    def get_job(self, analysis_id: str, actor_id: str) -> AnalysisJob | None:
        return self.repository.get_job(analysis_id, actor_id)

    def cancel(self, analysis_id: str, actor_id: str) -> AnalysisJob:
        job = self.repository.get_job(analysis_id, actor_id)
        if job is None:
            raise RepositoryNotFound(analysis_id)
        if job.status in {
            ExecutionStatus.SUCCEEDED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.EXPIRED,
        }:
            return job
        updated = self.repository.update_job(
            analysis_id,
            job.revision,
            {"status": ExecutionStatus.CANCEL_REQUESTED},
        )
        payload = {"status": ExecutionStatus.CANCEL_REQUESTED.value}
        self.repository.append_event(
            analysis_id,
            AnalysisEventType.CANCEL_REQUESTED,
            payload,
        )
        self._mirror(analysis_id, AnalysisEventType.CANCEL_REQUESTED, payload, source="api")
        return updated

    def answer_interaction(
        self, analysis_id: str, actor_id: str, command: InteractionCommand
    ) -> InteractionResult:
        job = self.repository.get_job(analysis_id, actor_id)
        if job is None:
            raise RepositoryNotFound(analysis_id)
        interaction = self.repository.get_interaction(command.interaction_id)
        if interaction is None or interaction.analysis_id != analysis_id:
            raise RepositoryNotFound(command.interaction_id)
        result = self.repository.answer_interaction(
            command.interaction_id,
            actor_id,
            command.expected_revision,
            command.idempotency_key,
            command.response,
        )
        if not result.duplicate:
            payload = {
                "interaction_id": command.interaction_id,
                "kind": interaction.kind.value,
                "response_keys": sorted(command.response.keys()),
            }
            self.repository.append_event(
                analysis_id,
                AnalysisEventType.INTERACTION_ANSWERED,
                payload,
            )
            self._mirror(
                analysis_id,
                AnalysisEventType.INTERACTION_ANSWERED,
                {**payload, "response": command.response},
                source="user",
            )
            current = self.repository.get_job(analysis_id, actor_id)
            if current is not None:
                self.repository.update_job(
                    analysis_id,
                    current.revision,
                    {
                        "status": ExecutionStatus.QUEUED,
                        "pending_interaction_id": None,
                    },
                )
            self.queue.enqueue(
                analysis_id,
                command="interaction",
                payload={"interaction_id": command.interaction_id},
            )
        return result

    def rephrase(
        self,
        analysis_id: str,
        actor_id: str,
        message: str,
        user: dict[str, Any],
        idempotency_key: str | None,
    ) -> tuple[AnalysisJob, bool]:
        parent = self.repository.get_job(analysis_id, actor_id)
        if parent is None:
            raise RepositoryNotFound(analysis_id)
        return self.submit(
            session_id=parent.session_id,
            message=message,
            user=user,
            idempotency_key=idempotency_key,
            parent_analysis_id=analysis_id,
        )


class AnalysisWorker:
    """Executes one durable command around the existing, unchanged pipeline."""

    def __init__(
        self,
        repository: AnalysisRepository,
        queue: Any,
        orchestrator: Any,
        *,
        worker_id: str | None = None,
        lease_seconds: int = 120,
        recorder: LiveTrialRecorder | None = None,
    ) -> None:
        self.repository = repository
        self.queue = queue
        self.orchestrator = orchestrator
        self.worker_id = worker_id or f"worker-{uuid4()}"
        self.lease_seconds = lease_seconds
        self.recorder = recorder or LiveTrialRecorder()

    def _mirror(
        self,
        analysis_id: str,
        event_type: AnalysisEventType | str,
        data: dict[str, Any] | None = None,
        *,
        source: str = "worker",
    ) -> None:
        name = event_type.value if isinstance(event_type, AnalysisEventType) else str(event_type)
        try:
            self.recorder.append(analysis_id, name, data or {}, source=source)
        except Exception:
            logger.exception("live-trial file log failed for %s", analysis_id)

    def _install_progress_sink(self, analysis_id: str) -> list[Any]:
        last_stage = {"value": None}

        def sink(workflow: Any) -> None:
            stage = getattr(workflow, "progress_step", None)
            if not stage or stage == last_stage["value"]:
                return
            last_stage["value"] = stage
            steps = getattr(workflow, "steps", None) or []
            latest = steps[-1] if steps else None
            summary = ""
            if latest is not None:
                summary = str(getattr(latest, "summary", "") or "")[:400]
            status = getattr(workflow, "status", None)
            if hasattr(status, "value"):
                status = status.value
            payload = {
                "stage": stage,
                "status": status,
                "sql_attempt": getattr(workflow, "sql_attempt", None),
                "clarify_round": getattr(workflow, "clarify_round", None),
                "summary": summary,
                "step_count": len(steps),
            }
            self.repository.append_event(analysis_id, AnalysisEventType.PROGRESS, payload)
            self._mirror(analysis_id, AnalysisEventType.PROGRESS, payload)

        previous = list(getattr(self.orchestrator, "progress_sinks", []) or [])
        self.orchestrator.progress_sinks = [*previous, sink]
        return previous

    def process(self, message: QueueMessage) -> None:
        job = self.repository.acquire_lease(
            message.analysis_id, self.worker_id, self.lease_seconds
        )
        if job is None:
            self.queue.ack(message.message_id)
            return
        self._restore_legacy_cache(job)
        if job.status == ExecutionStatus.CANCEL_REQUESTED:
            self._finish_cancelled(job)
            self.queue.ack(message.message_id)
            return
        previous_sinks = self._install_progress_sink(job.analysis_id)
        try:
            job = self.repository.update_job(
                job.analysis_id,
                job.revision,
                {
                    "status": ExecutionStatus.RUNNING,
                    "current_stage": "pipeline",
                    "progress": 0.05,
                    "started_at": job.started_at or utc_now(),
                },
            )
            started = {
                "status": "running",
                "attempt": job.attempt,
                "command": message.command,
            }
            self.repository.append_event(
                job.analysis_id,
                AnalysisEventType.STARTED,
                started,
            )
            self._mirror(job.analysis_id, AnalysisEventType.STARTED, started)
            self.repository.save_checkpoint(
                AnalysisCheckpoint(
                    analysis_id=job.analysis_id,
                    boundary="ingress",
                    revision=job.revision,
                    context={"command": message.command},
                )
            )
            user = {
                "sub": job.actor_id,
                "role": job.actor_role,
                "tenant_id": job.tenant_id,
                "store_ids": job.store_ids,
            }
            response = self._execute_with_heartbeat(job, message, user)
            current = self.repository.get_job(job.analysis_id)
            if current is None:
                raise RepositoryNotFound(job.analysis_id)
            if current.status == ExecutionStatus.CANCEL_REQUESTED:
                self._finish_cancelled(current)
            elif response.clarification is not None:
                self._pause_for_clarification(current, response)
            elif response.error:
                self._finish_failed(current, response)
            else:
                self._finish_succeeded(current, response)
            self.queue.ack(message.message_id)
        except Exception:
            logger.exception("analysis worker failed for %s", message.analysis_id)
            current = self.repository.get_job(message.analysis_id)
            if current is not None and current.attempt < current.max_attempts:
                current = self.repository.update_job(
                    current.analysis_id,
                    current.revision,
                    {
                        "status": ExecutionStatus.RETRY_SCHEDULED,
                        "safe_error": SafeError(
                            code="WORKER_ERROR",
                            message="Analysis temporarily unavailable.",
                            retryable=True,
                        ).model_dump(mode="json"),
                    },
                )
                retry_payload = {"attempt": current.attempt + 1}
                self.repository.append_event(
                    current.analysis_id,
                    AnalysisEventType.RETRY_SCHEDULED,
                    retry_payload,
                )
                self._mirror(
                    current.analysis_id,
                    AnalysisEventType.RETRY_SCHEDULED,
                    retry_payload,
                )
                self.queue.enqueue(current.analysis_id, command=message.command, payload=message.payload)
                self.queue.ack(message.message_id)
            else:
                if current is not None:
                    self._finish_failed(current, None)
                self.queue.dead_letter(message, "worker_error")
        finally:
            self.orchestrator.progress_sinks = previous_sinks

    def _execute_with_heartbeat(
        self, job: AnalysisJob, message: QueueMessage, user: dict[str, Any]
    ) -> Any:
        stop = Event()

        def heartbeat() -> None:
            interval = max(1.0, self.lease_seconds / 3)
            while not stop.wait(interval):
                current = self.repository.get_job(job.analysis_id)
                if (
                    current is not None
                    and current.status == ExecutionStatus.CANCEL_REQUESTED
                    and hasattr(self.orchestrator, "request_cancel")
                ):
                    self.orchestrator.request_cancel(job.session_id)
                if not self.repository.heartbeat_lease(
                    job.analysis_id, self.worker_id, self.lease_seconds
                ):
                    logger.warning("lease lost for %s", job.analysis_id)
                    return
                self._persist_pipeline_checkpoint(job.analysis_id)

        thread = Thread(target=heartbeat, daemon=True)
        thread.start()
        try:
            if message.command == "interaction":
                return self._resume_interaction(job, message.payload, user)
            return self.orchestrator.handle_chat(
                session_id=job.session_id,
                message=job.message,
                user=user,
            )
        finally:
            self._persist_pipeline_checkpoint(job.analysis_id)
            stop.set()
            thread.join(timeout=1.0)

    def _persist_pipeline_checkpoint(self, analysis_id: str) -> None:
        stm = getattr(self.orchestrator, "stm", None)
        job = self.repository.get_job(analysis_id)
        if stm is None or job is None:
            return
        try:
            bundle = stm.load_session(job.session_id)
            context: dict[str, Any] = {
                "transcript": [
                    item.model_dump(mode="json") for item in bundle.transcript
                ],
                "clarification": bundle.clarification,
            }
            if bundle.workflow is not None:
                context["workflow"] = bundle.workflow.model_dump(mode="json")
            self.repository.save_checkpoint(
                AnalysisCheckpoint(
                    analysis_id=analysis_id,
                    boundary="pipeline",
                    revision=job.revision,
                    context=context,
                )
            )
        except Exception:
            logger.warning("could not persist pipeline checkpoint for %s", analysis_id)

    def _restore_legacy_cache(self, job: AnalysisJob) -> None:
        stm = getattr(self.orchestrator, "stm", None)
        if stm is None:
            return
        checkpoint = self.repository.get_latest_checkpoint(job.analysis_id)
        if checkpoint is None or "workflow" not in checkpoint.context:
            return
        try:
            from project_core.domain.contracts.workflow import WorkflowState
            from project_core.domain.memory.session_bundle import TranscriptTurn

            workflow = WorkflowState.model_validate(checkpoint.context["workflow"])
            stm.save_workflow(job.session_id, workflow)
            transcript = [
                TranscriptTurn.model_validate(item)
                for item in checkpoint.context.get("transcript", [])
            ]
            stm.save_transcript(job.session_id, transcript)
            stm.save_clarification(
                job.session_id, checkpoint.context.get("clarification")
            )
        except Exception:
            logger.warning("could not restore pipeline checkpoint for %s", job.analysis_id)

    def _resume_interaction(
        self, job: AnalysisJob, payload: dict[str, Any], user: dict[str, Any]
    ) -> Any:
        interaction = self.repository.get_interaction(str(payload["interaction_id"]))
        if (
            interaction is None
            or interaction.response is None
            or interaction.kind != InteractionKind.CLARIFICATION
        ):
            raise RepositoryConflict("interaction_not_resumable")
        legacy_id = str(interaction.payload.get("legacy_analysis_id") or job.legacy_analysis_id)
        reply = ClarificationReply.model_validate(
            {"analysis_id": legacy_id, **interaction.response}
        )
        return self.orchestrator.handle_clarify(
            session_id=job.session_id, reply=reply, user=user
        )

    def _pause_for_clarification(self, job: AnalysisJob, response: Any) -> None:
        request = response.clarification.model_dump(mode="json")
        interaction = self.repository.add_interaction(
            PendingInteraction(
                analysis_id=job.analysis_id,
                actor_id=job.actor_id,
                kind=InteractionKind.CLARIFICATION,
                prompt=response.message,
                payload={
                    "request": request,
                    "legacy_analysis_id": response.analysis_id,
                },
            )
        )
        updated = self.repository.update_job(
            job.analysis_id,
            job.revision,
            {
                "status": ExecutionStatus.AWAITING_INTERACTION,
                "outcome": response.outcome,
                "legacy_analysis_id": response.analysis_id,
                "pending_interaction_id": interaction.interaction_id,
                "current_stage": "clarification",
                "progress": max(job.progress, 0.1),
                "lease_owner": None,
                "lease_expires_at": None,
            },
        )
        latest_checkpoint = self.repository.get_latest_checkpoint(job.analysis_id)
        self.repository.save_checkpoint(
            AnalysisCheckpoint(
                analysis_id=job.analysis_id,
                boundary="interaction",
                revision=updated.revision,
                context={
                    **(latest_checkpoint.context if latest_checkpoint else {}),
                    "interaction_id": interaction.interaction_id,
                },
            )
        )
        self.repository.append_event(
            job.analysis_id,
            AnalysisEventType.INTERACTION_REQUESTED,
            {
                "interaction_id": interaction.interaction_id,
                "kind": interaction.kind.value,
                "revision": interaction.revision,
                "prompt": interaction.prompt,
                "request": request,
            },
        )
        self._mirror(
            job.analysis_id,
            AnalysisEventType.INTERACTION_REQUESTED,
            {
                "interaction_id": interaction.interaction_id,
                "kind": interaction.kind.value,
                "revision": interaction.revision,
                "prompt": interaction.prompt,
                "request": request,
            },
        )

    def _finish_succeeded(self, job: AnalysisJob, response: Any) -> None:
        updated = self.repository.update_job(
            job.analysis_id,
            job.revision,
            {
                "status": ExecutionStatus.SUCCEEDED,
                "outcome": response.outcome or "success",
                "legacy_analysis_id": response.analysis_id,
                "trace_id": getattr(response, "trace_id", None),
                "result_message": response.message,
                "progress": 1.0,
                "current_stage": "completed",
                "completed_at": utc_now(),
                "lease_owner": None,
                "lease_expires_at": None,
            },
        )
        self.repository.append_transcript(
            TranscriptEntry(
                session_id=job.session_id,
                role="assistant",
                content=response.message,
                analysis_id=job.analysis_id,
            )
        )
        trace_id = getattr(response, "trace_id", None)
        for raw in response.artifacts or []:
            url = str(raw.get("url") or raw.get("download_url") or "")
            name, download_url = _public_artifact_ref(url, trace_id)
            if not download_url and raw.get("download_url"):
                download_url = str(raw.get("download_url"))
            artifact = ArtifactMetadata(
                analysis_id=job.analysis_id,
                actor_id=job.actor_id,
                name=name,
                download_url=download_url,
            )
            self.repository.add_artifact(artifact)
            public = artifact.model_dump(mode="json")
            public["url"] = download_url
            self.repository.append_event(
                job.analysis_id,
                AnalysisEventType.ARTIFACT_CREATED,
                public,
            )
            self._mirror(
                job.analysis_id,
                AnalysisEventType.ARTIFACT_CREATED,
                public,
            )
        self.repository.save_checkpoint(
            AnalysisCheckpoint(
                analysis_id=job.analysis_id,
                boundary="terminal",
                revision=updated.revision,
                context={"outcome": updated.outcome},
            )
        )
        completed = {
            "status": ExecutionStatus.SUCCEEDED.value,
            "outcome": updated.outcome,
            "message": response.message,
            "legacy_analysis_id": response.analysis_id,
            "trace_id": trace_id,
        }
        self.repository.append_event(
            job.analysis_id,
            AnalysisEventType.COMPLETED,
            completed,
        )
        self._mirror(job.analysis_id, AnalysisEventType.COMPLETED, completed)

    def _finish_failed(self, job: AnalysisJob, response: Any | None) -> None:
        error = SafeError(
            code=(response.error or {}).get("code", "ANALYSIS_FAILED")
            if response is not None
            else "ANALYSIS_FAILED",
            message="Analysis could not be completed.",
            retryable=False,
        )
        updated = self.repository.update_job(
            job.analysis_id,
            job.revision,
            {
                "status": ExecutionStatus.FAILED,
                "outcome": getattr(response, "outcome", None) or "error",
                "safe_error": error.model_dump(mode="json"),
                "completed_at": utc_now(),
                "lease_owner": None,
                "lease_expires_at": None,
            },
        )
        self.repository.save_checkpoint(
            AnalysisCheckpoint(
                analysis_id=job.analysis_id,
                boundary="terminal",
                revision=updated.revision,
                context={"outcome": "error"},
            )
        )
        self.repository.append_event(
            job.analysis_id,
            AnalysisEventType.FAILED,
            {"status": "failed", "error": error.model_dump()},
        )
        self._mirror(
            job.analysis_id,
            AnalysisEventType.FAILED,
            {"status": "failed", "error": error.model_dump()},
        )

    def _finish_cancelled(self, job: AnalysisJob) -> None:
        updated = self.repository.update_job(
            job.analysis_id,
            job.revision,
            {
                "status": ExecutionStatus.CANCELLED,
                "outcome": "cancelled",
                "completed_at": utc_now(),
                "lease_owner": None,
                "lease_expires_at": None,
            },
        )
        self.repository.save_checkpoint(
            AnalysisCheckpoint(
                analysis_id=job.analysis_id,
                boundary="terminal",
                revision=updated.revision,
                context={"outcome": "cancelled"},
            )
        )
        self.repository.append_event(
            job.analysis_id,
            AnalysisEventType.CANCELLED,
            {"status": ExecutionStatus.CANCELLED.value},
        )
        self._mirror(
            job.analysis_id,
            AnalysisEventType.CANCELLED,
            {"status": ExecutionStatus.CANCELLED.value},
        )


def create_analysis_service() -> AnalysisService:
    from pymongo import MongoClient

    client = MongoClient(
        os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent"),
        serverSelectionTimeoutMS=int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "2000")),
    )
    client.admin.command("ping")
    repository = MongoAnalysisRepository(client.get_default_database())
    repository.ensure_indexes()
    # Socket timeout must exceed XREADGROUP block time or the worker crashes
    # on idle polls. Disable socket timeout and rely on the command block.
    redis_client = redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:18379/0"),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=None,
        health_check_interval=30,
    )
    queue = RedisAnalysisQueue(redis_client)
    queue.ensure_group()
    recorder = LiveTrialRecorder()
    return AnalysisService(repository, queue, recorder=recorder)

