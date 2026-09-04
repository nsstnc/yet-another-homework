from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import LoginRequest
from src.app.use_cases.login_user import LoginUser
from src.infra.database.engine import get_db_session
from src.infra.database.repositories.user_repository import SqlAlchemyUserRepository
from src.infra.database.repositories.user_session_repository import SqlAlchemyUserSessionRepository

router = APIRouter()


@router.post("/login")
async def login(
        request: LoginRequest,
        session: AsyncSession = Depends(get_db_session),
):
    user_repository = SqlAlchemyUserRepository(session)
    user_session_repository = SqlAlchemyUserSessionRepository(session)

    use_case = LoginUser(
        users=user_repository,
        sessions=user_session_repository,
    )

    tokens = await use_case.execute(
        email=request.email,
        password=request.password,
    )

    return tokens
