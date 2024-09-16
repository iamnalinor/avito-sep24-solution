from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import NoResultFound
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .errors import ClientRequestError

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ClientRequestError)
async def exc_400_handler(_: object, exc: ClientRequestError) -> JSONResponse:
    return JSONResponse({"reason": exc.reason}, status_code=exc.status_code)


@app.exception_handler(NoResultFound)
async def not_found_handler(_: object, __: NoResultFound) -> JSONResponse:
    return JSONResponse({"reason": "object not found"}, status_code=404)


@app.exception_handler(RequestValidationError)
async def invalid_schema_handler(
    _: object, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse({"reason": f"validation error: {exc}"}, status_code=400)
