from flask import Blueprint, request

from api.models.orders import Order, OrderSchema
from api.models.clients import Client
from api.utils.responses import response_with
import api.utils.responses as resp

order_routes = Blueprint("order_routes", __name__)


@order_routes.route("/")
def order_index():
    fetched = Order.query.all()
    fetched = OrderSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"orders": fetched})


@order_routes.route("/", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        order_schema = OrderSchema()
        order = order_schema.load(data)
        result = order_schema.dump(order.create())
        return response_with(resp.SUCCESS_200, value={"order": result})
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@order_routes.route("/<id>")
def get_order_by_id(id):
    if not id.isdecimal():
        return get_order_by_client(id)
    fetched = Order.query.filter_by(id=id).first_or_404()
    fetched = OrderSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"order": fetched})


def get_order_by_client(name):
    client = Client.query.filter_by(name=name).first_or_404()
    fetched = Order.query.filter_by(client_id=client.id).first_or_404()
    fetched = OrderSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"order": fetched})
