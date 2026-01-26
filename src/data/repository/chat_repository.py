import logging

from pydantic_ai import ModelMessage, ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from data.models.chat import ChatSession

logger = logging.getLogger(__name__)


class ChatRepository:
    """Repositorio para gestionar sesiones de chat con Pydantic AI"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_phone(self, user_phone: str) -> ChatSession | None:
        """Obtiene una sesión por número de teléfono"""
        logger.debug("Getting chat session", extra={"user_phone": user_phone})
        stmt = select(ChatSession).where(ChatSession.user_phone == user_phone)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_phone: str) -> ChatSession:
        """Obtiene la sesión o la crea si no existe"""
        logger.info("Get or create chat session", extra={"user_phone": user_phone})
        chat = await self.get_by_phone(user_phone)
        if not chat:
            chat = ChatSession(user_phone=user_phone)
            self.session.add(chat)
            await self.session.commit()
            await self.session.refresh(chat)
        return chat

    async def save_conversation(
        self, user_phone: str, messages: list[ModelMessage]
    ) -> ChatSession:
        """Guarda el estado completo de la conversación"""
        logger.info("Saving conversation", extra={"user_phone": user_phone})
        chat = await self.get_or_create(user_phone)
        chat.history = to_jsonable_python(messages)  # Reemplaza (no append)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def get_history(
        self, user_phone: str, max_messages: int = 20
    ) -> list[ModelMessage]:
        """
        Obtiene el historial truncado de forma segura.
        Mantiene bloques completos user->assistant para evitar romper tool calls.
        """
        chat = await self.get_by_phone(user_phone)
        if not chat or len(chat.history) <= max_messages:
            return (
                ModelMessagesTypeAdapter.validate_python(chat.history) if chat else []
            )

        # Tomar desde el final
        messages = chat.history[-max_messages:]

        # Buscar el primer mensaje "user" para empezar desde un turno completo
        first_user_idx = next(
            (i for i, msg in enumerate(messages) if msg.get("role") == "user"), 0
        )

        return ModelMessagesTypeAdapter.validate_python(messages[first_user_idx:])

    async def delete_session(self, user_phone: str) -> bool:
        """Elimina una sesión de chat"""
        logger.info("Deleting chat session", extra={"user_phone": user_phone})
        chat = await self.get_by_phone(user_phone)
        if chat:
            await self.session.delete(chat)
            await self.session.commit()
            return True
        return False
