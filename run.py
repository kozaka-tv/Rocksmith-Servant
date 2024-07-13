import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from common.enums import Tags
from modules.api import users_api_example
from modules.servant.servant import Servant


@asynccontextmanager
async def start_servant_app(fast_api: FastAPI):
    # noinspection PyAsyncCall
    asyncio.create_task(Servant().run())

    yield
    print('Shutting app server down...')


tags_metadata = [
    {"name": Tags.USERS, "description": "Some user endpoint examples...fake as f"},
    {"name": Tags.GETTERS, "description": "One other way around"},
    {"name": "post methods", "description": "Keep doing this"},
    {"name": "delete methods", "description": "KILL 'EM ALL"},
    {"name": "put methods", "description": "Boring"},
]

app = FastAPI(lifespan=start_servant_app, openapi_tags=tags_metadata)
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
