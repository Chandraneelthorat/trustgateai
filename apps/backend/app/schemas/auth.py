from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class ApiKeyCreated(BaseModel):
    id: uuid.UUID
    name: str
    prefix: str
    api_key: str  # plaintext, returned once
    created_at: datetime


class ApiKeyRead(BaseModel):
    id: uuid.UUID
    name: str
    prefix: str
    active: bool
    created_at: datetime
    last_used_at: datetime | None = None
