import json
from typing import Any

from redis.exceptions import RedisError

from app.core.redis import redis_client


async def get_cache(key: str) -> Any | None:
    try:
        data = await redis_client.get(key)

        if data is None:
            return None

        return json.loads(data)

    except RedisError:
        return None


async def set_cache(
    key: str,
    value: Any,
    expire: int = 300,
) -> None:
    try:
        await redis_client.set(
            key,
            json.dumps(value),
            ex=expire,
        )
    except RedisError:
        pass


async def delete_cache(key: str) -> None:
    try:
        await redis_client.delete(key)
    except RedisError:
        pass


async def delete_cache_pattern(pattern: str) -> None:
    try:
        keys = []

        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            await redis_client.delete(*keys)

    except RedisError:
        pass