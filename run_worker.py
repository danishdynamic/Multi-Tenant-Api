#!/usr/bin/env python3
"""
Script to run the background worker for processing RabbitMQ messages.
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.workers.worker import worker

if __name__ == "__main__":
    print("🚀 Starting SaaS Backend Worker...")
    print("Processing queues: email_notifications, pdf_generation, background_jobs")

    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        print("\n🛑 Worker stopped by user")
        asyncio.run(worker.stop())
    except Exception as e:
        print(f"❌ Worker error: {e}")
        sys.exit(1)