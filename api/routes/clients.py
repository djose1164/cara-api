from flask import Blueprint, request

from api.models.clients import Client, ClientSchema
import api.utils.responses as resp
from api.utils.responses import response_with

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
        client_schema = ClientSchema()
        client = client_schema.load(data)
        result = client_schema.dump(client.create())
        return response_with(resp.SUCCESS_200, value={"client": result})
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)
