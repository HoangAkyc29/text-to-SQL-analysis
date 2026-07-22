from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from chat_gateway.analysis_service import AnalysisService, AnalysisWorker
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import (
    ClarificationOption,
    ClarificationQuestion,
    ClarificationRequest,
)
from project_core.domain.contracts.interactive import (
    AnalysisEventType,
    AnalysisJob,
    ExecutionStatus,
    InteractionCommand,
)
from project_core.domain.contracts.pipeline import ChatResponse
from project_core.infra.analysis_queue import QueueMessage
from project_core.infra.analysis_repository import (
    InMemoryAnalysisRepository,
    RepositoryConflict,
)

pytestmark = pytest.mark.unit


class FakeQueue:
    def __init__(self) -> None:
        self.enqueued: list[tuple[str, str, dict[str, Any]]] = []
        self.acked: list[str] = []
        self.dead: list[str] = []

    def enqueue(
        self,
        analysis_id: str,
        *,
        command: str = "run",
        payload: dict[str, Any] | None = None,
    ) -> str:
        self.enqueued.append((analysis_id, command, payload or {}))
        return f"{len(self.enqueued)}-0"

    def ack(self, message_id: str) -> None:
        self.acked.append(message_id)

    def dead_letter(self, message: QueueMessage, reason: str) -> None:
        self.dead.append(f"{message.message_id}:{reason}")


def user(actor_id: str = "u1") -> dict[str, Any]:
    return {
        "sub": actor_id,
        "role": "hq_analyst",
        "store_ids": None,
        "tenant_id": "tenant-1",
    }


def test_repository_cas_event_order_and_public_sanitization() -> None:
    repo = InMemoryAnalysisRepository()
    job, created = repo.create_job(
        AnalysisJob(session_id="s1", actor_id="u1", message="question")
    )
    assert created
    updated = repo.update_job(job.analysis_id, job.revision, {"progress": 0.25})
    with pytest.raises(RepositoryConflict):
        repo.update_job(job.analysis_id, job.revision, {"progress": 0.5})

    first = repo.append_event(
        job.analysis_id,
        AnalysisEventType.PROGRESS,
        {
            "stage": "planning",
            "sql": "private",
            "system_prompt": "private",
            "nested": {"token": "private", "safe": True},
        },
    )
    second = repo.append_event(
        job.analysis_id, AnalysisEventType.STAGE_COMPLETED, {"stage": "planning"}
    )
    assert updated.revision == 2
    assert [first.sequence, second.sequence] == [1, 2]
    assert first.data == {"stage": "planning", "nested": {"safe": True}}


def test_submission_idempotency_ownership_and_durable_cancel() -> None:
    repo = InMemoryAnalysisRepository()
    queue = FakeQueue()
    service = AnalysisService(repo, queue)

    first, created = service.submit(
        session_id="s1", message="analyze", user=user(), idempotency_key="same"
    )
    duplicate, duplicate_created = service.submit(
        session_id="s1", message="ignored", user=user(), idempotency_key="same"
    )
    assert created is True
    assert duplicate_created is False
    assert duplicate.analysis_id == first.analysis_id
    assert len(queue.enqueued) == 1
    assert service.get_job(first.analysis_id, "other") is None

    cancelled = service.cancel(first.analysis_id, "u1")
    assert cancelled.status == ExecutionStatus.CANCEL_REQUESTED
    assert repo.list_events(first.analysis_id)[-1].event_type == AnalysisEventType.CANCEL_REQUESTED
    worker = AnalysisWorker(
        repo, queue, ClarifyingOrchestrator(), worker_id="cancel-worker"
    )
    worker.process(
        QueueMessage(
            message_id="cancel-1",
            analysis_id=first.analysis_id,
            command="run",
            payload={},
        )
    )
    assert repo.get_job(first.analysis_id).status == ExecutionStatus.CANCELLED  # type: ignore[union-attr]


class ClarifyingOrchestrator:
    def __init__(self) -> None:
        self.resumed = False

    def handle_chat(self, **_: Any) -> ChatResponse:
        request = ClarificationRequest(
            reason="Choose scope",
            partial_brief=AnalysisBrief(intent="analysis"),
            questions=[
                ClarificationQuestion(
                    id="scope",
                    prompt="Which scope?",
                    options=[ClarificationOption(id="all", label="All")],
                    maps_to_brief_field="scope",
                )
            ],
        )
        return ChatResponse(
            session_id="s1",
            analysis_id="legacy-1",
            workflow_status="awaiting_clarification",
            outcome="needs_clarification",
            message="Which scope?",
            clarification=request,
        )

    def handle_clarify(self, **_: Any) -> ChatResponse:
        self.resumed = True
        return ChatResponse(
            session_id="s1",
            analysis_id="legacy-1",
            workflow_status="idle",
            outcome="success",
            message="Done",
        )


