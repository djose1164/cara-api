from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.models.buy_order import BuyOrder, BuyOrderSchema
from api.models.orders import (
    Order,
    OrderQueueEnum,
    OrderSchema,
    OrderQueue,
    OrderQueueSchema,
)
from api.models.order_details import OrderDetailSchema
from api.models.customers import Customer
from api.models.payments import PaymentSchema
from api.utils.exceptions import CustomerNotFound, StocksException
from api.utils.responses import BAD_REQUEST_400, response_with
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
        new_order = Order.new_order_from_json(data)
        print("create_order: before dumping")
        new_order = OrderSchema().dump(new_order)
        print("create_order: after dumping")
        return response_with(resp.SUCCESS_200, value={"order": new_order})
    except StocksException as e:
        print(f"StocksException: {e}")
        db.session.rollback()
        return response_with(
            resp.SERVER_ERROR_404,
            message=e.message,
        )
    except CustomerNotFound as e:
        db.session.rollback()
        return response_with(resp.SERVER_ERROR_404, error=e.to_dict())
    except Exception as e:
        db.session.rollback()
        print(f"Error while creating order: {e.__class__.__name__}: {e}")
        return response_with(resp.INVALID_INPUT_422)


@order_routes.route("/queue")
@jwt_required()
def order_queue():
    salesperson_id = request.args.get("salesperson_id")
    order_id = request.args.get("order_id")
    status_id = request.args.get("status_id")

    if order_id:
        fetched = OrderQueue.get_by_order_id(order_id)
        fetched = OrderQueueSchema().dump(fetched)
        return response_with(resp.SUCCESS_200, value={"order": fetched})
    
    fetched = OrderQueue.get_salesperson_queue(salesperson_id, status_id)
    fetched = OrderQueueSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"orders": fetched})


@order_routes.route("/queue", methods=["POST"])
@jwt_required()
def add_order_to_queue():
    """
    Endpoint called upon customer ordering something.
    """
    try:
        print(request.json)
        order_queue = OrderQueue.get_by_order_id(request.json["order_id"])
        if order_queue is not None and order_queue.salesperson_id is not None:
            return response_with(
                resp.BAD_REQUEST_400, error="The order is already taken"
            )

        # new_order = Order.new_order_from_json(request.json)
        # order_queue = OrderQueue(
        #     order_id=new_order.id,
        #     customer_id=new_order.customer_id,
        #     order_queue_status_id=int(OrderQueueEnum.NoAssigned),
        # )

        # if order.is_taken:
        #     return response_with(resp.SERVER_ERROR_500, message="La orden ya ha sido tomada por otro vendedor.")
        order_queue.set_salesperson_id(request.json["salesperson_id"])
        order_queue.create()
        order_queue_schema = OrderQueueSchema()

        return response_with(
            resp.SUCCESS_201,
            value={"order_queue": order_queue_schema.dump(order_queue)},
        )
    except StocksException as e:
        db.session.rollback()
        print(e)
        return response_with(resp.SERVER_ERROR_404, message=e.message)
    except Exception as e:
        db.session.rollback()
        print(e)
        return response_with(resp.BAD_REQUEST_400)

@order_routes.route("/<int:order_id>/queue", methods=["DELETE"])
@jwt_required()
def abandon_order_queue(order_id):
    order = db.get_or_404(OrderQueue, order_id)
    order.abandon()
    db.session.add(order)
    db.session.commit()
    return response_with(resp.SUCCESS_204)

@order_routes.route("/<int:order_id>/queue", methods=["DELETE"])
@jwt_required()
def delete_order_queue(order_id):
    order = db.session.execute(db.select(Order).filter_by(id=order_id)).scalar_one()
    order.is_taken = False
    db.session.execute(db.delete(OrderQueue).filter_by(order_id=order_id))
    db.session.commit()
    return response_with(resp.SUCCESS_204)


@order_routes.route("/<int:order_id>/queue", methods=["PATCH"])
@jwt_required()
def update_order_queue(order_id):
    try:
        order_queue: OrderQueue = db.session.execute(
            db.select(OrderQueue).filter_by(order_id=order_id)
        ).scalar_one()

        data = request.json
        if data.get("order_queue_status_id"):
            order_queue.order_queue_status_id = data["order_queue_status_id"]
            order_queue.order.place(order_queue.salesperson_id)

        db.session.add(order_queue)
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
    return response_with(resp.SUCCESS_200, value={"order": fetched})
