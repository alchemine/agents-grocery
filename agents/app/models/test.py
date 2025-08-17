"""Test Models"""

from pydantic import BaseModel

from app.models.base import BaseResponse


############################################################
# Requests
############################################################
# Request is not needed
class TestRequest(BaseModel): ...


############################################################
# Responses
############################################################
class TestResponse(BaseResponse):
    data: list[dict]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {
                        "response": "네 반갑습니다!",
                        "context": [],
                    },
                }
            ]
        }
    }
