from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.models.orders import Order, OrderSchema
from api.models.order_details import OrderDetailSchema
from api.models.payments import PaymentSchema
from api.models.customers import Customer
from api.models.person_info import PersonInfo
from api.models.products import Product
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
