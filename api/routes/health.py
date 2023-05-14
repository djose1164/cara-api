from flask import Blueprint

import api.utils.responses as resp
from api.utils.responses import response_with


health_routes = Blueprint("health_routes", __name__)

health_routes.route("/")


def status():
    return response_with(resp.SUCCESS, value={"status": OK})
