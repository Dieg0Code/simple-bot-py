import logging
from logging import Logger

from data.models.chat import ChatSession
from data.repository.chat_repository import ChatRepository

logger: Logger = logging.getLogger(name=__name__)


class ChatService:
    def __init__(self, chat_repository: ChatRepository) -> None:
        self.chat_repository = chat_repository

    async def get_history(
        self, user_phone: str, max_messages: int = 20
    ) -> list[dict[str, str]]:
        logger.debug(
            msg="Fetching chat history",
            extra={"user_phone": user_phone, "max_messages": max_messages},
        )

        if max_messages <= 0:
            logger.warning("Max messages must be positive, received %d", max_messages)
            return []

        if max_messages > 20:
            logger.warning("Max messages %d exceeds limit, capping to 20", max_messages)
            max_messages = 20

        if user_phone.strip() == "":
            logger.error("User phone number is empty")
            return []

        return await self.chat_repository.get_history(user_phone, max_messages)

    async def save_conversation(
        self, user_phone: str, messages: list[dict[str, str]]
    ) -> ChatSession:
        logger.info(
            "Saving chat conversation",
            extra={"user_phone": user_phone, "message_count": len(messages)},
        )

        if user_phone.strip() == "":
            logger.error("User phone number is empty")
            raise ValueError("User phone number cannot be empty")

        if not messages:
            logger.warning("No messages to save for user_phone: %s", user_phone)
            raise ValueError("Messages list cannot be empty")

        return await self.chat_repository.save_conversation(user_phone, messages)
