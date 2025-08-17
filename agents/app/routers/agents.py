from fastapi import APIRouter, Request

from app.models.agents import CompletionsRequest, CompletionsResponse
from src.common.logger import log_error


router = APIRouter(tags=["agents"])


@router.post(
    "/qa_agent/completions",
    response_model=CompletionsResponse,
    description="QA Agent Completion",
)
async def qa_agent_completions(
    fastapi_request: Request, request: CompletionsRequest
) -> CompletionsResponse:
    try:
        qa_agent = fastapi_request.app.state.qa_agent
        data = qa_agent.invoke(request.query, request.user_id)
        result = CompletionsResponse(success=True, data=data)
    except Exception as e:
        log_error("Unexpected error occurred.")
        result = CompletionsResponse(success=False, message=str(e))
    return result


@router.post(
    "/question_generator/completions",
    response_model=CompletionsResponse,
    description="Question Generator Completion",
)
async def question_generator_completions(
    fastapi_request: Request, request: CompletionsRequest
) -> CompletionsResponse:
    try:
        question_generator = fastapi_request.app.state.question_generator
        data = question_generator.invoke(request.query, request.user_id)
        result = CompletionsResponse(success=True, data=data)
    except Exception as e:
        log_error("Unexpected error occurred.")
        result = CompletionsResponse(success=False, message=str(e))
    return result


@router.post(
    "/bible_chat/completions",
    response_model=CompletionsResponse,
    description="Bible Chat Completion",
)
async def bible_chat_completions(
    fastapi_request: Request, request: CompletionsRequest
) -> CompletionsResponse:
    try:
        bible_chat_qa_agent = fastapi_request.app.state.bible_chat_qa_agent
        data = bible_chat_qa_agent.invoke(request.query, request.user_id)
        result = CompletionsResponse(success=True, data=data)
    except Exception as e:
        log_error("Unexpected error occurred.")
        result = CompletionsResponse(success=False, message=str(e))
    return result
