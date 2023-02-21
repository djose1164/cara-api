from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.models.customers import Customer, CustomerSchema
from api.models.address import AddressSchema
from api.models.person_info import PersonInfoSchema, PersonInfo
from api.models.orders import Order
from api.models.payments import Payment
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

customer_routes = Blueprint("customer_routes", __name__)
filter_route = Blueprint("filter_route", __name__, url_prefix="/filter")
customer_routes.register_blueprint(filter_route)


@customer_routes.route("/", strict_slashes=False)
@jwt_required()
def customer_index():
    fetched = PersonInfo.query.all()
    fetched = PersonInfoSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customers": fetched})


@customer_routes.route("/<identifier>")
def get_customer(identifier):
    if identifier.isdecimal():
        fetched = Customer.find_by_id(identifier)
        fetched = CustomerSchema().dump(fetched)
    else:
        fetched = Customer.find_by_name(identifier)
        fetched = CustomerSchema(many=True).dump(fetched)
    if fetched is None:
        return response_with(resp.SERVER_ERROR_404)
    return response_with(resp.SUCCESS_200, value={"customer": fetched})


@customer_routes.route("/", methods=["POST"])
@jwt_required()
def create_customer():
    try:
        customer = CustomerSchema().load({})
        db.session.add(customer)
        db.session.flush()
    except Exception as e:
        print(e)
        db.session.rollback()
        return response_with(resp.INVALID_INPUT_422)
    else:
        try:
            data = request.get_json()

            address_data = data.pop("address")
            address = AddressSchema().load(address_data)

            db.session.add(address)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()
            return response_with(resp.INVALID_INPUT_422)
        else:
            try:
                data.update({"address_id": address.id})
                data.update({"customer_id": customer.id})

                person_info = PersonInfoSchema().load(data)

                db.session.add(person_info)
                db.session.flush()
            except Exception as e:
                print(e)
                return response_with(resp.INVALID_INPUT_422)
            else:
                db.session.commit()
                return response_with(resp.SUCCESS_200)


@filter_route.route("/", methods=["POST"])
@jwt_required()
def filter_bills_by():
    data = request.get_json()

    if data.get("filter_by") is None:
        return response_with(
            resp.INVALID_INPUT_422, message="Necesitas especificar un tipo de orden."
        )
    elif not data.get("order_by"):
        return response_with(
            resp.BAD_REQUEST_400,
            message="Necesitas especifar segun que se deberia ordenar.",
        )

    fetched = Customer.filter_by_payment_status(data["status"])

    customers = CustomerSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"customers": customers})
