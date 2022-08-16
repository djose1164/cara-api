from flask import Blueprint, request

from api.models.orders import Order, OrderSchema
from api.models.order_details import OrderDetail, OrderDetailSchema
from api.models.clients import Client
from api.utils.responses import response_with
import api.utils.responses as resp
from api.utils.database import db

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
        keys = ["client_id"]
        if data.get("date"):
            keys.append("date")
        _ = {key: data[key] for key in keys}
        #print("Holala --", data["date"])
        order = OrderSchema().load(_)
        print("---", order.date)
        db.session.add(order)
        db.session.flush()
        
    except Exception as e:
        print(e)
        db.session.rollback()
        return response_with(resp.INVALID_INPUT_422)
    else:
        try:
            data = data["order_details"]
            for detail in data:
                detail.update({"order_id": int(order.id)})
            details = OrderDetailSchema(many=True).load(data)
            db.session.add_all(details)
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            print("#-#-Here", e)
            return response_with(resp.INVALID_INPUT_422)
        else:
            db.session.commit()
            return response_with(resp.SUCCESS_200)

        

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
