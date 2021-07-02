from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError

from nextgen.api.utils import api_exception_handler, api_validation_error_handler


app = FastAPI()

app.add_exception_handler(HTTPException, api_exception_handler)
app.add_exception_handler(RequestValidationError, api_validation_error_handler)


@app.get("/api/ping")
async def ping() -> str:
    return "pong"
