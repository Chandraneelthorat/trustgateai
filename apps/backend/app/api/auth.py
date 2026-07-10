from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models import ApiKey
from app.schemas.auth import ApiKeyCreate, ApiKeyCreated, ApiKeyRead
from app.services.security import generate_api_key, hash_api_key, key_display_prefix

router = APIRouter(prefix="/auth/keys", tags=["auth"])


@router.post("", response_model=ApiKeyCreated, dependencies=[Depends(require_admin)])
async def create_key(body: ApiKeyCreate, db: Session = Depends(get_db)) -> ApiKeyCreated:
    raw = generate_api_key()
    row = ApiKey(name=body.name, prefix=key_display_prefix(raw), key_hash=hash_api_key(raw))
    db.add(row)
    db.commit()
    db.refresh(row)
    return ApiKeyCreated(
        id=row.id,
        name=row.name,
        prefix=row.prefix,
        api_key=raw,
        created_at=row.created_at,
    )


@router.get("", response_model=list[ApiKeyRead], dependencies=[Depends(require_admin)])
async def list_keys(db: Session = Depends(get_db)) -> list[ApiKeyRead]:
    rows = db.execute(select(ApiKey).order_by(ApiKey.created_at.desc())).scalars().all()
    return [
        ApiKeyRead(
            id=r.id,
            name=r.name,
            prefix=r.prefix,
            active=r.active,
            created_at=r.created_at,
            last_used_at=r.last_used_at,
        )
        for r in rows
    ]


@router.delete("/{key_id}", dependencies=[Depends(require_admin)])
async def revoke_key(key_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    row = db.get(ApiKey, key_id)
    if row is None:
        raise HTTPException(status_code=404, detail="key not found")
    row.active = False
    db.add(row)
    db.commit()
    return {"ok": True, "id": str(key_id), "active": row.active}
