import asyncio
import logging
from app.core.message_queue import message_queue
from app.services.notification_service import NotificationService
from app.services.report_service import ReportService
from app.core.config import settings

logger = logging.getLogger(__name__)

class BackgroundWorker:
    def __init__(self):
        self.running = False

    async def start(self):
        """Start the background worker"""
        self.running = True
        logger.info("Starting background worker...")

        try:
            # Connect to message queue
            await message_queue.connect()

            # Start consuming different queues
            await asyncio.gather(
                self._consume_email_notifications(),
                self._consume_pdf_generation(),
                self._consume_general_jobs()
            )
        except Exception as e:
            logger.error(f"Error in background worker: {e}")
        finally:
            await message_queue.close()

    async def stop(self):
        """Stop the background worker"""
        self.running = False
        await message_queue.close()
        logger.info("Background worker stopped")

    async def _consume_email_notifications(self):
        """Consume email notification messages"""
        logger.info("Starting email notification consumer...")

        async def process_email(message_data):
            await NotificationService.process_email_queue(message_data)

        await message_queue.consume_messages('email_notifications', process_email)

    async def _consume_pdf_generation(self):
        """Consume PDF generation messages"""
        logger.info("Starting PDF generation consumer...")

        async def process_pdf(message_data):
            await ReportService.process_pdf_generation(message_data)

        await message_queue.consume_messages('pdf_generation', process_pdf)

    async def _consume_general_jobs(self):
        """Consume general background jobs"""
        logger.info("Starting general job consumer...")

        async def process_job(message_data):
            job_type = message_data.get('type')
            if job_type == 'cache_invalidation':
                # Handle cache invalidation jobs
                tenant_id = message_data.get('tenant_id')
                if tenant_id:
                    from app.core.cache import cache
                    await cache.invalidate_tenant_cache(tenant_id)
                    logger.info(f"Invalidated cache for tenant {tenant_id}")
            elif job_type == 'data_cleanup':
                # Handle data cleanup jobs
                logger.info("Running data cleanup job")
                # Add cleanup logic here
            else:
                logger.warning(f"Unknown job type: {job_type}")

        await message_queue.consume_messages('background_jobs', process_job)

# Global worker instance
worker = BackgroundWorker()

if __name__ == "__main__":
    # Run worker directly
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
        asyncio.run(worker.stop())