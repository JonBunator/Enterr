from abc import abstractmethod, ABC
from functools import wraps
from typing import Type, Callable, List
from flask import jsonify
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus
from database.database import db
from endpoints.models.api_response_model import ApiGetResponse

class GetRequestBaseModel(BaseModel, ABC):
    @staticmethod
    @abstractmethod
    def from_sql_model(data: db.Model) -> "GetRequestBaseModel":
        pass

def validate_get_request(response_model: Type[GetRequestBaseModel]):
    """
    A reusable decorator for handling GET requests, ensuring standardized error handling
    and response structure.

    :param response_model: Pydantic model for the response
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Call the original route function (fetch the data)
                data = func(*args, **kwargs)

                # Ensure data is iterable (e.g., a list of models)
                if isinstance(data, List):
                    response_data = [response_model.from_sql_model(d) for d in data]
                else:
                    response_data = response_model.from_sql_model(data)

                # Prepare the success response
                response = ApiGetResponse(success=True, message="Operation successful", data=response_data)
                return jsonify(response.model_dump()), HTTPStatus.OK

            except SQLAlchemyError as e:
                # In case of sql error
                response = ApiGetResponse(success=False, message="SQL error", error=str(e))
                return jsonify(response.model_dump()), HTTPStatus.INTERNAL_SERVER_ERROR
            except Exception as e:
                # Handle general exceptions and return a 500 Internal Server Error response
                response = ApiGetResponse(success=False, message="An error occurred", error=str(e))
                return jsonify(response.model_dump()), HTTPStatus.INTERNAL_SERVER_ERROR

        return wrapper

    return decorator
