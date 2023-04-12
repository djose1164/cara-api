from flask import Blueprint, request
from flask_jwt_extended import jwt_required

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
    fetched = Customer.query.all()
    fetched = CustomerSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customers": fetched})


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


@info_route.route("/")
def customer_info():
    fetched = PersonInfo.query.all()
    fetched = PersonInfoSchema(only=("customer_id", "name"), many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"customers": fetched})
