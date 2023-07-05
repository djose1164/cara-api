from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from api.models.contact import ContactSchema

from api.models.customers import Customer, CustomerSchema
from api.models.address import AddressSchema
from api.models.person_info import PersonInfoSchema, PersonInfo
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
            only=("person_info.forename", "person_info.surname", "id", "admin_id"),
        ).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"customers": fetched})

   
    return response_with(resp.BAD_REQUEST_400, )


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
        admin_id = data.pop("admin_id")
        customer = CustomerSchema().load({"person_info": data, "admin_id": admin_id})
        customer.create()

        return response_with(resp.SUCCESS_200)
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
        address = customer.person_info.contact.address
        customer.person_info.contact.address = AddressSchema().load(
            address_data, instance=address
        )

        contact_data = data.pop("contact")
        contact = customer.person_info.contact
        customer.person_info.contact = ContactSchema().load(
            contact_data, instance=contact, partial=True
        )

        customer.person_info = PersonInfoSchema().load(
            data, instance=customer.person_info
        )
        customer.create()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return resp.BAD_REQUEST_400


@info_route.route("/")
@jwt_required()
def customers_info():
    fetched = PersonInfo.query.all()
    fetched = PersonInfoSchema(only=("customer_id", "name"), many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customers": fetched})


@info_route.route("/<int:customer_id>")
@jwt_required()
def customer_info(customer_id: int):
    fetched = Customer.find_by_id(customer_id).person_info
    fetched = PersonInfoSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customer": fetched})
