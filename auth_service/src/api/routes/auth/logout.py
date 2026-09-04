from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import LogoutRequest
from src.app.use_cases.logout_user import LogoutUser
from src.infra.database.engine import get_db_session
from src.infra.database.repositories.user_session_repository import SqlAlchemyUserSessionRepository

router = APIRouter()


@router.post("/logout")
async def logout(
        request: LogoutRequest,
        session: AsyncSession = Depends(get_db_session),
):
    user_session_repository = SqlAlchemyUserSessionRepository(session)

    use_case = LogoutUser(
        sessions=user_session_repository
    )

    tokens = await use_case.execute(
        request.refresh_token
    )

    return tokens
