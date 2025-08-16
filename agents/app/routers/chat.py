from fastapi import APIRouter, Request

from app.models.chat import CompletionsRequest, CompletionsResponse
from src.common.logger import log_error


router = APIRouter(tags=["chat"])


@router.post(
    "/completions",
    response_model=CompletionsResponse,
    description="Chat",
)
async def completions(
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
