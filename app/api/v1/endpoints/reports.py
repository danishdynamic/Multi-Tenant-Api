from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.report_repository import ReportRepository
from app.services.report_service import ReportService
from app.schemas.report import ReportCreate, Report
from app.core.dependencies import get_current_user
from app.db.models import User
from typing import List, cast

router = APIRouter()

@router.post("/", response_model=Report)
async def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if report.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized for this tenant")
    
    repo = ReportRepository(db)
    service = ReportService(repo)
    return await service.create_report(report)

@router.get("/", response_model=List[Report])
async def get_user_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = cast(int, current_user.id)
    repo = ReportRepository(db)
    service = ReportService(repo)
    return await service.get_user_reports(user_id)

@router.get("/{report_id}/pdf")
async def download_report_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tenant_id = cast(int, current_user.tenant_id)
    repo = ReportRepository(db)
    report = await repo.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if cast(int, report.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    service = ReportService(repo)
    title = cast(str, report.title)
    content = cast(str, report.content)
    pdf_buffer = service.generate_pdf_report(title, content)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={title}.pdf"}
    )