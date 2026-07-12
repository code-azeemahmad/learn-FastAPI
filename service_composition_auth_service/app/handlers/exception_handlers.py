from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.user import EmailAlreadyExistsException, UserNotFoundException, InvalidCredentialsError


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(request: Request, exc: UserNotFoundException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "UserNotFound",
                "detail": str(exc),
            },
        )

    @app.exception_handler(EmailAlreadyExistsException)
    async def email_exists_handler(request: Request, exc: EmailAlreadyExistsException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "EmailAlreadyExists",
                "detail": str(exc),
            },
        )
    

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "detail": str(exc),
            },
        )