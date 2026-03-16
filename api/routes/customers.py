from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func, select

import api.utils.responses as resp
from api.models.customers import (
    Customer,
    CustomerOutstandingOrdersSchema,
    CustomerSchema,
    CustomerSummarySchema,
)
from api.models.orders import Order
from api.models.payments import Payment
from api.models.person import Person, PersonSchema
from api.utils.database import db
from api.utils.responses import response_with

customer_routes = Blueprint("customer_routes", __name__)
info_route = Blueprint("filter_route", __name__, url_prefix="/info")
customer_routes.register_blueprint(info_route)


@customer_routes.route("/")
@jwt_required()
def customer_index():
    admin_id = request.args.get("admin_id") or request.args.get("salesperson_id")
    payment_status_id = [int(arg) for arg in request.args.getlist("payment_status_id")]

    if admin_id:
        admin_id = int(admin_id)
        fetched = Customer.customers_by_admin_id(admin_id)
        if not fetched:
            return response_with(resp.SERVER_ERROR_404)

        fetched = CustomerSchema(many=True, exclude=("orders",)).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"customers": fetched})
    elif payment_status_id:
        query = (
            select(
                Person.forename,
                Person.surname,
                Customer.id.label("customer_id"),
                func.concat(Person.forename + " " + Person.surname).label(
                    "customer_name"
                ),
                func.count(Order.id).label("number_of_orders"),
                func.sum(Payment.amount_to_pay - Payment.paid_amount).label(
                    "total_to_pay"
                ),
            )
            .select_from(Customer)
            .join(Person, Person.id == Customer.person_id)
            .join(Order, Order.customer_id == Customer.id)
            .join(Payment, Order.payment_id == Payment.id)
            .where(Payment.payment_status_id.in_(payment_status_id))
            .group_by(Customer.id)
            .order_by(Person.forename)
        )
        res = db.session.execute(query).mappings().all()
        dumped = CustomerOutstandingOrdersSchema(many=True).dump(res)

        return response_with(resp.SUCCESS_200, {"customers": dumped})

    return response_with(
        resp.BAD_REQUEST_400,
    )


@customer_routes.route("/<int:identifier>")
@jwt_required()
def get_customer(identifier):
    fetched = Customer.find_by_id(identifier)
    fetched = CustomerSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customer": fetched})


@customer_routes.route("/<int:identifier>/summary")
@jwt_required()
def get_customer_summary(identifier):
    fetched = db.session.execute(
        db.select(
            Order,
            Payment.payment_status_id,
            db.func.count(Payment.payment_status_id).label("total"),
        )
        .join(Order.payment)
        .where(Order.customer_id == identifier)
        .group_by(Payment.payment_status_id)
    ).all()

    fetched = CustomerSummarySchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"summary": fetched})


@customer_routes.route("/", methods=["POST"])
@jwt_required()
def create_customer():
    try:
        data = request.get_json()

        customer_schema = CustomerSchema()
        customer = customer_schema.load(data)
        customer.create()

        return response_with(
            resp.SUCCESS_200,
            value={"customer": customer_schema.dump(customer)},
        )
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@customer_routes.route("/<int:customer_id>", methods=["PUT"])
@jwt_required()
def put_customer(customer_id: int):
    try:
        data = request.get_json()

        customer: Customer = Customer.find_by_id(customer_id)
        PersonSchema().load(data, instance=customer.person, partial=True)
        db.session.commit()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return resp.BAD_REQUEST_400


@info_route.route("/")
@jwt_required()
def customers_info():
    salesperson_id = request.args.get("salesperson_id")
    if salesperson_id:
        fetched = Customer.customers_by_admin_id(salesperson_id)
        fetched = CustomerSchema(
            many=True,
            exclude=("contact", "orders"),
        ).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"customers": fetched})

    return response_with(
        resp.BAD_REQUEST_400,
    )


@info_route.route("/<int:customer_id>")
@jwt_required()
def customer_info(customer_id: int):
    fetched = Customer.find_by_id(customer_id).person
    fetched = PersonSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customer": fetched})
