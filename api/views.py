from django.shortcuts import render
from django.http import JsonResponse
from redis import Redis
from .rate_limiter_logic import TokenBucket

redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)
token_bucket_strategy = TokenBucket(redis_client, capacity=100, refill_rate=1)

def serve_home(request):
    return render(request, 'index.html')

def get_resource(request):
    user_id = "django_demo_user"
    is_allowed, tokens_left = token_bucket_strategy.is_allowed(user_id)
    if is_allowed:
        response = JsonResponse({"message": "Success! Data from Django Backend."}, status=200)
    else:
        response = JsonResponse({"detail": f"Too Many Requests. Tokens left: {tokens_left}"}, status=429)
    response['X-RateLimit-Tokens-Left'] = str(tokens_left)
    return response