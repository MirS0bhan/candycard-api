import time

from fastapi import Depends
from cachetools import TTLCache

from auth import oauth2_scheme
from errors import credentials_exception, flowd_exception


def rate_limit_builder(rete_limit: int, time_window: int, cache_size: int = 1000):
    cache = TTLCache(maxsize=cache_size, ttl=time_window)

    async def rate_limit_middleware(token: str = Depends(oauth2_scheme)):
        if not token:
            raise credentials_exception

        current_time = time.time()

        # Get the current request count and timestamp for the token
        request_count, timestamp = cache.get(token, (0, current_time))

        # Reset the count if the time window has expired
        if current_time - timestamp > time_window:
            request_count = 0
            timestamp = current_time

        # Check if the rate limit is exceeded
        if request_count >= rete_limit:
            raise flowd_exception

        # Increment the request count and update the cache
        request_count += 1
        cache[token] = (request_count, timestamp)

        # Proceed to the next middleware or request handler
        return True  # or you can return None to indicate success

    return rate_limit_middleware
