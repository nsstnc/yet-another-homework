from abc import ABC, abstractmethod

from src.domain.entities.user_session import UserSession


class UserSessionRepository(ABC):
    @abstractmethod
    async def get_by_refresh_token_hash(self, token_hash: str) -> UserSession | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, user_session: UserSession) -> None:
        raise NotImplementedError
