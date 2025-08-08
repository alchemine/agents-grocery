"""Base Models"""

from pydantic import BaseModel


############################################################
# Responses
############################################################
class BaseResponse(BaseModel):
    success: bool
    message: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                },
                {
                    "success": False,
                    "message": "ValueError: ...",
                },
            ]
        }
    }
