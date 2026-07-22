from __future__ import annotations

import logging
import os
import socket

from chat_gateway.analysis_service import AnalysisWorker, create_analysis_service
from chat_gateway.orchestrator import ChatOrchestrator

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def main() -> None:
    service = create_analysis_service()
    worker_id = os.getenv("ANALYSIS_WORKER_ID") or f"{socket.gethostname()}-{os.getpid()}"
    worker = AnalysisWorker(
        service.repository,
        service.queue,
        ChatOrchestrator(),
        worker_id=worker_id,
        lease_seconds=int(os.getenv("ANALYSIS_LEASE_SECONDS", "120")),
        recorder=service.recorder,
    )
    service.queue.ensure_group()
    logger.info("analysis worker started as %s", worker_id)
    while True:
        try:
            reclaimed = service.queue.reclaim(
                worker_id,
                idle_ms=int(os.getenv("ANALYSIS_RECLAIM_IDLE_MS", "180000")),
            )
            messages = reclaimed or service.queue.read(
                worker_id,
                count=1,
                block_ms=int(os.getenv("ANALYSIS_QUEUE_BLOCK_MS", "5000")),
            )
            for message in messages:
                worker.process(message)
        except Exception:
            logger.exception("analysis worker poll failed; retrying")
            continue


if __name__ == "__main__":
    main()