def test_worker_clarification_is_generic_idempotent_interaction() -> None:
    repo = InMemoryAnalysisRepository()
    queue = FakeQueue()
    service = AnalysisService(repo, queue)
    job, _ = service.submit(session_id="s1", message="analyze", user=user())
    orchestrator = ClarifyingOrchestrator()
    worker = AnalysisWorker(repo, queue, orchestrator, worker_id="worker-1")

    worker.process(
        QueueMessage(
            message_id="1-0", analysis_id=job.analysis_id, command="run", payload={}
        )
    )
    paused = repo.get_job(job.analysis_id)
    assert paused is not None
    assert paused.status == ExecutionStatus.AWAITING_INTERACTION
    interaction = repo.list_interactions(job.analysis_id, "u1")[0]

    command = InteractionCommand(
        interaction_id=interaction.interaction_id,
        expected_revision=interaction.revision,
        idempotency_key="answer-1",
        response={
            "answers": [
                {"question_id": "scope", "selected_option_id": "all"}
            ]
        },
    )
    answered = service.answer_interaction(job.analysis_id, "u1", command)
    duplicate = service.answer_interaction(job.analysis_id, "u1", command)
    assert answered.duplicate is False
    assert duplicate.duplicate is True

    worker.process(
        QueueMessage(
            message_id="2-0",
            analysis_id=job.analysis_id,
            command="interaction",
            payload={"interaction_id": interaction.interaction_id},
        )
    )
    completed = repo.get_job(job.analysis_id)
    assert completed is not None
    assert completed.status == ExecutionStatus.SUCCEEDED
    assert completed.result_message == "Done"
    assert orchestrator.resumed is True


def test_async_api_status_sessions_and_sse(monkeypatch) -> None:
    import chat_gateway.app as gateway_app

    repo = InMemoryAnalysisRepository()
    queue = FakeQueue()
    service = AnalysisService(repo, queue)
    monkeypatch.setattr(gateway_app, "_analysis_service", service)
    client = TestClient(gateway_app.app)

    submitted = client.post(
        "/analyses",
        headers={"Idempotency-Key": "api-1"},
        json={"session_id": "api-session", "message": "analyze"},
    )
    assert submitted.status_code == 202
    analysis_id = submitted.json()["analysis_id"]
    job = repo.get_job(analysis_id)
    assert job is not None
    repo.update_job(
        analysis_id,
        job.revision,
        {
            "status": ExecutionStatus.SUCCEEDED,
            "outcome": "success",
            "result_message": "Safe result",
        },
    )
    repo.append_event(
        analysis_id, AnalysisEventType.COMPLETED, {"message": "Safe result"}
    )

    status = client.get(f"/analyses/{analysis_id}")
    assert status.status_code == 200
    assert status.json()["status"] == "succeeded"
    assert "lease_owner" not in status.json()

    events = client.get(f"/analyses/{analysis_id}/events")
    assert events.status_code == 200
    assert "id: 1" in events.text
    assert "event: completed" in events.text

    sessions = client.get("/sessions").json()["items"]
    assert sessions[0]["session_id"] == "api-session"
    transcript = client.get("/sessions/api-session/transcript").json()["items"]
    assert transcript[0]["content"] == "analyze"

    trial = client.get(f"/analyses/{analysis_id}/trial-log")
    assert trial.status_code == 200
    body = trial.json()
    assert body["analysis_id"] == analysis_id
    assert body["job"]["message"] == "analyze"
    assert any(row.get("event_type") == "queued" for row in body["file_log"])


def test_live_trial_recorder_roundtrip(tmp_path) -> None:
    from project_core.infra.live_trial_recorder import LiveTrialRecorder

    recorder = LiveTrialRecorder(tmp_path)
    recorder.append("ana-1", "queued", {"message_preview": "hello"}, source="api")
    recorder.append("ana-1", "progress", {"stage": "sql_plan"}, source="worker")
    rows = recorder.read("ana-1")
    assert len(rows) == 2
    assert rows[0]["event_type"] == "queued"
    assert rows[1]["data"]["stage"] == "sql_plan"

