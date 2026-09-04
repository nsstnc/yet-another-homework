from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import RefreshRequest
from src.infra.database.engine import get_db_session

router = APIRouter()


@router.post("/refresh")
async def refresh(
        request: RefreshRequest,
        session: AsyncSession = Depends(get_db_session),
):
    pass