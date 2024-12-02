from flask import Flask
from database.change_database import IDataBase
from endpoints.decorators.get_request_validator import validate_get_request
from endpoints.decorators.post_request_validator import validate_post_request
from endpoints.models.website_model import GetWebsite, AddWebsite, EditWebsite

def register_rest_endpoints(app: Flask):
    @app.route('/api/websites', methods=['GET'])
    @validate_get_request(GetWebsite)
    def get_websites():
        return IDataBase.get_all_websites()

    @app.route('/api/websites/add', methods=['POST'])
    @validate_post_request(AddWebsite)
    def add_website(website_request: AddWebsite):
        IDataBase.add_website(website_request)

    @app.route('/api/websites/edit', methods=['POST'])
    @validate_post_request(EditWebsite)
    def edit_website(website_request: EditWebsite):
        IDataBase.edit_website(website_request)