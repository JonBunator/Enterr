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
