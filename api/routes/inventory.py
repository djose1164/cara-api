from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from api.models.inventory import Inventory, InventorySchema
from api.models.products import ProductSchema
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp

inventory_routes = Blueprint("inventory_routes", __name__)


@inventory_routes.route("/")
@jwt_required()
def index():
    admin_id = request.args.get("admin_id")
    product_id = request.args.get("product_id")
    if admin_id and product_id:
        fetched = Inventory.find_inventory(admin_id=admin_id, product_id=product_id)
        fetched = InventorySchema().dump(fetched)
        return response_with(resp.SUCCESS_200, value={"inventory": fetched})
    elif admin_id:
        fetched = Inventory.find_inventory_by_admin_id(admin_id)
        fetched = InventorySchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"inventory": fetched})
    elif product_id is not None:
        return avaivable_stocks_of(product_id)
        
    return resp.response_with(resp.BAD_REQUEST_400)

@inventory_routes.route("/<int:inventory_id>")
@jwt_required()
def get_inventory(inventory_id: int):
    inventory = Inventory.find_inventory_by_id(inventory_id)
    inventory = InventorySchema().dump(inventory)
    return response_with(resp.SUCCESS_200, value={"inventory": inventory})

@inventory_routes.route("/<int:inventory_id>", methods=["PUT"])
@jwt_required()
def put_inventory(inventory_id: int):
    try:
        data = request.get_json()
        
        inventory: Inventory = Inventory.find_inventory_by_id(inventory_id)
        
        ProductSchema().load(data["product"], instance=inventory.product)
        
        db.session.add(inventory)
        db.session.commit()
        
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)
    

def avaivable_stocks_of(product_id: int):
    inventories = Inventory.query.filter_by(product_id=product_id).all()
    inventories = InventorySchema(exclude=("product",), many=True).dump(inventories)
    return response_with(resp.SUCCESS_200, value={"inventories": inventories})