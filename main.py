import logging
import uvicorn
import redis.asyncio as redis

from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import contacts, auth, users


logging.basicConfig(level=logging.ERROR)

app = FastAPI()

origins = ["*"]
methods = ["*"]
headers = ["*"]


app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)


@app.on_event("startup")
async def startup():
    """
    Initializes the Redis connection and FastAPILimiter on application startup.
    """
    r = await redis.Redis(
        host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
    )
    await FastAPILimiter.init(r)


@app.get(
    "/",
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
def read_root():
    """
    Returns the name of application.

    :return: Name of application.
    :rtype: dict
    """
    print("We are in read_root")
    return {"AppName": "Contacts"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
