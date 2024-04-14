from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.models.buy_order import BuyOrder, BuyOrderSchema
from api.models.orders import Order, OrderSchema, TakenOrder, TakenOrderSchema
from api.models.order_details import OrderDetailSchema
from api.models.customers import Customer
from api.models.payments import PaymentSchema
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
    payment_status_id: int = request.args.get("payment_status_id")
    if customer_id:
        customer_id = int(customer_id)
        fetched = Order.find_orders_by_customer_id(customer_id)
        fetched = OrderSchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"orders": fetched})
    elif status_id and admin_id:
        fetched = Order.find_orders_by_status_id(status_id, admin_id)
        fetched = OrderSchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"orders": fetched})
    elif status_id:
        fetched = Order.find_orders_by_status_id(status_id)
        fetched = OrderSchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"orders": fetched})
    elif payment_status_id:
        fetched = Order.find_orders_by_payment_status_id(payment_status_id)
        fetched = OrderSchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"orders": fetched})

    return response_with(resp.BAD_REQUEST_400)


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
            return response_with(
                resp.BAD_REQUEST_400, message="salesperson is missing."
            )

        customer = data["customer"]
        buyer = Customer.find_by_id(customer["id"])
        if buyer is None:
            return response_with(
                resp.SERVER_ERROR_404, message="No existe ningún cliente con ese ID."
            )

        payment = PaymentSchema().load(data["pay"])

        new_order = Order(customer=buyer, payment=payment, date=data.get("date"))
        new_order.is_taken = True
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
        return response_with(resp.SERVER_ERROR_404, error=e.to_dict())
    except Exception as e:
        print(f"Error while creating order: {e}")
        return response_with(resp.INVALID_INPUT_422)


@order_routes.route("/queue")
@jwt_required()
def order_queue():
    fetched = Order.get_orders_in_queue()
    fetched = OrderSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"orders": fetched})


@order_routes.route("/queue", methods=["POST"])
@jwt_required()
def take_order():
    try:
        
        data: dict = request.json
        if data.get("order_id") is None:
            return response_with(resp.INVALID_INPUT_422, message="order_id is missing.")
        if data.get("salesperson_id") is None:
            return response_with(
                resp.INVALID_INPUT_422, message="salesperson_id is missing."
            )

        order = db.get_or_404(Order, data["order_id"])
        print("HOLALA")
        taken_order_schema = TakenOrderSchema()
        taken_order = taken_order_schema.load(data)

        order.is_taken = True
        db.session.add(order)

        taken_order.create()

        return response_with(
            resp.SUCCESS_201,
            value={"taken_order": taken_order_schema.dump(taken_order)},
        )
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@order_routes.route("/<int:order_id>/queue", methods=["DELETE"])
@jwt_required()
def delete_taken_order(order_id):
    order = db.session.execute(db.select(Order).filter_by(id=order_id)).scalar_one()
    order.is_taken = False
    db.session.execute(db.delete(TakenOrder).filter_by(order_id=order_id))
    db.session.commit()
    return response_with(resp.SUCCESS_204)


@order_routes.route("/<int:order_id>/queue", methods=["PATCH"])
@jwt_required()
def update_taken_order(order_id):
    try:
        taken_order: TakenOrder = db.session.execute(
            db.select(TakenOrder).filter_by(order_id=order_id)
        ).scalar_one()

        data = request.json
        if data.get("is_done"):
            taken_order.is_done = data["is_done"]
            taken_order.order.place(taken_order.salesperson_id)

        db.session.add(taken_order)
        db.session.commit()
        return response_with(resp.SUCCESS_204)
    except StocksException as e:
        print(f"StocksException: {e}")
        db.session.rollback()
        return response_with(
            resp.SERVER_ERROR_500,
            message=e.message,
        )
    except Exception as e:
        print(e)
        return response_with(resp.SERVER_ERROR_404)


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
    print(fetched["queue"])
    return response_with(resp.SUCCESS_200, value={"order": fetched})
