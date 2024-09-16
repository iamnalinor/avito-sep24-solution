from fastapi import APIRouter
from starlette.responses import PlainTextResponse

router = APIRouter()


@router.get("/api/ping")
def ping() -> PlainTextResponse:
    return PlainTextResponse("ok")
