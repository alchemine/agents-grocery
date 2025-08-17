"""Test Endpoints"""

from fastapi import APIRouter, Request

from app.routers import agents
from app.models.agents import CompletionsRequest
from app.models.test import TestResponse


router = APIRouter(tags=["test"])


@router.post("/smoke", response_model=TestResponse)
async def smoke(fastapi_request: Request) -> TestResponse:
    """Request to test smoke endpoints"""
    request_result = []

    request = CompletionsRequest(query="넌 뭘 도와줄 수 있어?", user_id="test")

    # 1. Test /agents/qa_agent/completions
    response = await agents.qa_agent_completions(fastapi_request, request)
    request_result.append(
        {
            "router": "agents",
            "endpoint": "qa_agent/completions",
            "request": request.model_dump(),
            "response": response.model_dump(),
        }
    )

    # 2. Test /agents/question_generator/completions
    response = await agents.question_generator_completions(fastapi_request, request)
    request_result.append(
        {
            "router": "agents",
            "endpoint": "question_generator/completions",
            "request": request.model_dump(),
            "response": response.model_dump(),
        }
    )

    # Check if all requests are successful
    if all(res["response"]["success"] for res in request_result):
        result = TestResponse(success=True, data=request_result)
    else:
        result = TestResponse(
            success=False,
            data=request_result,
            message="Some requests have been failed",
        )
    return result
