from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.database import get_db
from app.models.user import User
from app.schemas.conversation import AskRequest
from app.api.v1.auth import get_current_user
from app.services.rag import get_answer
from app.services.cache import get_cached
from app.services.pdf_report import generate_qa_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/export")
async def export_report(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cached = await get_cached(current_user.id, request.question)
    if cached:
        result = cached
    else:
        result = await get_answer(request.question, current_user.id, db)

    pdf_bytes = generate_qa_pdf(
        question=request.question,
        answer=result["answer"],
        sources=result["sources"],
    )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=docmind_report.pdf"}
    )