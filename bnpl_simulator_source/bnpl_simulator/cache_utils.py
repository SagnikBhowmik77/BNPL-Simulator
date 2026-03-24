# cache_utils.py
"""
Utility functions for caching expensive queries to improve performance.
"""
import time
from typing import Dict, Any, Optional

# Simple in-memory cache for expensive queries
QUERY_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 300  # 5 minutes cache TTL

def get_cache_key(user_id: str, query_type: str) -> str:
    """Generate cache key for user-specific queries."""
    return f"{user_id}:{query_type}"

def is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """Check if cached data is still valid."""
    return time.time() - cache_entry['timestamp'] < CACHE_TTL

def get_cached_data(cache_key: str) -> Optional[Any]:
    """Retrieve data from cache if valid."""
    if cache_key in QUERY_CACHE:
        if is_cache_valid(QUERY_CACHE[cache_key]):
            return QUERY_CACHE[cache_key]['data']
        else:
            del QUERY_CACHE[cache_key]
    return None

def set_cached_data(cache_key: str, data: Any) -> None:
    """Store data in cache with timestamp."""
    QUERY_CACHE[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }