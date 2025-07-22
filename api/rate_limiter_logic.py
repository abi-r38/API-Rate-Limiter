# api/rate_limiter_logic.py

import time
from abc import ABC, abstractmethod
from typing import Tuple
from redis import Redis

class RateLimiterStrategy(ABC):
    @abstractmethod
    def is_allowed(self, user_id: str) -> Tuple[bool, int]:
        pass

class TokenBucket(RateLimiterStrategy):
    def __init__(self, redis_client: Redis, capacity: int, refill_rate: int):
        self.redis_client = redis_client
        self.capacity = capacity
        # UPDATED: Refill rate is now 1, as requested.
        self.refill_rate = refill_rate

    def is_allowed(self, user_id: str) -> Tuple[bool, int]:
        current_time = time.time()
        bucket_key = f"token_bucket:{user_id}"

        # THE DEFINITIVE FIX: Use HGET for each key individually. This is the most robust
        # way and removes all ambiguity about string-vs-byte keys from hgetall.
        last_tokens_val = self.redis_client.hget(bucket_key, 'tokens')
        last_refill_val = self.redis_client.hget(bucket_key, 'last_refill')

        # Check if the user is new
        if last_tokens_val is None:
            tokens = self.capacity - 1
            self.redis_client.hmset(bucket_key, {"tokens": tokens, "last_refill": current_time})
            return True, int(tokens)
        
        # For an existing user, convert the retrieved string values to floats.
        last_tokens = float(last_tokens_val)
        last_refill = float(last_refill_val)

        # The rest of the logic correctly calculates the refill.
        time_diff = current_time - last_refill
        new_tokens = last_tokens + time_diff * self.refill_rate
        tokens = min(self.capacity, new_tokens)

        if tokens >= 1:
            tokens -= 1
            self.redis_client.hmset(bucket_key, {"tokens": tokens, "last_refill": current_time})
            return True, int(tokens)
        else:
            self.redis_client.hmset(bucket_key, {"tokens": tokens, "last_refill": current_time})
            return False, int(tokens)