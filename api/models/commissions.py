from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, post_dump

from api.models.price_history import PriceHistory, PriceTypeEnum
from api.utils.database import db


class CommissionItem(db.Model):
    __tablename__ = "commission_item"
    id: int = db.Column(db.Integer, primary_key=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    commission_id = db.Column(
        db.Integer, db.ForeignKey("commission.id"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_commission = db.Column(db.Numeric(6, 2))
    supplier_id: int = db.Column(db.Integer, db.ForeignKey("providers.id"))
    product = db.relationship("Product")


class CommissionItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CommissionItem
        load_instance = True
        sqla_session = db.session

    product_id = auto_field()
    quantity = auto_field()
    image_url = fields.String(dump_only=True)
    product = fields.Nested("ProductSchema", exclude=("price_history", "category",))

    @post_dump
    def add_image_url(self, data, **kwargs):
        product = data.get("product")
        if product and "images" in product and product["images"]:
            data["image_url"] = product["images"][0]["image_url"]
        return data


class Commission(db.Model):
    __tablename__ = "commission"
    id: int = db.Column(db.Integer, primary_key=True, nullable=False)
    rate: float = db.Column(db.Numeric(4, 2), nullable=False)
    amount: float = db.Column(db.Numeric(6, 2))
    payment_date = db.Column(db.DateTime)
    admin_id: int = db.Column(db.Integer, db.ForeignKey("users.id"))
    salesperson_id: int = db.Column(db.Integer, db.ForeignKey("salesperson.id"))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    commission_items = db.relationship("CommissionItem")
    salesperson = db.relationship("Salesperson")
    admin = db.relationship("User")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def calculate_unit_commission(self):
        for item in self.commission_items:
            product_id = item.product_id
            item.unit_commission = PriceHistory.get_latest_price(
                product_id, PriceTypeEnum.SELL
            ) - PriceHistory.get_latest_price(product_id, PriceTypeEnum.BUY)


class CommissionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Commission
        sqla_session = db.session
        load_instance = True

    commission_items = fields.List(
        fields.Nested(CommissionItemSchema)
    )
    salesperson = fields.Nested(
        "SalespersonSchema",
        exclude=("user", "warehouse", "buy_orders", "customers", "inventory"),
    )
    admin = fields.Nested(
        "UserSchema",
        exclude=("salesperson", "associated_salesperson", "favorites", "customer"),
    )
    salesperson_id = auto_field()
    admin_id = auto_field()
    payment_date = fields.DateTime(allow_none=True)
