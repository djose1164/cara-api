from flask import Blueprint, request

from api.models.clients import Client, ClientSchema
from api.models.address import AddressSchema
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

client_routes = Blueprint("client_routes", __name__)


@client_routes.route("/")
def client_index():
    fetched = Client.query.all()
    fetched = ClientSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"clients": fetched})


@client_routes.route("/<identifier>")
def get_client(identifier):
    if identifier.isdecimal():
        fetched = Client.find_by_id(identifier)
        fetched = ClientSchema().dump(fetched)
    else:
        fetched = Client.find_by_name(identifier)
        fetched = ClientSchema(many=True).dump(fetched)
    if fetched is None:
        return response_with(resp.SERVER_ERROR_404)
    return response_with(resp.SUCCESS_200, value={"client": fetched})


@client_routes.route("/", methods=["POST"])
def create_client():
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
            client = ClientSchema().load(data)
            db.session.add(client)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()
            return response_with(resp.INVALID_INPUT_422)
        else:
            db.session.commit()
            return response_with(resp.SUCCESS_200)
