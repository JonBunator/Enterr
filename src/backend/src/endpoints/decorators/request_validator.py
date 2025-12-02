from abc import abstractmethod, ABC
from functools import wraps
from typing import Callable
from fastapi import HTTPException
from pydantic import BaseModel
from dataAccess.database.database import Base
import traceback
from utils.exceptions import NotFoundException


class GetRequestBaseModel(BaseModel, ABC):
    @staticmethod
    @abstractmethod
    def from_sql_model(data: Base) -> "GetRequestBaseModel":
        pass


class PostRequestBaseModel(BaseModel, ABC):
    @staticmethod
    @abstractmethod
    def to_sql_model() -> Base:
        pass


def validate_request():
    """
    A reusable decorator for handling requests, ensuring standardized error handling.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Call the original route function (fetch the data)
                return func(*args, **kwargs)

            except NotFoundException as e:
                raise HTTPException(status_code=404, detail=e.message)

            except Exception as e:
                traceback.print_exc()
                # Handle general exceptions
                raise HTTPException(status_code=500, detail="An unkown error occurred")

        return wrapper

    return decorator
