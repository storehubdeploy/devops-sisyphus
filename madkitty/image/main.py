from fastapi import FastAPI, Body
import uvicorn
import aioredis
import json
import os
from fastapi.exceptions import HTTPException

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

app = FastAPI(docs_url="/api/v1/open",
              title="Mad Kitty",
              version="1.0")


class Redis:
    _redis = None

    async def open(self):
        if not self._redis:
            self._redis = await aioredis.create_redis_pool((os.getenv('REDIS_HOST'), 6379),
                                                           db=int(os.getenv('REDIS_DB')),
                                                           password=os.getenv('REDIS_PASSWORD'),
                                                           encoding='utf-8')
            return self._redis

    async def close(self):
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()


async def set_value(key, value):
    r = await Redis().open()
    await r.set(key, json.dumps(value))
    await r.get(key)
    # val = await r.get(key)
    # print(val)
    await Redis().close()


async def put_value(key, value_new):
    r = await Redis().open()
    value_old = await r.get(key)
    value = {**json.loads(value_old), **value_new}
    await set_value(key, value)
    await Redis().close()


async def get_value(key):
    r = await Redis().open()
    value = await r.get(key)
    await Redis().close()
    return value


@app.get("/{env}/{service}")
async def fetch(env, service):
    key = f"{env}:{service}"
    value = await get_value(key)
    if value:
        return json.loads(value)
    else:
        raise HTTPException(
            status_code=404,
            detail="Key doesn't exists"
        )


@app.post("/{env}/{service}")
async def create(*, env, service, password, value: dict = Body(...)):
    if password == os.getenv('SECRET_KEY'):
        key = f"{env}:{service}"
        return await set_value(key, value)
    else:
        raise HTTPException(
            status_code=401,
            detail="Token Invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.put("/{env}/{service}")
async def modify(*, env, service, password, value: dict = Body(...)):
    if password == os.getenv('SECRET_KEY'):
        key = f"{env}:{service}"
        return await put_value(key, value)
    else:
        raise HTTPException(
            status_code=401,
            detail="Token Invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


if __name__ == '__main__':
    uvicorn.run(app=app,
                host="0.0.0.0",
                port=80)
