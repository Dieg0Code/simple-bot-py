

from datetime import datetime, timezone

from sqlmodel import JSON, Column, Field, SQLModel


class ChatSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_phone: str
    history: list[dict[str, str]] = Field(default_factory=list, sa_column=Column(JSON))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
