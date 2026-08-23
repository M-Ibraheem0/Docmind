from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.conversation import AskRequest, AskResponse
from app.api.v1.auth import get_current_user
from app.services.rag import get_answer
from app.services.cache import get_cached, set_cached

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cached = await get_cached(current_user.id, request.question)
    if cached:
        return AskResponse(
            question=request.question,
            answer=cached["answer"],
            sources=cached["sources"],
            cached=True,
        )

    result = await get_answer(request.question, current_user.id, db)

    await set_cached(current_user.id, request.question, result)

    return AskResponse(
        question=request.question,
        answer=result["answer"],
        sources=result["sources"],
        cached=False,
    )