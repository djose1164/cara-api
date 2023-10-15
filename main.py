import json
import os
import logging
import sys

from flask import Flask, send_from_directory, make_response
from flask_jwt_extended import JWTManager
import flask_monitoringdashboard as dashboard
from flask_sock import Sock

from api.routes.users import user_routes
from api.routes.products import product_routes
from api.routes.orders import order_routes
from api.routes.order_details import order_detail_routes
from api.routes.payments import payment_routes
from api.routes.customers import customer_routes
from api.routes.customers_rating import rating_routes
from api.routes.order_status import status_routes
from api.routes.health import health_routes
from api.routes.providers import provider_routes
from api.routes.statistics import statistics_routes
from api.routes.inventory import inventory_routes
from api.routes.product_category import category_routes
from api.routes.address import address_routes
from api.config.config import ProductionConfig, TestingConfig, DevelopmentConfig
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

app = Flask(__name__, static_url_path="", static_folder="frontend")
dashboard.bind(app)

match os.environ.get("WORK_ENV"):
    case "PROD":
        app_config = ProductionConfig
    case "TEST":
        app_config = TestingConfig
    case _:
        app_config = DevelopmentConfig

app.config.from_object(app_config)
jwt = JWTManager(app)
sock = Sock(app)

app.register_blueprint(user_routes, url_prefix="/api/users")
app.register_blueprint(product_routes, url_prefix="/api/products")
app.register_blueprint(order_routes, url_prefix="/api/orders")
app.register_blueprint(order_detail_routes, url_prefix="/api/order_details")
app.register_blueprint(customer_routes, url_prefix="/api/customers")
app.register_blueprint(payment_routes, url_prefix="/api/payments")
app.register_blueprint(rating_routes, url_prefix="/api/rating")
app.register_blueprint(health_routes, url_prefix="/api/health")
app.register_blueprint(status_routes, url_prefix="/api/statuses")
app.register_blueprint(provider_routes, url_prefix="/api/providers")
app.register_blueprint(statistics_routes, url_prefix="/api/statistics")
app.register_blueprint(inventory_routes, url_prefix="/api/inventory")
app.register_blueprint(category_routes, url_prefix="/api/products/categories")
app.register_blueprint(address_routes, url_prefix="/api/address")


@app.route("/")
def index():
    response = make_response(send_from_directory(app.static_folder, "Cara.html"), 200)
    return response


@app.after_request
def add_header(response):
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


@jwt.unauthorized_loader
def expired_token_callback(jwt_header):
    return resp.response_with(resp.UNAUTHORIZED_401)


@sock.route("/echo")
def echo(ws):
    while True:
        data = ws.receive()
        print(f"socket's data: {json.loads(data)}")
        ws.send(data)


db.init_app(app)
with app.app_context():
    db.create_all()

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s|%(message)s",
    level=logging.DEBUG,
)

if __name__ == "__main__":
    app.run(debug=True)
