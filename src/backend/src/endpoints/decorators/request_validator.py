from abc import abstractmethod, ABC
from pydantic import BaseModel
from dataAccess.database.database import Base


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
