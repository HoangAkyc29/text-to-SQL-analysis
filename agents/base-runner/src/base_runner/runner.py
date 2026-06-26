"""Generic platform runner — executes the agent graph on demand or on a poll interval."""

from __future__ import annotations

import argparse
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path

from platform_core.runtime.platform import AgentPlatform
from project_core.config.env import load_project_env
from project_core.runtime.scheduler import sleep_interval

# TODO: load project config from config/project.yaml
# TODO: ProjectStateStore, preflight gates, audit_log from project_core.domain


class BaseRunner:
    """Scaffold runner — implement run_once() for your trigger model (poll, queue, webhook, …)."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root = root_dir or Path.cwd()
        load_project_env(self.root)
        os.environ.setdefault("AGENT_ROOT_DIR", str(self.root))
        os.environ.setdefault("AGENT_DATA_DIR", str(self.root / "data"))
        transport = os.getenv("PLATFORM_TRANSPORT", "in_process")
        self.platform = AgentPlatform.from_config(transport=transport)
        # TODO: self.config = load_project_config(self.root)
        # TODO: self.store = ProjectStateStore(...)

    def run_once(
        self,
        goal: str | None = None,
        *,
        use_llm: bool = True,
        inputs: dict | None = None,
    ) -> dict:
        """
        TODO checklist for one execution:
        1. new_run_id(), preflight (feature flags, rate limits)
        2. Fetch context snapshot (DB, API, user session, …)
        3. Build run metadata
        4. platform.run_goal(...) → graph executes agents
        5. Record run in state store + audit log
        """
        run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-todo"
        run_goal = goal or f"template run {run_id}"
        merged_inputs = {
            "run_id": run_id,
            "use_llm": use_llm,
            "status": "todo",
            **(inputs or {}),
        }
        result = self.platform.run_goal(
            goal=run_goal,
            actor_id="base_runner",
            inputs=merged_inputs,
        )
        return {
            "run_id": run_id,
            "goal": run_goal,
            "status": "todo",
            "message": "Implement BaseRunner.run_once()",
            "graph": result,
        }

    def run_loop(
        self,
        goal: str | None = None,
        *,
        use_llm: bool = True,
        interval: str = "60s",
    ) -> None:
        """Poll on a wall-clock interval, then run_once()."""
        while True:
            sleep_interval(interval)
            try:
                result = self.run_once(goal=goal, use_llm=use_llm)
                print(json.dumps(result, indent=2, default=str), flush=True)
            except Exception as exc:
                print(
                    json.dumps({"status": "error", "error": str(exc), "continuing": True}),
                    flush=True,
                )
                traceback.print_exc()


def main() -> None:
    parser = argparse.ArgumentParser(description="Base platform runner (template)")
    parser.add_argument("--once", action="store_true", help="Run the graph once")
    parser.add_argument("--loop", action="store_true", help="Poll forever at --interval")
    parser.add_argument("--goal", default=None, help="Goal passed to platform.run_goal()")
    parser.add_argument(
        "--interval",
        default="60s",
        help="Poll interval for --loop (e.g. 30s, 5m, 1h)",
    )
    parser.add_argument("--no-llm", action="store_true", help="Deterministic mode without LLM")
    args = parser.parse_args()

    runner = BaseRunner()
    use_llm = not args.no_llm
    if args.loop:
        runner.run_loop(goal=args.goal, use_llm=use_llm, interval=args.interval)
    else:
        result = runner.run_once(goal=args.goal, use_llm=use_llm)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
