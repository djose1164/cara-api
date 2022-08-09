from flask import Blueprint, request

from api.models.orders import Order, OrderSchema
from api.utils.responses import response_with
import api.utils.responses as resp

order_routes = Blueprint("order_routes", __name__)

@order_routes.route("/"):
def order_index():
    fetched = Order.query.all()
    print(f"fetched: {fetched}")
    fetched = OrderSchema().dump(fetched, many=True)
    print(f"fetched: {fetched}")    
    return response_with(resp.SUCCESS_200, value={"orders": fetched})