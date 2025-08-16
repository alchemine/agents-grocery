from os import getenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import SERVICE_NAME, SERVICE_VERSION
from src.common.logger import log_info, log_success


##################################################
# Lifespan
##################################################
@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    log_info("Starting up...")

    # Initialize agents
    qa_agent = ...
    app.state.qa_agent = qa_agent
    log_success("Agent initialized.")

    yield

    # on shutdown
    log_info("Shutting down...")

    # Release agents
    del app.state.qa_agent
    log_success("Agent resources released.")


##################################################
# FastAPI application
##################################################
tags_metadata = [
    {"name": "healthcheck", "description": "HealthCheck API"},
    {"name": "chat", "description": "Chat API"},
]
application = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    openapi_tags=tags_metadata,
    root_path=getenv("FASTAPI_ROOT_PATH", None),
    lifespan=lifespan,
)
application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

##################################################
# Error handling
##################################################
from app.errors import *
from app.middlewares import *


##################################################
# Routers
##################################################
from app.routers import healthcheck, chat


router_infos = [
    (healthcheck.router, "healthcheck"),
    (chat.router, "chat"),
]
for router_info in router_infos:
    r = router_info[0]
    t = [router_info[1]]
    p = f"/{router_info[1]}"
    log_success(f'Register router for prefix "{p}"')
    application.include_router(router=r, prefix=p)
