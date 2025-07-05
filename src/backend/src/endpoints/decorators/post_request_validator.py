from abc import ABC, abstractmethod
from pydantic import BaseModel
from dataAccess.database.database import Base


class PostRequestBaseModel(BaseModel, ABC):
    @staticmethod
    @abstractmethod
    def to_sql_model() -> Base:
        pass


class CustomValidationError(Exception):
    pass
