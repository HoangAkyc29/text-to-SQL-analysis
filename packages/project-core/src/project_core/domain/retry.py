from __future__ import annotations

from tenacity import retry, stop_after_attempt, wait_exponential

from project_core.config.loader import load_project_config


def sql_gateway_retry():
    return retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.5, min=0.5, max=4), reraise=True)


def agent_invoke_retry():
    cfg = load_project_config()
    return retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.3, min=0.3, max=2), reraise=True)
