from flask import Blueprint

from api.models.address import Address, AddressSchema, Country, CountrySchema, Municipality, MunicipalitySchema, Province, ProvinceSchema, Sector, SectorSchema
from api.utils.responses import response_with
import api.utils.responses as resp

address_routes = Blueprint("address_routes", __name__)

@address_routes.route("/")
def index():
    fetched = Address.query.all()
    fetched = AddressSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"address": fetched})

@address_routes.route("/<int:identifier>")
def get_address_by_id(identifier):
    pass

@address_routes.route("/country/")
def get_countries():
    fetched = Country.query.all()
    fetched = CountrySchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"countries": fetched})

@address_routes.route("/country/<int:identifier>/")
def get_provinces(identifier: int):
    fetched = Province.query.all()
    fetched = ProvinceSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"provinces": fetched})

@address_routes.route("/country/<int:country_id>/<int:province_id>/")
def get_municipalities(country_id: int, province_id: int):
    fetched = Municipality.query.all()
    fetched = MunicipalitySchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"municipalities": fetched})

@address_routes.route("/country/<int:country_id>/<int:province_id>/<int:municipality_id>/")
def get_sectors(country_id: int, province_id: int, municipality_id: int):
    fetched = Sector.query.all()
    fetched = SectorSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"sectors": fetched})