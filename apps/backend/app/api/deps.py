"""Authentication dependencies.

Auth is opt-in: when ``settings.require_api_key`` is false the API stays open
(useful for local dev and public demos). When true, a valid key must be presented
via ``X-API-Key`` or ``Authorization: Bearer <key>``. A configured
``settings.admin_api_key`` acts as a bootstrap master key for managing other keys.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models import ApiKey
from app.services.security import hash_api_key


@dataclass
class Identity:
    kind: str  # "admin" | "api_key"
    name: str | None = None
    key_id: str | None = None


def _extract_key(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    header_key = request.headers.get("X-API-Key")
    return header_key.strip() if header_key else None


def _authenticate(request: Request, db: Session) -> Identity | None:
    key = _extract_key(request)
    if not key:
        return None

    admin = settings.admin_api_key
    if admin and secrets.compare_digest(key, admin):
        return Identity(kind="admin", name="admin")

    row = db.execute(
        select(ApiKey).where(ApiKey.key_hash == hash_api_key(key))
    ).scalar_one_or_none()
    if row is not None and row.active:
        row.last_used_at = datetime.now(timezone.utc)
        db.commit()
        return Identity(kind="api_key", name=row.name, key_id=str(row.id))

    return None


def require_auth(request: Request, db: Session = Depends(get_db)) -> Identity | None:
    identity = _authenticate(request, db)
    if settings.require_api_key and identity is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return identity


def require_admin(request: Request, db: Session = Depends(get_db)) -> Identity:
    identity = _authenticate(request, db)
    if identity is None or identity.kind != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="admin API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return identity
