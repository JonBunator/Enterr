from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

from dataAccess.data_access import DataAccess
from endpoints.decorators.get_request_validator import validate_get_request
from endpoints.decorators.post_request_validator import validate_post_request
from endpoints.models.action_history_model import GetActionHistory
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


