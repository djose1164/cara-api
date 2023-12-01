from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from api.models.buy_order import BuyOrder, BuyOrderSchema
from api.models.customers import CustomerSchema
from api.models.inventory import Inventory, InventorySchema
from api.models.products import Product

from api.models.salesperson import Salesperson, SalespersonCredit, SalespersonSchema

from api.models.users import User, UserSchema
from api.utils.responses import response_with
import api.utils.responses as resp
from api.utils.database import db


salesperson_routes = Blueprint("salesperson_routes", __name__)


@salesperson_routes.route("/")
@jwt_required()
def get_associate_salesperson():
    fetched = Salesperson.query.all()
    fetched = SalespersonSchema(
        many=True, exclude=("admin_warehouse", "warehouse", "buy_orders", "inventory")
    ).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"salespersons": fetched})


@salesperson_routes.route("/<int:identifier>")
@jwt_required()
def get_salesperson(identifier: int):
    fetched = Salesperson.get_by_id(identifier)
    fetched = SalespersonSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"salesperson": fetched})


@salesperson_routes.route("/<int:identifier>/buy_orders")
@jwt_required()
def get_buy_orders(identifier):
    fetched = Salesperson.get_by_id(identifier)
    fetched = BuyOrderSchema(many=True).dump(fetched.buy_orders)
    return response_with(resp.SUCCESS_200, value={"buy_orders": fetched})


@salesperson_routes.route("/<int:identifier>/customers")
@jwt_required()
def get_customers(identifier: int):
    fetched = Salesperson.get_by_id(identifier)
    fetched = CustomerSchema(many=True).dump(fetched.customers)
    return response_with(resp.SUCCESS_200, value={"customers": fetched})

@salesperson_routes.route("/<int:identifier>/associated")
@jwt_required()
def get_associated(identifier: int):
    user_id = Salesperson.get_by_id(identifier).user_id
    fetched = SalespersonSchema(many=True).dump(Salesperson.get_by_user_id(user_id))
    return response_with(resp.SUCCESS_200, value={"customers": fetched})


@salesperson_routes.route("/<int:identifier>/buy_orders", methods=["POST"])
@jwt_required()
def create_buy_order(identifier):
    try:
        data = request.json
        fetched = Salesperson.get_by_id(identifier)
        total_amount: int = data.pop("total_amount")
        if fetched.is_associate() and total_amount > fetched.credit_available:
            return response_with(
                resp.SERVER_ERROR_500,
                message="No cuentas con crédito suficiente para esta compra.",
            )

        for detail in data["order_details"]:
            inventory = Inventory.find_inventory(identifier, detail["product_id"])
            if inventory is None:
                inventory = add_product(detail["product_id"], identifier)
            inventory.quantity_available += detail["quantity"]
            db.session.add(inventory)
            db.session.flush()
            print("inventory flushed")

        if fetched.is_associate():
            fetched.credit_consumed += total_amount
            fetched.credit_available -= total_amount

        buy_order_schema = BuyOrderSchema()
        buy_order: BuyOrder = buy_order_schema.load(data)
        buy_order.payment.set_payment_status()
        buy_order.salesperson = fetched

        buy_order = buy_order_schema.dump(buy_order.create())
        return response_with(resp.SUCCESS_200, value={"buy_order": buy_order})
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


def add_product(product_id: int, salesperson_id: int):
    product = Product.find_product_by_id(product_id)
    salesperson = Salesperson.get_by_id(salesperson_id)
    warehouse = salesperson.warehouse

    inventory = Inventory(warehouse=warehouse, product=product, salesperson=salesperson)
    return inventory.create()


@salesperson_routes.route("/<int:identifier>/inventory")
@jwt_required()
def get_inventory(identifier):
    fetched = Salesperson.get_by_id(identifier)
    fetched = BuyOrderSchema(many=True).dump(fetched.buy_orders)
    return response_with(resp.SUCCESS_200, value={"buy_orders": fetched})


@salesperson_routes.route("/", methods=["POST"])
@jwt_required()
def create_associate_salesperson():
    try:
        data = request.get_json()
        import pprint

        pprint.pprint(data)
        if data.get("user") is None:
            return response_with(resp.INVALID_INPUT_422, message="user is missing.")
        if data["user"].get("contact") is None:
            return response_with(resp.INVALID_INPUT_422, message="contact is missing.")

        data["user"]["password"] = User.generate_hash(data["user"]["password"])

        salespersonSchema = SalespersonSchema()
        salesperson: Salesperson = salespersonSchema.load(data)
        salesperson.credit_available = salesperson.credit_limit
        salesperson.create()

        fetched = salespersonSchema.dump(salesperson)
        return response_with(resp.SUCCESS_200, value={"salesperson": fetched})
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@salesperson_routes.route("/<int:salesperson_id>", methods=["PATCH"])
@jwt_required()
def patch_salesperson(salesperson_id: int):
    try:
        data = request.json
        print(data)
        salesperson: Salesperson = Salesperson.get_by_id(salesperson_id)

        if data.get("credit_available"):
            salesperson.credit_available = data["credit_available"]
        if data.get("credit_limit"):
            cl = data["credit_limit"]
            salesperson.credit_limit = cl
            salesperson.credit_available = cl - salesperson.credit_consumed
            db.session.add(SalespersonCredit(credit_increase=cl, salesperson=salesperson))
        if data.get("credit_consumed"):
            salesperson.credit_consumed = data["credit_consumed"]
        if data.get("salesperson_type_id"):
            salesperson.salesperson_type_id = data["salesperson_type_id"]
        if data.get("user_id"):
            salesperson.user_id = data["user_id"]

        db.session.add(salesperson)
        db.session.commit()
        return response_with(resp.SUCCESS_204)
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400, message=e)
