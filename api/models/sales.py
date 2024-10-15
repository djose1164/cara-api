from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from api.utils.database import ma
from api.utils.database import db


class SaleItem(db.Model):
    __tablename__ = "sale_item"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey("sale.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(6, 2))


class SaleItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SaleItem
        sqla_session = db.session
        load_instance = True

    product_id = auto_field()


class Sale(db.Model):
    __tablename__ = "sale"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    total_amount = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    sale_items = db.relationship("SaleItem")


class SalesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Sale
        sqla_session = db.session
        load_instance = True

    sale_items = fields.List(fields.Nested(SaleItemSchema))
    customer_id = auto_field()
