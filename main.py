import json
import os
import logging
import pathlib
import sys

from flask import Flask, jsonify, send_from_directory, make_response
from flask_jwt_extended import JWTManager

import flask_monitoringdashboard as dashboard
from flask_restful import Api
from flask_sock import Sock

from api.utils.database import db, ma
from api.routes.users import user_routes
from api.routes.products import product_routes
from api.routes.orders import order_routes
from api.routes.order_details import order_detail_routes
from api.routes.payments import payment_routes
from api.routes.customers import customer_routes
from api.routes.reviews import rating_routes
from api.routes.order_status import status_routes
from api.routes.health import health_routes
from api.routes.providers import provider_routes
from api.routes.statistics import statistics_routes
from api.routes.inventory import inventory_routes
from api.routes.product_category import category_routes
from api.routes.address import address_routes
from api.routes.salesperson import salesperson_routes
from api.config.config import ProductionConfig, TestingConfig, DevelopmentConfig
from api.utils.exceptions import ResourceAlreadyExists
import api.utils.responses as resp
from api.utils.responses import response_with
from api.routes.organization import OrganizationListResource, OrganizationResource
from api.routes.shopping import ShoppingList
from api.routes.contact import ContactList
from api.routes.comments import CommentResource, CommentResourceList
from api.routes.sales import SalesResource, SalesResourceList
from api.routes.commissions import CommissionResource, CommissionResourceList

app = Flask(__name__, static_url_path="", static_folder="frontend")
api = Api(app)

app.config['CORS_HEADERS'] = 'Content-Type'
dashboard.bind(app)

match os.environ.get("WORK_ENV"):
    case "PROD":
        app_config = ProductionConfig
    case "TEST":
        app_config = TestingConfig
    case _:
        app_config = DevelopmentConfig

app.config.from_object(app_config)

# Create upload path if needed.
pathlib.Path(app_config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

jwt = JWTManager(app)
sock = Sock(app)

API_PREFIX: str = "/api"

app.register_blueprint(user_routes, url_prefix="/api/users")
app.register_blueprint(product_routes, url_prefix="/api/products")
app.register_blueprint(order_routes, url_prefix="/api/orders")
app.register_blueprint(order_detail_routes, url_prefix="/api/order_details")
app.register_blueprint(customer_routes, url_prefix="/api/customers")
app.register_blueprint(payment_routes, url_prefix="/api/payments")
app.register_blueprint(rating_routes, url_prefix="/api/reviews")
app.register_blueprint(health_routes, url_prefix="/api/health")
app.register_blueprint(status_routes, url_prefix="/api/statuses")
app.register_blueprint(provider_routes, url_prefix="/api/providers")
app.register_blueprint(statistics_routes, url_prefix="/api/statistics")
app.register_blueprint(inventory_routes, url_prefix="/api/inventory")
app.register_blueprint(category_routes, url_prefix="/api/products/categories")
app.register_blueprint(address_routes, url_prefix="/api/address")
app.register_blueprint(salesperson_routes, url_prefix="/api/salespersons")

api.add_resource(ShoppingList, f"{API_PREFIX}/shopping")
api.add_resource(OrganizationListResource, "/api/organizations/")
api.add_resource(OrganizationResource, "/api/organizations/<int:identifier>")
api.add_resource(ContactList, "/api/contacts")
api.add_resource(CommentResource, "/api/comment/<int:identifier>")
api.add_resource(CommentResourceList, "/api/comments/")
api.add_resource(SalesResource, "/api/sales/<int:sale_id>")
api.add_resource(SalesResourceList, "/api/sales")
api.add_resource(CommissionResource, "/api/commissions/<int:commission_id>")
api.add_resource(CommissionResourceList, "/api/commissions/")


@app.route("/")
def index():
    response = make_response(send_from_directory(app.static_folder, "index.html"), 200)
    return response


@app.after_request
def add_header(response):
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response


@app.errorhandler(400)
def bad_request(e):
    logging.error(e)
    return response_with(resp.BAD_REQUEST_400)


@app.errorhandler(404)
def not_found(e):
    logging.error(e)
    return response_with(resp.SERVER_ERROR_404)


@app.errorhandler(500)
def server_error(e):
    logging.error(e)
    return response_with(resp.SERVER_ERROR_500)


@app.errorhandler(ResourceAlreadyExists)
def resource_already_exists(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# Error handler for expired or invalid JWTs
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "code": "refresh_token_expired",
        "message": "The refresh token has expired. Please log in again."
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({
        "code": "refresh_token_invalid",
        "message": f"Invalid token: {reason}"
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(reason):
    return jsonify({
        "code": "authorization_required",
        "message": f"Token missing: {reason}"
    }), 401


@sock.route("/echo")
def echo(ws):
    while True:
        data = ws.receive()
        print(f"socket's data: {json.loads(data)}")
        ws.send(data)


@app.route("/uploads/<path:name>")
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


db.init_app(app)
ma.init_app(app)
with app.app_context():
    db.create_all()

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s",
    level=logging.DEBUG,
)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
