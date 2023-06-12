from flask import Blueprint, request
from marshmallow import EXCLUDE

from api.models.providers import Provider, ProviderSchema
from api.utils.responses import response_with
import api.utils.responses as resp


provider_routes = Blueprint("provider_routes", __name__)


@provider_routes.route("/")
def provider_index():
    fetched = Provider.query.all()
    providers = ProviderSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"providers": providers})


@provider_routes.route("/", methods=["POST"])
def create_provider():
    try:
        data = request.get_json()

        provider = ProviderSchema(unknown=EXCLUDE).load(data, partial=True)
        provider.create()
        
        return response_with(resp.SUCCESS_200)        
    except Exception as e:
        print("While creating provider: ", e)
        return response_with(resp.BAD_REQUEST_400)

