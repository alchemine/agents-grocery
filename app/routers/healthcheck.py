"""Healthcheck API"""

from fastapi import APIRouter


router = APIRouter(tags=["healthcheck"])


@router.get("")
def healthcheck():
    return {"status": "success"}
