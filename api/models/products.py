"""
Copyright Cara 2022
"""
from api.utils.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


class Product(db.Model):
    """
    Model class for product.

    Attributes:
        __tablename__ (str): The table for this model.
        id (int): Unique number.
        name (str): Product's name.
        buy_price (int): Price of buy. WHen we buy to our provider.
        sell_price (int): Price of sell. When we sell to our clients.
    """

    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(64))
    buy_price = db.Column(db.Integer, nullable=False)
    sell_price = db.Column(db.Integer, nullable=False)

    def __init__(self, name, description, buy_price, sell_price):
        self.name = name
        self.description = description
        self.buy_price = buy_price
        self.sell_price = sell_price

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_product_by_id(cls, id_):
        return cls.query.filter_by(id=id_).first()

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
    description = fields.String(required=True)
    buy_price = fields.Integer(required=True)
    sell_price = fields.Integer(required=True)
