"""Item 24 concrete - the central A2A message router.

Routes an :class:`AgentRequest` to a target agent resolved from the registry by
name or capability. Transports:

  - in-process: call ``run(request)`` directly
  - http / https: POST to the agent's ``/run`` endpoint with optional TLS + bearer auth
"""

from __future__ import annotations

import os

from commons.logging import get_logger

from agent_core.io.schemas import AgentRequest, AgentResponse

from platform_core.config.schema import PlatformConfig
from platform_core.registry.agent_registry import PlatformAgentRegistry
from platform_core.router.a2a_client import A2AClientConfig

log = get_logger("platform_core.router")


class MessageRouter:
    """Resolve + deliver requests to agents."""

    def __init__(
        self,
        registry: PlatformAgentRegistry,
        *,
        transport: str = "in_process",
        config: PlatformConfig | None = None,
        a2a: A2AClientConfig | None = None,
    ) -> None:
        self.registry = registry
        self.transport = transport
        self.config = config
        self.a2a = a2a or A2AClientConfig()

    def send_to_agent(self, name: str, request: AgentRequest) -> AgentResponse:
        if self.transport in ("http", "https"):
            return self._send_http(name, request)
        return self._send_in_process(name, request)

    def send_to_capability(self, capability: str, request: AgentRequest) -> AgentResponse:
        return self.send_to_agent(self.registry.resolve_capability(capability), request)

    def _send_in_process(self, name: str, request: AgentRequest) -> AgentResponse:
        service = self.registry.create(name)
        log.info("Routing (in-process) -> %s", name)
        return service.run(request)

    def _resolve_token(self, name: str) -> str | None:
        if self.a2a.bearer_token:
            return self.a2a.bearer_token
        spec = self.registry.spec(name)
        if spec.auth_token_env:
            return os.getenv(spec.auth_token_env)
        return None

    def _send_http(self, name: str, request: AgentRequest) -> AgentResponse:
        import httpx

        card = self.registry.get(name)
        if not card.endpoint:
            raise RuntimeError(f"Agent '{name}' has no endpoint for HTTP routing")

        endpoint = card.endpoint
        if self.config and self.config.require_https and not endpoint.startswith("https://"):
            raise RuntimeError(f"Agent '{name}' endpoint must use HTTPS when require_https is set")

        url = endpoint.rstrip("/") + "/run"
        headers: dict[str, str] = {}
        token = self._resolve_token(name)
        if token:
            headers["Authorization"] = f"Bearer {token}"

        verify: bool | str = self.a2a.ca_bundle if self.a2a.ca_bundle else self.a2a.verify_ssl
        spec = self.registry.spec(name)
        if not spec.tls_verify:
            verify = False

        log.info("Routing (%s) -> %s at %s", self.transport, name, url)
        with httpx.Client(verify=verify, cert=self.a2a.client_cert, timeout=self.a2a.timeout) as client:
            resp = client.post(url, json=request.model_dump(), headers=headers)
        resp.raise_for_status()
        return AgentResponse(**resp.json())
