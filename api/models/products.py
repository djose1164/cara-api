"""
Copyright Cara 2022
"""

from datetime import datetime, timezone
from api.models.product_category import ProductCategorySchema
from api.utils.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from api.models.price_history import PriceHistory, PriceHistorySchema, PriceTypeEnum
from api.utils.exceptions import ResourceAlreadyExists


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
    category_id = db.Column(
        db.Integer, db.ForeignKey("product_category.id"), nullable=False
    )
    category = db.relationship("ProductCategory", backref="product_category")
    images = db.relationship("ProductImage", backref="product")
    price_history = db.relationship(
        PriceHistory,
        primaryjoin="and_(PriceHistory.product_id==Product.id, PriceHistory.price_type=='sell')",
    )

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def invalidate_current_price(self, price_type: PriceTypeEnum):
        ph: PriceHistory = PriceHistory.get_latest_by_product_id(self.id, price_type)
        ph.thru_date = datetime.now(timezone.utc)

        #self.create()

    def set_current_price(self, new_price: PriceHistory):
        if new_price.price == PriceHistory.get_latest_price(
            self.id, new_price.price_type
        ):
            raise ResourceAlreadyExists("Ya existe una entrada con el mismo precio.")

        if len(self.buy_price_history.all()) > 0:
            self.invalidate_current_price(new_price.price_type)
        self.create()
        self.price_history.append(new_price)
        self.create()

    def get_current_supplier(self):
        return PriceHistory.get_latest_by_product_id(self.id, PriceTypeEnum.BUY)

    @property
    def sell_price(self):
        return PriceHistory.get_latest_price(self.id, PriceTypeEnum.SELL)

    @property
    def price(self):
        for ph in self.price_history:
            if ph.thru_date is None:
                return ph.price

    @property
    def buy_price_history(self):
        return PriceHistory.get_history_by_product_id(self.id, PriceTypeEnum.BUY)

    @classmethod
    def find_product_by_id(cls, id_) -> "Product":
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
    sell_price = fields.Method("get_current_price", dump_only=True)
    price = fields.Method("get_price", dump_only=True)
    category_id = fields.Integer(required=True)
    category = fields.Nested(ProductCategorySchema)
    category_name = fields.Function(lambda obj: obj.category.name, dump_only=True)
    images = fields.List(fields.Nested("ProductImageSchema"))
    price_history = fields.List(fields.Nested("PriceHistorySchema"))
    supplier_catalog = fields.Method("get_current_supplier", dump_only=True)
    buy_price_history = fields.Method("get_buy_price_history", dump_only=True)

    def get_current_price(self, obj: Product):
        return obj.sell_price

    def get_price(self, obj: Product):
        return obj.price

    def get_current_supplier(self, obj: Product):
        return PriceHistorySchema().dump(obj.get_current_supplier())

    def get_buy_price_history(self, obj: Product):
        return PriceHistorySchema(many=True).dump(obj.buy_price_history)
