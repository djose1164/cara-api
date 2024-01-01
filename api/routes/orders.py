from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.models.buy_order import BuyOrder, BuyOrderSchema
from api.models.orders import Order, OrderSchema
from api.models.order_details import OrderDetailSchema
from api.models.customers import Customer
from api.models.payments import PaymentSchema
from api.models.salesperson import Salesperson
from api.utils.exceptions import CustomerNotFound, StocksException
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
        if data.get("customer") is None:
            return response_with(resp.BAD_REQUEST_400, message="customer is missing.")
        if data.get("products") is None:
            return response_with(resp.BAD_REQUEST_400, message="products is missing.")
        if data.get("pay") is None:
            return response_with(resp.BAD_REQUEST_400, message="pay is missing.")
        if data.get("salesperson") is None:
            return response_with(resp.BAD_REQUEST_400, message="salesperson is missing.")

        customer = data["customer"]
        buyer = Customer.find_by_id(customer["id"])
        if buyer is None:
            return response_with(resp.SERVER_ERROR_404, message="No existe ningún cliente con ese ID.")
        
        payment = PaymentSchema().load(data["pay"])

        data["orderDate"] = datetime.strptime(data["orderDate"], "%d/%m/%Y")
        new_order = Order(customer=buyer, date=data["orderDate"], payment=payment)
        db.session.add(new_order)
        db.session.flush()

        _ = [product.update({"order_id": new_order.id}) for product in data["products"]]
        products = OrderDetailSchema(many=True).load(data["products"])
        new_order.order_details = products
        new_order.place(data["salesperson"]["id"])

        new_order = OrderSchema().dump(new_order)
        return response_with(resp.SUCCESS_200, value={"order": new_order})
    except StocksException as e:
        print(f"StocksException: {e}")
        db.session.rollback()
        return response_with(
            resp.SERVER_ERROR_404,
            message=e.message,
        )
    except CustomerNotFound as e:
        return response_with(resp.SERVER_ERROR_404, error=e.to_dict());
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


def process_salesperson_buy_order(salesperson: Salesperson, data):
    if salesperson.credit_available < data["total_amount"]:
        print("No cuentas con suficientes creditos")
        return response_with(
            resp.SERVER_ERROR_404,
            message="No cuentas con suficiente crédito disponible para esta compra.",
        )

    process_order()


def process_admin_buy_order():
    pass


def process_order():
    pass


@order_routes.route("/buy/<int:salesperson_id>")
@jwt_required()
def buy_orders(salesperson_id):
    fetched = BuyOrder.query.filter_by(salesperson_id=salesperson_id).all()
    fetched = BuyOrderSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"orders": fetched})


@order_routes.route("/<int:id>")
@jwt_required()
def get_order_by_id(id):
    fetched = Order.query.filter_by(id=id).first_or_404()
    fetched = OrderSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"order": fetched})
