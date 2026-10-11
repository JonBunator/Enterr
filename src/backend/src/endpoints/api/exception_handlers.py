from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from utils.exceptions import NotFoundException


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(_request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
        )
