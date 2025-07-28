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
        self.refill_rate = refill_rate

    def is_allowed(self, user_id: str) -> Tuple[bool, int]:
        current_time = time.time()
        bucket_key = f"token_bucket:{user_id}"


        last_tokens_val = self.redis_client.hget(bucket_key, 'tokens')
        last_refill_val = self.redis_client.hget(bucket_key, 'last_refill')

        
        if last_tokens_val is None:
            tokens = self.capacity - 1
            self.redis_client.hmset(bucket_key, {"tokens": tokens, "last_refill": current_time})
            return True, int(tokens)
        
        
        last_tokens = float(last_tokens_val)
        last_refill = float(last_refill_val)

        
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
