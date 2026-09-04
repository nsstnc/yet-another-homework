from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import RefreshRequest
from src.app.use_cases.refresh_token import RefreshToken
from src.infra.database.engine import get_db_session
from src.infra.database.repositories.user_session_repository import SqlAlchemyUserSessionRepository

router = APIRouter()


@router.post("/refresh")
async def refresh(
        request: RefreshRequest,
        session: AsyncSession = Depends(get_db_session),
):
    user_session_repository = SqlAlchemyUserSessionRepository(session)

    use_case = RefreshToken(
        sessions=user_session_repository
    )

    tokens = await use_case.execute(
        request.refresh_token
    )

    return tokens