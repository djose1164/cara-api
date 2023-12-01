from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from api.models.contact import ContactSchema

from api.models.customers import Customer, CustomerSchema
from api.models.address import AddressSchema

import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

customer_routes = Blueprint("customer_routes", __name__)
info_route = Blueprint("filter_route", __name__, url_prefix="/info")
customer_routes.register_blueprint(info_route)


@customer_routes.route("/")
@jwt_required()
def customer_index():
    admin_id = request.args.get("admin_id")
    if admin_id:
        admin_id = int(admin_id)
        fetched = Customer.customers_by_admin_id(admin_id)
        fetched = CustomerSchema(
            many=True,
        ).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"customers": fetched})

    return response_with(
        resp.BAD_REQUEST_400,
    )


@customer_routes.route("/<int:identifier>")
@jwt_required()
def get_customer(identifier):
    fetched = Customer.find_by_id(identifier)
    fetched = CustomerSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customer": fetched})


@customer_routes.route("/", methods=["POST"])
@jwt_required()
def create_customer():
    try:
        data = request.get_json()
        if not data["contact"]["address"]["house_number"]:
            del data["contact"]["address"]["house_number"]
        customer_schema = CustomerSchema()
        customer = customer_schema.load(data)
        customer.create()

        return response_with(
            resp.SUCCESS_200,
            value={
                "customer": {
                    "name": f"{customer.contact.forename} {customer.contact.surname}",
                    "customer_id": customer.id,
                }
            },
        )
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@customer_routes.route("/<int:customer_id>", methods=["PUT"])
@jwt_required()
def put_customer(customer_id: int):
    try:
        data = request.get_json()

        address_data = data["contact"].pop("address")
        customer: Customer = Customer.find_by_id(customer_id)
        address = customer.contact.address
        customer.contact.address = AddressSchema().load(address_data, instance=address)

        contact_data = data.pop("contact")
        contact = customer.contact
        customer.contact = ContactSchema().load(
            contact_data, instance=contact, partial=True
        )

        customer.contact = ContactSchema().load(data, instance=customer.contact)
        customer.create()

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
            exclude=("contact",),
        ).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"customers": fetched})

    return response_with(
        resp.BAD_REQUEST_400,
    )


@info_route.route("/<int:customer_id>")
@jwt_required()
def customer_info(customer_id: int):
    fetched = Customer.find_by_id(customer_id).contact
    fetched = ContactSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customer": fetched})
