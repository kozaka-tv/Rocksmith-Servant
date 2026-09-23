import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import config.log_config
from common.enums import Tags
from modules.api import users_api_example
from modules.servant.servant import Servant
from utils.exceptions import ConfigError

log = logging.getLogger(__name__)

@asynccontextmanager
async def start_servant_app(fast_api: FastAPI):
    # Reuse the pre-initialized Servant, or create one in reload mode
    servant = getattr(fast_api.state, "servant", None)

    if servant is None:
        config.log_config.config()
        servant = Servant()

    servant_task = asyncio.create_task(servant.run())

    try:
        yield
    finally:
        # Stop Servant and wait for its worker threads to finish
        log.info("Shutting down application...")
        servant.stop()
        await servant_task

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
    reload_enabled = os.getenv("UVICORN_RELOAD", "false").lower() == "true"

    if not reload_enabled:
        config.log_config.config()

        # Initialize Servant before Uvicorn to handle configuration errors
        # without triggering Uvicorn's startup traceback
        try:
            app.state.servant = Servant()
        except ConfigError as exc:
            log.error("Application startup failed: %s", exc)
            sys.exit(1)

    try:
        uvicorn.run(
            # Reload requires an import string instead of an application instance
            "run:app" if reload_enabled else app,
            host="127.0.0.1",
            port=8000,
            log_level="debug",
            log_config=None, # Use the application's logging configuration.
            reload=reload_enabled,
        )
    except KeyboardInterrupt:
        pass
