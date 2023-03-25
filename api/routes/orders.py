from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.models.orders import Order, OrderSchema
from api.models.order_details import OrderDetailSchema
from api.models.payments import PaymentSchema
from api.models.payments import Payment
from api.models.customers import Customer, CustomerSchema
from api.models.person_info import PersonInfo, PersonInfoSchema
from api.utils.responses import response_with
import api.utils.responses as resp
from api.utils.database import db

order_routes = Blueprint("order_routes", __name__)


@order_routes.route("/")
@jwt_required()
def order_index():
    fetched = Order.query.all()
    fetched = OrderSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"orders": fetched})


@order_routes.route("/", methods=["POST"])
@jwt_required()
def create_order():
    try:
        data = request.get_json()
        was_new = False

        if int(data.get("customer_id")) == 0:
            person_info = PersonInfo.query.filter_by(user_id=data["user_id"]).first_or_404()
            new_customer = Customer()
            db.session.add(new_customer)
            db.session.flush()
            print("new_customer", new_customer)

            person_info.customer_id = new_customer.id
            data["customer_id"] = new_customer.id
            was_new = True

        keys = ["customer_id"]
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
        return (
            response_with(resp.SUCCESS_200)
            if not was_new
            else response_with(resp.SUCCESS_200, value={"customer_id": new_customer.id})
        )


@order_routes.route("/<int:id>")
@jwt_required()
def get_order_by_id(id):
    if not id.isdecimal():
        return get_order_by_client(id)
    fetched = Order.query.filter_by(id=id).first_or_404()
    fetched = OrderSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"order": fetched})


@order_routes.route("/<name>")
def get_order_by_client(name):
    client = Customer.query.filter_by(name=name).first_or_404()
    fetched = Order.query.filter_by(customer_id=client.id).first_or_404()
    fetched = OrderSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"order": fetched})
