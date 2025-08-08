"""Chat Models"""

from pydantic import BaseModel

from app.models.base import BaseResponse


############################################################
# Requests
############################################################
class CompletionsRequest(BaseModel):
    query: str
    user_id: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "안녕하세요!",
                    "user_id": "test",
                }
            ]
        }
    }


############################################################
# Responses
############################################################
class CompletionsResponse(BaseResponse):
    data: dict | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {
                        "response": "네 반갑습니다!",
                        "context": [],
                    },
                },
                {
                    "success": False,
                    "message": "ValueError: ...",
                },
            ]
        }
    }
