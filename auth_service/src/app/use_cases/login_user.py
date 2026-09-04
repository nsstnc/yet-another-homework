import logging
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.api.dependencies.security import Security, Tokens
from src.config import settings
from src.domain.entities.user_session import UserSession
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.user_session_repository import UserSessionRepository


logger = logging.getLogger(__name__)

class InvalidCredentialsError(Exception):
    pass


class UserDoesNotExists(Exception):
    pass


class LoginUser:
    def __init__(
            self,
            users: UserRepository,
            sessions: UserSessionRepository,
    ) -> None:
        self._users = users
        self._sessions = sessions
        self._security = Security

    async def execute(
            self,
            email: str,
            password: str,
    ) -> Tokens:
        user = await self._users.get_by_email(email)

        if user is None:
            logger.warning("User does not exist", user)
            raise UserDoesNotExists

        if not self._security.verify(
                password,
                user.password_hash,
        ):
            raise InvalidCredentialsError

        refresh_token = self._security.generate_refresh_token()

        session = UserSession(
            id=uuid4(),
            user_id=user.id,
            refresh_token_hash=self._security.hash_refresh_token(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            created_at=datetime.now(UTC)
        )

        await self._sessions.add(session)

        access_token = self._security.generate_access_token(str(user.id), str(session.id))

        return Tokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )
