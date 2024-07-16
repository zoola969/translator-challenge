from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from db import create_schema
from router import translator_router
from system import system_roter


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    await create_schema()
    yield


app = FastAPI(title="Translator challenge", lifespan=lifespan)
app.include_router(translator_router)
app.include_router(system_roter)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        use_colors=True,
    )
