from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from api.models.orders import Order
from api.utils.responses import response_with
import api.utils.responses as resp

status_routes = Blueprint("status_routes", __name__)


@status_routes.route("/<int:order_id>", methods=["PATCH"])
#@jwt_required()
def update_order_status(order_id):
    try:
        fetched: Order = Order.find_order_by_id(order_id)
        data = request.get_json()

        if data.get("status_id") is None:
            return response_with(
                resp.BAD_REQUEST_400, message="Debes proveer un status_id."
            )

        fetched.order_status_id = data["status_id"]
        fetched.create()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
