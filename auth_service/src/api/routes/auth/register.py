from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import RegisterRequest
from src.app.use_cases.register_user import RegisterUser
from src.infra.database.engine import get_db_session
from src.infra.database.repositories.user_repository import SqlAlchemyUserRepository

router = APIRouter()


@router.post("/register")
async def register(
        request: RegisterRequest,
        session: AsyncSession = Depends(get_db_session),
):
    repository = SqlAlchemyUserRepository(session)

    use_case = RegisterUser(
        users=repository,
    )

    user = await use_case.execute(
        email=request.email,
        password=request.password,
    )

    return {
        "id": user.id,
        "email": user.email,
    }
