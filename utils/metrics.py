"""
Prometheus metrics
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time


# Metrics
request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

generation_count = Counter(
    'generation_requests_total',
    'Total generation requests',
    ['user_id']
)

generation_tokens = Histogram(
    'generation_tokens',
    'Number of tokens generated',
    ['user_id']
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits'
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses'
)

rate_limit_exceeded = Counter(
    'rate_limit_exceeded_total',
    'Total rate limit violations',
    ['user_id']
)


async def metrics_middleware(request, call_next):
    """Middleware to track metrics"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response


def get_metrics():
    """Get Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
