from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user_session import UserSession
from src.domain.repositories.user_session_repository import UserSessionRepository
from src.infra.database.models.user_session import UserSessionModel


class SqlAlchemyUserSessionRepository(UserSessionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, session: UserSession) -> None:
        model = UserSessionModel(
            id=session.id,
            user_id=session.user_id,
            refresh_token_hash=session.refresh_token_hash,
            expires_at=session.expires_at,
            created_at=session.created_at,
            revoked_at=session.revoked_at,
        )

        self._session.add(model)

        await self._session.commit()

    async def get_by_refresh_token_hash(self, token_hash: str) -> UserSession | None:
        stmt = select(UserSessionModel).where(UserSessionModel.refresh_token_hash == token_hash)

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: UserSessionModel) -> UserSession:
        return UserSession(
            id=model.id,
            user_id=model.user_id,
            refresh_token_hash=model.refresh_token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            revoked_at=model.revoked_at
        )
