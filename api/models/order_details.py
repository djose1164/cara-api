from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from api.models.inventory import Inventory
from api.models.stocks import Stocks

from api.utils.database import db
from api.models.products import Product
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
    def validate_product_stocks(details: dict, admin_id: int):
        for detail in details:
            inventory: Inventory = Inventory.find_inventory(
                admin_id, detail["product_id"]
            )
            product: Product = Product.find_product_by_id(detail["product_id"])
            if inventory is None:
                raise StocksException(product.name)
            stocks: Stocks = inventory.stocks
            quantity: int = detail["quantity"]
            if not stocks.enough_stocks_for(quantity):
                raise StocksException(product.name)
            else:
                inventory.stocks.in_stock -= quantity
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
