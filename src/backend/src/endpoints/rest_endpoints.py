from flask import Flask
from endpoints.decorators.get_request_validator import validate_get_request
from endpoints.decorators.post_request_validator import validate_post_request
from endpoints.models.website_model import GetWebsite, AddWebsite, EditWebsite
from database.database import Website, db

def register_rest_endpoints(app: Flask):
    @app.route('/api/websites', methods=['GET'])
    @validate_get_request(GetWebsite)
    def get_websites():
        return Website.query.all()


    @app.route('/api/websites/add', methods=['POST'])
    @validate_post_request(AddWebsite)
    def add_website(website_request: AddWebsite):
        website = website_request.to_sql_model()
        db.session.add(website)
        db.session.commit()

    @app.route('/api/websites/edit', methods=['POST'])
    @validate_post_request(EditWebsite)
    def edit_website(website_request: EditWebsite):
        edit_id = website_request.id
        existing_website = Website.query.get(edit_id)
        website_request.edit_existing_model(existing_website)
        db.session.commit()