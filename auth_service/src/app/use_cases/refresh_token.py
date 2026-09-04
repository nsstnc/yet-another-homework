from datetime import datetime, UTC, timedelta
import logging
from uuid import uuid4

from src.api.dependencies.security import Security, Tokens
from src.config import settings
from src.domain.entities.user_session import UserSession
from src.domain.repositories.user_session_repository import UserSessionRepository

logger = logging.getLogger(__name__)


class SessionDoesNotExists(Exception):
    pass


class SessionHasExpired(Exception):
    pass


class SessionWasRevoked(Exception):
    pass


class RefreshToken:
    def __init__(
            self,
            sessions: UserSessionRepository,
    ) -> None:
        self._sessions = sessions
        self._security = Security

    async def execute(
            self,
            refresh_token: str,
    ) -> Tokens:
        refresh_token_hash = self._security.hash_refresh_token(refresh_token)
        session = await self._sessions.get_by_refresh_token_hash(refresh_token_hash)

        if session is None:
            logger.warning("Session does not exist")
            raise SessionDoesNotExists

        if session.expires_at < datetime.now(UTC):
            logger.warning("Session has expired")
            raise SessionHasExpired

        if session.revoked_at:
            logger.warning("Session was revoked")
            raise SessionWasRevoked

        new_refresh_token = self._security.generate_refresh_token()

        new_session = UserSession(
            id=uuid4(),
            user_id=session.user_id,
            refresh_token_hash=self._security.hash_refresh_token(new_refresh_token),
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            created_at=datetime.now(UTC)
        )

        await self._sessions.add(new_session)
        # старую обнуляем
        await self._sessions.revoke_session(session.id)

        new_access_token = self._security.generate_access_token(str(new_session.user_id), str(new_session.id))

        return Tokens(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
