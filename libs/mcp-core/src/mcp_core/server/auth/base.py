"""MCP server authentication and authorization."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(slots=True)
class AuthContext:
    """Identity + granted scopes for a request."""

    principal: str
    scopes: list[str] = field(default_factory=list)
    token: str | None = None
    claims: dict[str, object] = field(default_factory=dict)


class Authorizer(ABC):
    """Decide whether a principal may perform an action on a target."""

    @abstractmethod
    def authenticate(self, token: str | None) -> AuthContext:
        """Resolve a token into an :class:`AuthContext` (may raise on invalid)."""

    @abstractmethod
    def authorize(self, ctx: AuthContext, *, target: str, action: str) -> bool:
        """Return True if ``ctx`` may ``action`` on ``target``."""


class AllowAll(Authorizer):
    """Permissive default for local/demo use."""

    def authenticate(self, token: str | None) -> AuthContext:
        return AuthContext(principal="anonymous", scopes=["*"], token=token)

    def authorize(self, ctx: AuthContext, *, target: str, action: str) -> bool:
        return True


@dataclass(slots=True)
class AuthPolicy:
    """Map tool/resource names to required scopes."""

    tool_scopes: dict[str, list[str]] = field(default_factory=dict)
    default_scopes: list[str] = field(default_factory=list)

    def required_scopes(self, target: str) -> list[str]:
        return self.tool_scopes.get(target, self.default_scopes)

    def allows(self, ctx: AuthContext, target: str) -> bool:
        if "*" in ctx.scopes:
            return True
        required = self.required_scopes(target)
        if not required:
            return True
        return any(s in ctx.scopes for s in required)


class BearerTokenAuthorizer(Authorizer):
    """Validate static bearer tokens mapped to principals + scopes."""

    def __init__(
        self,
        tokens: dict[str, AuthContext],
        *,
        policy: AuthPolicy | None = None,
    ) -> None:
        self._tokens = tokens
        self.policy = policy or AuthPolicy()

    def authenticate(self, token: str | None) -> AuthContext:
        if not token:
            raise PermissionError("missing bearer token")
        if token not in self._tokens:
            raise PermissionError("invalid bearer token")
        return self._tokens[token]

    def authorize(self, ctx: AuthContext, *, target: str, action: str) -> bool:
        return self.policy.allows(ctx, target)


class JwtAuthorizer(Authorizer):
    """Validate JWT bearer tokens (HS256/RS256). Requires mcp-core[auth]."""

    def __init__(
        self,
        *,
        secret: str | None = None,
        public_key: str | None = None,
        algorithms: list[str] | None = None,
        audience: str | None = None,
        policy: AuthPolicy | None = None,
    ) -> None:
        self.secret = secret
        self.public_key = public_key
        self.algorithms = algorithms or (["HS256"] if secret else ["RS256"])
        self.audience = audience
        self.policy = policy or AuthPolicy()

    def authenticate(self, token: str | None) -> AuthContext:
        if not token:
            raise PermissionError("missing bearer token")
        try:
            import jwt
        except ImportError as exc:
            raise ImportError("JWT auth requires mcp-core[auth]") from exc

        key = self.secret or self.public_key
        if not key:
            raise ValueError("JwtAuthorizer requires secret or public_key")
        payload = jwt.decode(
            token,
            key,
            algorithms=self.algorithms,
            audience=self.audience,
            options={"verify_aud": bool(self.audience)},
        )
        scopes = payload.get("scope", "")
        if isinstance(scopes, str):
            scopes = scopes.split()
        return AuthContext(
            principal=str(payload.get("sub", "jwt-user")),
            scopes=list(scopes),
            token=token,
            claims=dict(payload),
        )

    def authorize(self, ctx: AuthContext, *, target: str, action: str) -> bool:
        return self.policy.allows(ctx, target)


class CompositeAuthorizer(Authorizer):
    """Try multiple authorizers in order (first successful authenticate wins)."""

    def __init__(self, authorizers: list[Authorizer], *, policy: AuthPolicy | None = None) -> None:
        self._authorizers = authorizers
        self.policy = policy or AuthPolicy()

    def authenticate(self, token: str | None) -> AuthContext:
        last_err: Exception | None = None
        for auth in self._authorizers:
            try:
                return auth.authenticate(token)
            except Exception as exc:  # noqa: BLE001
                last_err = exc
        raise PermissionError(str(last_err or "authentication failed"))

    def authorize(self, ctx: AuthContext, *, target: str, action: str) -> bool:
        return self.policy.allows(ctx, target)
