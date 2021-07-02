from typing import Union

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from nextgen.api.models.reponses import ApiResponse


def create_error_text(error: dict[str, Union[tuple[str, str], str]]) -> str:
    return f"{error['msg'].capitalize()}. Error location: '{error['loc'][0]} -> {error['loc'][1]}' ({error['type']})"


async def api_validation_error_handler(request: Request, ex: RequestValidationError) -> JSONResponse:
    errors = [create_error_text(error) for error in ex.errors()]
    error_response = jsonable_encoder(ApiResponse(errors=errors, success=False))
    return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content=error_response)


async def api_exception_handler(request: Request, ex: HTTPException) -> JSONResponse:
    error_response = jsonable_encoder(ApiResponse(errors=[ex.detail], success=False))
    return JSONResponse(status_code=ex.status_code, content=error_response, headers=ex.headers)
