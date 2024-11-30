from functools import wraps
from flask import request, jsonify
from pydantic import ValidationError
from typing import Callable, Type
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus
from endpoints.models.api_response_model import ApiPostResponse


def validate_post_request(request_model: Type[BaseModel]):
    """
    A reusable decorator for validating the post request body using Pydantic and
    returning a standardized JSON response.

    :param request_model: Pydantic model for validating the incoming request
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Validate the request body using the provided Pydantic model
                request_data = request.get_json()
                validated_data = request_model.model_validate(request_data)

                # Call the original route function with validated data
                func(validated_data, *args, **kwargs)

                # Return a 200 OK status code
                response = ApiPostResponse(success=True, message="Operation successful")
                return jsonify(response.model_dump()), HTTPStatus.OK

            except ValidationError as e:
                # In case of validation errors, return a 400 Bad Request response
                response = ApiPostResponse(success=False, message="Invalid request data", error=str(e))
                return jsonify(response.model_dump()), HTTPStatus.BAD_REQUEST
            except SQLAlchemyError as e:
                # In case of sql error
                response = ApiPostResponse(success=False, message="SQL error", error=str(e))
                return jsonify(response.model_dump()), HTTPStatus.INTERNAL_SERVER_ERROR
            except  Exception as e:
                # Handle general exceptions and return a 500 Internal Server Error response
                response = ApiPostResponse(success=False, message="An error occurred", error=str(e))
                return jsonify(response.model_dump()), HTTPStatus.INTERNAL_SERVER_ERROR

        return wrapper

    return decorator
