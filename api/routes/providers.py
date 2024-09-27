from flask import Blueprint, request
from marshmallow import EXCLUDE
from flask_jwt_extended import jwt_required

from api.utils.database import db
from api.models.providers import Supplier, SupplierCatalog, SupplierCatalogSchema, SupplierSchema
from api.utils.responses import response_with
import api.utils.responses as resp


provider_routes = Blueprint("provider_routes", __name__)


@provider_routes.route("/")
def provider_index():
    fetched = Supplier.query.all()
    providers = SupplierSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"providers": providers})


@provider_routes.route("/", methods=["POST"])
@jwt_required()
def create_provider():
    try:
        data = request.get_json()

        provider = SupplierSchema(unknown=EXCLUDE).load(data, partial=True)
        provider.create()

        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print("While creating provider: ", e)
        return response_with(resp.BAD_REQUEST_400)


@provider_routes.route("/<int:supplier_id>/catalog")
def provider_catalog(supplier_id: int):
    catalog = db.session.execute(
        db.select(SupplierCatalog).filter_by(supplier_id=supplier_id)
    ).scalars()
    return response_with(
        resp.SUCCESS_200,
        value={"catalog": SupplierCatalogSchema(many=True).dump(catalog)},
    )
