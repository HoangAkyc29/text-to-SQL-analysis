"""CLI entry point: ``agent-platform``.

Runs the full agent graph defined in platform.yaml for a goal.
"""

from __future__ import annotations

import argparse
import json

from commons.logging import get_logger

from platform_core.runtime.platform import AgentPlatform

log = get_logger("platform_core.cli")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the multi-agent control plane")
    parser.add_argument("--goal", default="Run the configured agent graph")
    parser.add_argument(
        "--inputs",
        default="{}",
        help='JSON object merged into each agent request metadata (e.g. \'{"tenant_id":"acme"}\')',
    )
    parser.add_argument("--config", default=None, help="path to platform.yaml")
    parser.add_argument(
        "--transport",
        default="in_process",
        choices=["in_process", "http", "https"],
        help="how the router reaches agents",
    )
    args = parser.parse_args()

    run_inputs = json.loads(args.inputs)
    if not isinstance(run_inputs, dict):
        raise SystemExit("--inputs must be a JSON object")

    platform = AgentPlatform.from_config(args.config, transport=args.transport)
    result = platform.run_goal(args.goal, inputs=run_inputs)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
