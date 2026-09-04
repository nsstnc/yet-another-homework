from datetime import datetime, UTC

from src.api.dependencies.security import Security
from src.domain.repositories.user_session_repository import UserSessionRepository


class InvalidSessionError(Exception):
    pass


class LogoutUser:
    def __init__(
            self,
            sessions: UserSessionRepository,
    ) -> None:
        self._sessions = sessions
        self._security = Security

    async def execute(self, refresh_token: str) -> None:
        token_hash = self._security.hash_refresh_token(
            refresh_token
        )

        session = await self._sessions.get_by_refresh_token_hash(
            token_hash
        )

        if session is None:
            raise InvalidSessionError

        if session.revoked_at is not None:
            raise InvalidSessionError

        if session.expires_at <= datetime.now(UTC):
            raise InvalidSessionError

        await self._sessions.revoke_session(session.id)
