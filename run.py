import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from modules.servant import servant
from common.enums import Tags
from modules.api import users_api_example


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(servant.run())
    yield
    # Add any logs or commands before shutting down.
    print('It is shutting down...')


tags_metadata = [
    {"name": Tags.USERS, "description": "Some user endpoint examples...fake as f"},
    {"name": Tags.GETTERS, "description": "One other way around"},
    {"name": "post methods", "description": "Keep doing this"},
    {"name": "delete methods", "description": "KILL 'EM ALL"},
    {"name": "put methods", "description": "Boring"},
]

app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.include_router(users_api_example.router)


@app.get("/", tags=[Tags.GETTERS])
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}", tags=[Tags.GETTERS])
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=True,
    )
