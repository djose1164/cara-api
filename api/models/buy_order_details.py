from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, fields
from api.models.products import ProductSchema
from api.utils.database import db


class BuyOrderDetails(db.Model):
    __tablename__ = "buy_order_details"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    quantity = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    buy_order_id = db.Column(db.Integer, db.ForeignKey("buy_orders.id"), nullable=False)
    product = db.relationship("Product", backref="producto")


class BuyOrderDetailsSchema(SQLAlchemySchema):
    class Meta:
        model = BuyOrderDetails
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)

    quantity = auto_field(required=True)
    product_id = auto_field(load_only=True)
    product = fields.Nested(ProductSchema, dump_only=True)
