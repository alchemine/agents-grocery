from os import getenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import SERVICE_NAME
from src.common.logger import log_info, log_success
from src.agents.qa_agent import QAAgent
from src.agents.question_generator import QuestionGenerator
from src.agents.bible_chat.qa_agent import QAAgent as BibleChatQAAgent


##################################################
# Lifespan
##################################################
@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    log_info("Starting up...")

    # Initialize agents
    app.state.qa_agent = QAAgent()
    app.state.question_generator = QuestionGenerator()
    app.state.bible_chat_qa_agent = BibleChatQAAgent()
    log_success("Agent initialized.")

    yield

    # on shutdown
    log_info("Shutting down...")

    # Release agents
    del app.state.qa_agent
    del app.state.question_generator
    del app.state.bible_chat_qa_agent
    log_success("All agents resources released.")


##################################################
# FastAPI application
##################################################
tags_metadata = [
    {"name": "healthcheck", "description": "HealthCheck API"},
    {"name": "agents", "description": "Agents API"},
    {"name": "test", "description": "Test API"},
]
application = FastAPI(
    title=SERVICE_NAME,
    version="0.1.1",
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
from app.routers import healthcheck, agents, test


router_infos = [
    (healthcheck.router, "healthcheck"),
    (agents.router, "agents"),
    (test.router, "test"),
]
for router_info in router_infos:
    r = router_info[0]
    t = [router_info[1]]
    p = f"/{router_info[1]}"
    log_success(f'Register router for prefix "{p}"')
    application.include_router(router=r, prefix=p)
