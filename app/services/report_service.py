from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportCreate, Report
from app.db.models import Report as ReportModel, User
from app.core.cache import cache
from app.core.message_queue import message_queue
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, repo: ReportRepository):
        self.repo = repo

    async def create_report(self, report_data: ReportCreate) -> ReportModel:
        report = ReportModel(
            title=report_data.title,
            content=report_data.content,
            tenant_id=report_data.tenant_id,
            user_id=report_data.user_id
        )

        created_report = await self.repo.create(report)

        # Invalidate cache for this user
        await cache.delete(f"user_{report_data.user_id}_reports")

        # Queue PDF generation for async processing
        await self._queue_pdf_generation(created_report)

        return created_report

    async def get_user_reports(self, user_id: int, limit: int = 20) -> List[ReportModel]:
        """Get reports for a user with caching"""
        cache_key = f"user_{user_id}_reports_{limit}"

        async def fetch_reports():
            # Use join to get user info efficiently
            query = select(ReportModel).options(
                joinedload(ReportModel.user)
            ).where(ReportModel.user_id == user_id).order_by(
                ReportModel.created_at.desc()
            ).limit(limit)

            result = await self.repo.session.execute(query)
            return result.scalars().unique().all()

        return await cache.get_or_set(cache_key, fetch_reports)

    async def get_report_with_user(self, report_id: int, tenant_id: int) -> Optional[ReportModel]:
        """Get a specific report with user info using join"""
        cache_key = f"report_{report_id}_tenant_{tenant_id}"

        async def fetch_report():
            query = select(ReportModel).options(
                joinedload(ReportModel.user)
            ).where(
                ReportModel.id == report_id,
                ReportModel.tenant_id == tenant_id
            )

            result = await self.repo.session.execute(query)
            return result.scalars().first()

        return await cache.get_or_set(cache_key, fetch_report)

    async def _queue_pdf_generation(self, report: ReportModel):
        """Queue PDF generation for async processing"""
        try:
            message_data = {
                'report_id': report.id,
                'title': report.title,
                'content': report.content,
                'tenant_id': report.tenant_id
            }

            await message_queue.publish_message(
                'pdf_generation',
                message_data,
                priority=2  # Higher priority for reports
            )
            logger.info(f"Queued PDF generation for report {report.id}")
        except Exception as e:
            logger.error(f"Failed to queue PDF generation: {e}")

    def generate_pdf_report(self, title: str, content: str) -> BytesIO:
        """Generate PDF report synchronously"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, title)

        # Content
        c.setFont("Helvetica", 12)
        y_position = 700
        for line in content.split('\n'):
            if y_position < 50:
                c.showPage()
                y_position = 750
            c.drawString(100, y_position, line[:80])  # Limit line length
            y_position -= 20

        c.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    async def process_pdf_generation(message_data: dict):
        """Process PDF generation from queue"""
        try:
            # Generate PDF and store it (could save to file system or database)
            pdf_buffer = ReportService.generate_pdf_report_static(
                message_data['title'],
                message_data['content']
            )

            # Here you could save the PDF to a file system or cloud storage
            # For now, we'll just log that it was generated
            logger.info(f"Generated PDF for report {message_data['report_id']}")

        except Exception as e:
            logger.error(f"Failed to generate PDF for report {message_data['report_id']}: {e}")

    @staticmethod
    def generate_pdf_report_static(title: str, content: str) -> BytesIO:
        """Static method for PDF generation (used by queue processor)"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, title)

        # Content
        c.setFont("Helvetica", 12)
        y_position = 700
        for line in content.split('\n'):
            if y_position < 50:
                c.showPage()
                y_position = 750
            c.drawString(100, y_position, line[:80])
            y_position -= 20

        c.save()
        buffer.seek(0)
        return buffer