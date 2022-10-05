import os
import logging
import sys

from flask import Flask
from flask_jwt_extended import JWTManager

import flask_monitoringdashboard as dashboard

from api.routes.users import user_routes
from api.routes.products import product_routes
from api.routes.orders import order_routes
from api.routes.order_details import order_detail_routes
from api.routes.payments import payment_routes
from api.routes.clients import client_routes
from api.config.config import ProductionConfig, TestingConfig, DevelopmentConfig
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db


app = Flask(__name__)
dashboard.bind(app)

match os.environ.get("WORK_ENV"):
    case "PROD":
        app_config = ProductionConfig
    case "TEST":
        app_config = TestingConfig
    case _:
        app_config = DevelopmentConfig
app.config.from_object(app_config)

app.register_blueprint(user_routes, url_prefix="/api/users")
app.register_blueprint(product_routes, url_prefix="/api/products")
app.register_blueprint(order_routes, url_prefix="/api/orders")
app.register_blueprint(order_detail_routes, url_prefix="/api/order_details")
app.register_blueprint(client_routes, url_prefix="/api/clients")
app.register_blueprint(payment_routes, url_prefix="/api/payments")


@app.route("/")
def index():
    return "<h1>Welcome to Author Manager</h1>"


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


jwt = JWTManager(app)
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
