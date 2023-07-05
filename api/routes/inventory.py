from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from api.models.inventory import Inventory, InventorySchema
from api.models.products import ProductSchema
from api.models.stocks import StocksSchema
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp

inventory_routes = Blueprint("inventory_routes", __name__)


@inventory_routes.route("/")
#@jwt_required()
def index():
    admin_id = request.args.get("admin_id")
    if admin_id:
        fetched = Inventory.find_inventory_by_admin_id(admin_id)
        fetched = InventorySchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"inventory": fetched})
        
    return resp.response_with(resp.BAD_REQUEST_400)


@inventory_routes.route("/<int:inventory_id>", methods=["PUT"])
#@jwt_required()
def put_inventory(inventory_id: int):
    try:
        data = request.get_json()
        
        inventory: Inventory = Inventory.find_inventory_by_id(inventory_id)
        
        ProductSchema().load(data["product"], instance=inventory.product)
        StocksSchema().load(data["stocks"], instance=inventory.stocks)
        
        db.session.add(inventory)
        db.session.commit()
        
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)