import os
from http import HTTPStatus

from flask import Flask, send_file, abort, jsonify
from sqlalchemy.exc import SQLAlchemyError

from dataAccess.data_access import DataAccess
from endpoints.decorators.get_request_validator import validate_get_request
from endpoints.decorators.post_request_validator import validate_post_request
from endpoints.models.action_history_model import GetActionHistory
from endpoints.models.api_response_model import ApiGetResponse
from endpoints.models.website_model import GetWebsite, AddWebsite, EditWebsite, DeleteWebsite


def register_rest_endpoints(app: Flask, data_access: DataAccess):
    @app.route('/api/websites', methods=['GET'])
    @validate_get_request(GetWebsite)
    def get_websites():
        return DataAccess.get_all_websites()

    @app.route('/api/websites/add', methods=['POST'])
    @validate_post_request(AddWebsite)
    def add_website(website_request: AddWebsite):
        data_access.add_website(website_request)

    @app.route('/api/websites/edit', methods=['POST'])
    @validate_post_request(EditWebsite)
    def edit_website(website_request: EditWebsite):
        data_access.edit_website(website_request)

    @app.route('/api/websites/delete', methods=['POST'])
    @validate_post_request(DeleteWebsite)
    def delete_website(website_request: DeleteWebsite):
        data_access.delete_website(website_request)

    @app.route('/api/action_history/<int:website_id>', methods=['GET'])
    @validate_get_request(GetActionHistory)
    def get_action_history(website_id: int):
        website = DataAccess.get_website(website_id)
        if website is None:
            raise SQLAlchemyError('Website with id does not exist.')
        return DataAccess.get_action_history(website)

    @app.route('/api/screenshot/<string:screenshot_id>', methods=['GET'])
    def get_screenshot(screenshot_id):
        dev_mode = os.getenv('FLASK_ENV') != 'production'
        if dev_mode:
            path = f"../config/images"
        else:
            path = f"/config/images"
        image_path = os.path.join(path, f"{screenshot_id}.png")

        try:
            if os.path.isfile(image_path):
                return send_file(image_path, mimetype='image/png')
            else:
                response = ApiGetResponse(success=False, message="Image not found", error="")
                return jsonify(response.model_dump()), HTTPStatus.NOT_FOUND
        except Exception as e:
            # Handle general exceptions and return a 500 Internal Server Error response
            response = ApiGetResponse(success=False, message="An error occurred", error=str(e))
            return jsonify(response.model_dump()), HTTPStatus.INTERNAL_SERVER_ERROR

