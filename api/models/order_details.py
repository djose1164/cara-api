from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from api.models.inventory import Inventory
from api.models.products import Product

from api.utils.database import db
from api.utils.exceptions import StocksException


class OrderDetail(db.Model):
    __tablename__ = "order_details"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product = db.relationship("Product", backref="product")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    @staticmethod
    def validate_admin_order(salesperson_id: int, details: dict):
        for detail in details:
            product_id: int = detail["product_id"]
            inventory: Inventory = Inventory.find_inventory(salesperson_id, product_id)
            quantity: int = detail["quantity"]

            if inventory and inventory.enough_stocks_for(product_id, quantity):
                inventory.quantity_available -= quantity
                db.session.add(inventory)
                db.session.flush()
            else:
                raise StocksException(inventory.product.name)


    @staticmethod
    def validate_customer_order(details: dict):
        for detail in details:
            product_id: int = detail["product_id"]
            quantity: int = detail["quantity"]
            OrderDetail.validate_across_inventories(product_id, quantity, detail)
                        
        
    @staticmethod
    def validate_across_inventories(product_id: int, required_quantity: int, detail: dict):
        inventories: list[Inventory] = Inventory.find_inventories_with_stocks_for(product_id)
        product_name = Product.find_product_by_id(product_id).name
        for inventory in inventories:
            stock_available = inventory.quantity_available
            if stock_available == 0:
                continue

            if stock_available >= required_quantity:
                inventory.quantity_available -= required_quantity
                detail["warehouse_id"] = inventory.warehouse_id
                db.session.add(inventory)
                db.session.flush()
                break
        else:
            raise StocksException(product_name)

class OrderDetailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderDetail
        load_instance = True
        sqla_session = db.session
        include_fk = True

    product = fields.Nested(
        "ProductSchema",
    )
