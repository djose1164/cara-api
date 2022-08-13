from flask import request, Blueprint

from api.models.order_details import OrderDetailSchema, OrderDetail
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

order_detail_routes = Blueprint("order_detail_routes", __name__)

@order_detail_routes.route("/", methods=["POST"])
def create_order_detail():
    try:
        data = request.get_json()
        schema = OrderDetailSchema(many=True)
        details = schema.load(data)
        db.session.add_all(details)
        db.session.commit()
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)