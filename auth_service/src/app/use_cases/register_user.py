from datetime import UTC, datetime
from uuid import uuid4

from src.api.dependencies.security import Security
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class UserAlreadyExistsError(Exception):
    pass


class RegisterUser:
    def __init__(
            self,
            users: UserRepository,
    ) -> None:
        self._users = users
        self._security = Security

    async def execute(
            self,
            email: str,
            password: str,
    ) -> User:
        existing_user = await self._users.get_by_email(email)

        if existing_user is not None:
            raise UserAlreadyExistsError

        now = datetime.now(UTC)

        user = User(
            id=uuid4(),
            email=email,
            password_hash=self._security.hash(password),
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        await self._users.add(user)

        return user
