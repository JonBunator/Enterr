import os
from http import HTTPStatus

from flask import Flask, send_file, jsonify
from flask_login import login_user, logout_user, login_required
from pydantic import ValidationError

from dataAccess.data_access import DataAccess
from endpoints.decorators.get_request_validator import validate_get_request
from endpoints.decorators.post_request_validator import validate_post_request, CustomValidationError
from endpoints.models.action_history_model import (
    GetActionHistory,
    AddManualActionHistory,
)
from endpoints.models.api_response_model import ApiGetResponse, ApiPostResponse
from endpoints.models.notification_model import AddNotification, GetNotification
from endpoints.models.other_model import TriggerAutomaticLogin
from endpoints.models.user_login_model import UserLogin, GetUserData
from endpoints.models.website_model import (
    GetWebsite,
    AddWebsite,
    EditWebsite,
    DeleteWebsite,
)


def register_rest_endpoints(app: Flask, data_access: DataAccess):
    @app.route("/api/websites", methods=["GET"])
    @login_required
    @validate_get_request(GetWebsite)
    def get_websites():
        return DataAccess.get_websites()

    @app.route("/api/websites/<int:website_id>", methods=["GET"])
    @login_required
    @validate_get_request(GetWebsite)
    def get_website(website_id: int):
        return DataAccess.get_website(website_id)

    @app.route("/api/websites/add", methods=["POST"])
    @login_required
    @validate_post_request(AddWebsite)
    def add_website(website_request: AddWebsite):
        data_access.add_website(website_request)

    @app.route("/api/websites/edit", methods=["POST"])
    @login_required
    @validate_post_request(EditWebsite)
    def edit_website(website_request: EditWebsite):
        data_access.edit_website(website_request)

    @app.route("/api/websites/delete", methods=["POST"])
    @login_required
    @validate_post_request(DeleteWebsite)
    def delete_website(website_request: DeleteWebsite):
        data_access.delete_website(website_request)

    @app.route("/api/action_history/<int:website_id>", methods=["GET"])
    @login_required
    @validate_get_request(GetActionHistory)
    def get_action_history(website_id: int):
        return DataAccess.get_action_history(website_id)

    @app.route("/api/action_history/manual_add", methods=["POST"])
    @login_required
    @validate_post_request(AddManualActionHistory)
    def add_manual_action_history(action_history_request: AddManualActionHistory):
        data_access.add_manual_action_history(action_history_request)

    @app.route("/api/trigger_login", methods=["POST"])
    @login_required
    @validate_post_request(TriggerAutomaticLogin)
    def trigger_login(login_request: TriggerAutomaticLogin):
        DataAccess.trigger_login(login_request.id)

    @app.route("/api/user/login", methods=["POST"])
    @validate_post_request(UserLogin)
    def login(login_request: UserLogin):
        user = data_access.get_user(login_request.username)
        if user and user.check_password(login_request.password):
            login_user(user)
        else:
            raise CustomValidationError("Invalid username or password")

    @app.route("/api/notifications/add", methods=["POST"])
    @login_required
    @validate_post_request(AddNotification)
    def add_notification(notification_request: AddNotification):
        data_access.add_notification(notification_request)

    @app.route("/api/notifications", methods=["GET"])
    @login_required
    @validate_get_request(GetNotification)
    def get_notifications():
        return DataAccess.get_notifications()

    @app.route("/api/user/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        response = ApiPostResponse(success=True, message="Logout successful")
        return jsonify(response.model_dump()), HTTPStatus.OK

    @app.route("/api/user/data", methods=["GET"])
    @validate_get_request(GetUserData)
    def get_user_data():
        return DataAccess.get_current_user()

    @app.route("/api/screenshot/<string:screenshot_id>", methods=["GET"])
    @login_required
    def get_screenshot(screenshot_id: str):
        dev_mode = os.getenv("FLASK_ENV") != "production"
        if dev_mode:
            path = f"../config/images"
        else:
            path = f"/config/images"
        image_path = os.path.join(path, f"{screenshot_id}.png")

        try:
            if os.path.isfile(image_path):
                return send_file(image_path, mimetype="image/png")
            else:
                response = ApiGetResponse(
                    success=False, message="Image not found", error=""
                )
                return jsonify(response.model_dump()), HTTPStatus.NOT_FOUND
        except Exception as e:
            # Handle general exceptions and return a 500 Internal Server Error response
            response = ApiGetResponse(
                success=False, message="An error occurred", error=str(e)
            )
            return jsonify(response.model_dump()), HTTPStatus.INTERNAL_SERVER_ERROR

