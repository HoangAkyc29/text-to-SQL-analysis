from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlencode

import httpx

from chat_gateway.auth import issue_token


class OAuthProvider(ABC):
    @abstractmethod
    def authorization_url(self, state: str) -> str: ...

    @abstractmethod
    def exchange_code(self, code: str) -> dict[str, Any]: ...


class LocalDevOAuthProvider(OAuthProvider):
    def authorization_url(self, state: str) -> str:
        return f"/auth/dev-login?state={state}"

    def exchange_code(self, code: str) -> dict[str, Any]:
        return {
            "access_token": issue_token("dev-user", "hq_analyst"),
            "token_type": "bearer",
        }


class AzureOAuthProvider(OAuthProvider):
    def __init__(self) -> None:
        self.tenant = os.getenv("AZURE_TENANT_ID", "common")
        self.client_id = os.getenv("OAUTH_CLIENT_ID", "")
        self.client_secret = os.getenv("OAUTH_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8300/auth/callback")

    def authorization_url(self, state: str) -> str:
        params = urlencode(
            {
                "client_id": self.client_id,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "response_mode": "query",
                "scope": "openid profile email",
                "state": state,
            }
        )
        return f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/authorize?{params}"

    def exchange_code(self, code: str) -> dict[str, Any]:
        token_url = f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(token_url, data=data)
            resp.raise_for_status()
            token_data = resp.json()
        # Map Azure user to internal JWT — production should lookup Auth DB.
        return {
            "access_token": issue_token("azure-user", "hq_analyst"),
            "token_type": "bearer",
            "provider_token": token_data,
        }


def oauth_provider_from_env() -> OAuthProvider:
    provider = os.getenv("OAUTH_PROVIDER", "local").lower()
    if provider == "azure":
        return AzureOAuthProvider()
    return LocalDevOAuthProvider()
