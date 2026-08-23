import json
import hashlib
import redis.asyncio as aioredis
from app.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
CACHE_TTL = 60 * 60  # 1 hour


def make_cache_key(user_id: int, question: str) -> str:
    hash = hashlib.md5(f"{user_id}:{question.strip().lower()}".encode()).hexdigest()
    return f"docmind:ask:{hash}"


async def get_cached(user_id: int, question: str):
    key = make_cache_key(user_id, question)
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cached(user_id: int, question: str, result: dict):
    key = make_cache_key(user_id, question)
    await redis_client.setex(key, CACHE_TTL, json.dumps(result))