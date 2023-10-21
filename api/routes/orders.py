from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import EXCLUDE
from api.models.buy_order import BuyOrder, BuyOrderSchema
from api.models.inventory import Inventory

from api.models.orders import Order, OrderSchema
from api.models.order_details import OrderDetail
from api.models.customers import Customer
from api.models.person_info import PersonInfo
from api.models.products import Product
from api.utils.exceptions import InventoryNotFoundException, StocksException
from api.utils.responses import response_with
import api.utils.responses as resp
from api.utils.database import db

order_routes = Blueprint("order_routes", __name__)


@order_routes.route("/")
@jwt_required()
def order_index():
    customer_id = request.args.get("customer_id")
    status_id: int = request.args.get("status_id")
    admin_id: int = request.args.get("admin_id")
    if customer_id:
        customer_id = int(customer_id)
        fetched = Order.find_orders_by_customer_id(customer_id)
        fetched = OrderSchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"orders": fetched})
    elif status_id is not None:
        fetched = Order.find_orders_by_status_id(status_id, admin_id)
        fetched = OrderSchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"orders": fetched})

    fetched = Order.query.all()
    fetched = OrderSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"orders": fetched})


@order_routes.route("/", methods=["POST"])
@jwt_required()
def create_order():
    try:
        data = request.get_json()
        print(data)
        was_new, customer_id = new_customer_if_zero(data)

        if data.get("details"):
            data["order_details"] = data.pop("details")

        Order.validate_order(data)

        order: Order = OrderSchema(unknown=EXCLUDE).load(data)
        order.payment.set_payment_status()
        order.create()

        return (
            response_with(resp.SUCCESS_200)
            if not was_new
            else response_with(resp.SUCCESS_200, value={"customer_id": customer_id})
        )
    except StocksException as e:
        print(e)
        db.session.rollback()
        return response_with(
            resp.SERVER_ERROR_404,
            message=e.message,
        )
    except Exception as e:
        print(f"Error while creating order: {e}")
        return response_with(resp.INVALID_INPUT_422)


def new_customer_if_zero(data):
    if int(data.get("customer_id")) == 0:
        person_info = PersonInfo.find_by_id(data["user_id"])

        person_info.customer_id = customer_id = Customer.next_id()
        data["customer_id"] = customer_id
        return True, customer_id
    return False, None


@order_routes.route("/buy/", methods=["POST"])
@jwt_required()
def create_buy_order():
    try:
        data = request.get_json()

        details_data = data["order_details"]

        buy_order: BuyOrder = BuyOrderSchema().load(data)
        buy_order.payment.set_payment_status()

        for detail in details_data:
            inventory = Inventory.find_inventory(data["admin_id"], detail["product_id"])
            inventory.quantity_available += detail["quantity"]

            db.session.add(inventory)
            db.session.flush()

        buy_order.create()
        return response_with(
            resp.SUCCESS_200, value={"buy_order": BuyOrderSchema().dump(buy_order)}
        )
    except InventoryNotFoundException as e:
        for detail in details_data:
            Inventory.add_product(
                e.product_id,
                e.admin_id,
            )
        buy_order.create()
        return response_with(
            resp.SUCCESS_200, value={"buy_order": BuyOrderSchema().dump(buy_order)}
        )
    except Exception as e:
        print(e)
        db.session.rollback()
        return response_with(resp.BAD_REQUEST_400)


@order_routes.route("/buy/<int:admin_id>")
@jwt_required()
def buy_orders(admin_id):
    fetched = BuyOrder.query.filter_by(admin_id=admin_id).all()
    fetched = BuyOrderSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"orders": fetched})


@order_routes.route("/<int:id>")
@jwt_required()
def get_order_by_id(id):
    fetched = Order.query.filter_by(id=id).first_or_404()
    fetched = OrderSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"order": fetched})
