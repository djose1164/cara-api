from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from api.models.products import ProductSchema

from api.models.stocks import StocksSchema
from api.utils.database import db


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), unique=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product = db.relationship("Product", backref="inventory_product")
    stocks = db.relationship("Stocks", backref="inventory_stocks")

    @classmethod
    def find_inventory_by_admin_id(cls, admin_id: int):
        return cls.query.filter_by(admin_id=admin_id).all()

    @classmethod
    def find_inventory(cls, admin_id: int, product_id: int):
        return (
            cls.query.filter_by(admin_id=admin_id)
            .filter_by(product_id=product_id)
            .one_or_none()
        )

    @classmethod
    def find_inventory_by_id(cls, inventory_id: int):
        return cls.query.filter_by(id=inventory_id).one()


class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        sqla_session = db.session

    product = fields.Nested(ProductSchema)
    stocks = fields.Nested(StocksSchema)
