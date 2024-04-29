"""
Copyright Cara 2022
"""

from api.models.product_category import ProductCategorySchema
from api.utils.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


class ProductImage(db.Model):
    __tablename__ = "product_image"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    image_url = db.Column(db.String(256), default="https://iili.io/HXfzSQj.png")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)


class ProductImageSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductImage
        load_instance = True
        sqla_session = db.session


class Product(db.Model):
    """
    Model class for product.

    Attributes:
        __tablename__ (str): The table for this model.
        id (int): Unique number.
        name (str): Product's name.
        buy_price (int): Price of buy. WHen we buy to our provider.
        sell_price (int): Price of sell. When we sell to our customers.
    """

    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(64))
    buy_price = db.Column(db.Integer, nullable=False)
    sell_price = db.Column(db.Integer, nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("product_category.id"), nullable=False
    )
    category = db.relationship("ProductCategory", backref="product_category")
    images = db.relationship("ProductImage", backref="product")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_product_by_id(cls, id_):
        return cls.query.filter_by(id=id_).one()

    @classmethod
    def find_product_by_name(cls, name):
        return cls.query.filter(cls.name.like(f"%{name}%")).all()


class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String()
    buy_price = fields.Integer(required=True)
    sell_price = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    category = fields.Nested(ProductCategorySchema)
    category_name = fields.Function(lambda obj: obj.category.name, dump_only=True)
    images = fields.List(fields.Nested("ProductImageSchema"))
