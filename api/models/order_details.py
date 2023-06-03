from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db
from api.models.products import Product


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


class OrderDetailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderDetail
        load_instance = True
        sqla_session = db.session

    quantity = fields.Integer(required=True)
    order_id = fields.Integer(required=True)
    product_id = fields.Integer(required=True)
    product = fields.Nested(
        "ProductSchema", only=("name", "sell_price", "image_url", "description")
    )
