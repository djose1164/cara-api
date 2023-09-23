from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from api.models.inventory import Inventory

from api.utils.database import db
from api.utils.exceptions import StocksException


class OrderDetail(db.Model):
    __tablename__ = "order_details"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), unique=True)
    product = db.relationship("Product", backref="product")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @staticmethod
    def validate_product_stocks(details: dict, admin_id: int=None):
        for detail in details:
            product_id: int = detail["product_id"]
            if admin_id is not None:
                inventory: Inventory = Inventory.find_inventory(
                    admin_id, product_id
                )
            else:
                inventories: list[Inventory] = Inventory.find_inventories_with_stocks_for(product_id)
            
            missing_quantity = quantity = detail["quantity"]

            for inventory in inventories:
                stock_available = inventory.quantity_available
                if stock_available == 0:
                    continue

                if stock_available == missing_quantity:
                    inventory.quantity_available = 0
                    break
                elif missing_quantity > stock_available:
                    missing_quantity -= stock_available
                    inventory.quantity_available = 0
                else:
                    inventory.quantity_available -= missing_quantity
                    missing_quantity = 0
                    break
            else:
                product_name = inventory.product.name
                raise StocksException(product_name)

            detail["warehouse_id"] = inventory.warehouse_id
                
            db.session.add(inventory)
            db.session.flush()


class OrderDetailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderDetail
        load_instance = True
        sqla_session = db.session
        include_fk = True

    product = fields.Nested(
        "ProductSchema",
    )
