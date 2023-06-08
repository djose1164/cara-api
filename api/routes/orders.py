from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import EXCLUDE
from api.models.buy_order import BuyOrder, BuyOrderSchema

from api.models.orders import Order, OrderSchema
from api.models.order_details import OrderDetailSchema, OrderDetail
from api.models.payments import PaymentSchema, Payment
from api.models.customers import Customer
from api.models.person_info import PersonInfo
from api.models.products import Product
from api.models.stocks import Stocks
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
        customer_id: int = None

        if int(data.get("customer_id")) == 0:
            person_info = PersonInfo.find_by_id(data["user_id"])

            person_info.customer_id = customer_id = Customer.next_id()
            data["customer_id"] = customer_id
            was_new = True

        keys = ["customer_id"]
        if data.get("date"):
            keys.append("date")

        order = OrderSchema().load({key: data[key] for key in keys})
        db.session.add(order)
        db.session.flush()
    except Exception as e:
        print(f"Error while creating order: {e}")
        db.session.rollback()
        return response_with(resp.INVALID_INPUT_422)
    else:
        try:
            if data["payment"] is None:
                return response_with(
                    resp.INVALID_INPUT_422, message="El pago debe ser añadido."
                )

            details = data["details"]
            payment = Payment(
                paid_amount=data["payment"]["paid_amount"], order_id=order.id
            )
            for detail in details:
                quantity: int = detail["quantity"]
                product = Product.find_product_by_id(detail["product_id"])
                if product.stock.in_stock - quantity >= 0:
                    payment.amount_to_pay += product.sell_price
                    add_details(product, quantity, order)
                else:
                    return response_with(
                        resp.SERVER_ERROR_404,
                        message="No se encuentran suficientes cantidades en inventario.",
                    )

            db.session.add(product)
            db.session.add(payment)
            db.session.flush()

        except Exception as e:
            print(f"Error while creating order's details & payment: {e}")
            db.session.rollback()
            return response_with(resp.INVALID_INPUT_422)
        else:
            db.session.commit()
        return (
            response_with(resp.SUCCESS_200)
            if not was_new
            else response_with(resp.SUCCESS_200, value={"customer_id": customer_id})
        )


def add_details(product, quantity, order):
    product.stock.in_stock -= quantity

    order_details = OrderDetail(order_id=order.id, quantity=quantity)
    order_details.product = product
    db.session.add(order_details)
    db.session.flush()

    order.order_details.append(order_details)


@order_routes.route("/buy/", methods=["POST"])
# @jwt_required()
def create_buy_order():
    try:
        data = request.get_json()

        payment_data = data.pop("payment")
        payment = PaymentSchema().load(payment_data)
        payment.create()

        data["payment_id"] = payment.id
        details_data = data['order_details']

        buy_order: BuyOrder = BuyOrderSchema(unknown=EXCLUDE).load(data)
        buy_order.create()
        
        print(details_data)
        for detail in details_data:
            print(detail["product_id"])
            stock: Stocks = Stocks.find_stocks_by_product_id(detail["product_id"])
            stock.stocks = detail["quantity"]

        return response_with(resp.SUCCESS_200, value={"buy_order": BuyOrderSchema().dump(buy_order)})
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@order_routes.route("/buy/")
# @jwt_required()
def buy_orders():
    fetched = BuyOrder.query.all()
    fetched = BuyOrderSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"orders": fetched})


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
