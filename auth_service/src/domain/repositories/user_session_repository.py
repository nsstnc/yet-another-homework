from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user_session import UserSession


class UserSessionRepository(ABC):
    @abstractmethod
    async def get_by_refresh_token_hash(self, token_hash: str) -> UserSession | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, user_session: UserSession) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_session(
            self,
            session_id: UUID,
    ) -> bool:
        raise NotImplementedError
