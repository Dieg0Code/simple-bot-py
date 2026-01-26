from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlmodel import JSON, Column, Field, SQLModel


class ChatSession(SQLModel, table=True):
    """Modelo que representa una sesión de chat con el historial de mensajes."""

    id: int | None = Field(default=None, primary_key=True)
    user_phone: str
    history: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    )
