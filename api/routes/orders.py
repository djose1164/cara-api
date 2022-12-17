from flask import Blueprint, request

from api.models.orders import Order, OrderSchema
from api.models.order_details import OrderDetailSchema
from api.models.payments import PaymentSchema
from api.models.payments import Payment
from api.models.clients import Client
from api.utils.responses import response_with
import api.utils.responses as resp
from api.utils.database import db

filter_route = Blueprint("filter_route", __name__, url_prefix="/filter")
order_routes = Blueprint("order_routes", __name__)
order_routes.register_blueprint(filter_route)


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
        order = OrderSchema().load(_)
        db.session.add(order)
        db.session.flush()
    except Exception as e:
        print(e)
        db.session.rollback()
        return response_with(resp.INVALID_INPUT_422)
    else:
        try:
            details = data["order_details"]
            for detail in details:
                detail.update({"order_id": int(order.id)})
            details = OrderDetailSchema(many=True).load(details)
            db.session.add_all(details)
            db.session.flush()

            payment = data["payment"]
            payment.update({"order_id": int(order.id)})
            payment = PaymentSchema().load(payment)
            db.session.add(payment)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()
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


@order_routes.route("/<name>")
def get_order_by_client(name):
    client = Client.query.filter_by(name=name).first_or_404()
    fetched = Order.query.filter_by(client_id=client.id).first_or_404()
    fetched = OrderSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"order": fetched})


@filter_route.route("/", methods=["POST"])
def filter_bills_by():
    data = request.get_json()
    print("Holalala")

    if not data.get("status"):
        return response_with(
            resp.INVALID_INPUT_422, message="Necesitas especificar un tipo de orden."
        )
    elif not data.get("filter_by"):
        return response_with(
            resp.BAD_REQUEST_400,
            message="Necesitas especifar segun que se deberia ordenar.",
        )
        
    col = getattr(Order, data["filter_by"])
    fetched = Order.query.filter(
        Order.payment.has(Payment.status==data["status"])) \
        .order_by(col).all()
    orders = OrderSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"orders": orders})
