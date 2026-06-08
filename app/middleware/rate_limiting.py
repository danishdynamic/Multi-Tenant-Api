from fastapi import Request, HTTPException
from collections import defaultdict
import time

rate_limit = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    # Get client IP - handle cases where request.client might be None
    client_ip = None

    # Try to get from request.client first
    if request.client and hasattr(request.client, 'host'):
        client_ip = request.client.host
    else:
        # Fallback: try to get from headers (for proxies/load balancers)
        client_ip = request.headers.get('x-forwarded-for', request.headers.get('x-real-ip'))

    # If still no IP, use a default (not recommended for production)
    if not client_ip:
        client_ip = "unknown"

    now = time.time()

    # Clean old requests (older than 60 seconds)
    rate_limit[client_ip] = [t for t in rate_limit[client_ip] if now - t < 60]

    # Check rate limit (100 requests per minute)
    if len(rate_limit[client_ip]) >= 100:
        raise HTTPException(status_code=429, detail="Too many requests")

    # Add current request timestamp
    rate_limit[client_ip].append(now)

    response = await call_next(request)
    return response