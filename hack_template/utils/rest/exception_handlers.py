from http import HTTPStatus

from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from hack_template.utils.exceptions import (
    HackTemplateException,
    UserWithUsernameAlreadyExistsException,
)
from hack_template.utils.rest.models import StatusResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return _exception_json_response(status_code=exc.status_code, message=exc.detail)


def user_already_exists_handler(
    request: Request,
    exc: UserWithUsernameAlreadyExistsException,
) -> JSONResponse:
    return _exception_json_response(
        status_code=HTTPStatus.BAD_REQUEST,
        message=exc.message,
    )


def internal_server_error_handler(
    request: Request, exc: HackTemplateException
) -> JSONResponse:
    return _exception_json_response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        message="Unknown internal server error",
    )


def _exception_json_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=StatusResponse(message=message).model_dump(),
    )
