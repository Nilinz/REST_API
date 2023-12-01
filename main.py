import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from app.routes import contacts, auth, users
from app.conf.config import settings

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

async def startup():
    """
    Function to be executed on application startup.

    Initializes and connects to the Redis server for rate limiting.

    :return: None
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)

@app.on_event("startup")
async def on_startup():
    """
    Event handler for application startup.

    Calls the startup function to initialize and connect to the Redis server for rate limiting.

    :return: None
    """
    await startup()

@app.get("/")
def read_root():
    """
    Default route to test the application.

    :return: A simple message.
    """
    return {"message": "Hello World"}
