"""API key authentication stub with role claims."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from api.config import get_settings


@dataclass
class Principal:
    username: str
    role: str


# Simple stub: API key maps to role
KEY_ROLES = {
    "dev-api-key-change-me": Principal("analyst", "analyst"),
    "admin-api-key": Principal("admin", "admin"),
    "viewer-api-key": Principal("viewer", "viewer"),
}


def get_principal(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> Principal:
    settings = get_settings()
    if x_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key")
    if x_api_key == settings.api_key:
        return KEY_ROLES.get(settings.api_key, Principal("analyst", "analyst"))
    principal = KEY_ROLES.get(x_api_key)
    if not principal:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return principal


def require_roles(*roles: str):
    def _dep(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.role not in roles and principal.role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient role")
        return principal

    return _dep
