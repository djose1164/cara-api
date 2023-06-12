from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields

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
    def validate_product_stocks(details: dict):
        for detail in details:
            product: Product = Product.find_product_by_id(detail["product_id"])
            if not product.enough_stocks_for(detail["quantity"]):
                raise StocksException(product.name)


class OrderDetailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderDetail
        load_instance = True
        sqla_session = db.session
        include_fk = True

    product = fields.Nested(
        "ProductSchema",
        only=("name", "sell_price", "image_url", "description"),
        dump_only=True,
    )
