from abc import ABC, abstractmethod

from src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, user: User) -> None:
        raise NotImplementedError
