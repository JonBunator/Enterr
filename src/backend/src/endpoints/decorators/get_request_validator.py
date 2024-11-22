from functools import wraps
from typing import Type, Callable, List

from flask import jsonify
from pydantic import BaseModel, ValidationError

from endpoints.models.api_response_model import ApiGetResponse


def validate_get_request(response_model: Type[BaseModel]):
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
                return jsonify(response.model_dump()), 200

            except Exception as e:
                # Handle general exceptions and return a 500 Internal Server Error response
                response = ApiGetResponse(success=False, message="An error occurred", error=str(e))
                return jsonify(response.model_dump()), 500

        return wrapper

    return decorator
