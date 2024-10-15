from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import EXCLUDE, fields
from api.models.buy_order_details import BuyOrderDetailsSchema
from api.models.payments import PaymentSchema
from api.models.price_history import PriceHistory, PriceTypeEnum
from api.models.providers import SupplierSchema
from api.utils.database import db


class BuyOrder(db.Model):
    __tablename__ = "buy_orders"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date)
    description = db.Column(db.String(255))
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id"))
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), nullable=False)
    salesperson_id = db.Column(
        db.Integer, db.ForeignKey("salesperson.id"), nullable=False
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    order_details = db.relationship("BuyOrderDetails", backref="order_details")
    provider = db.relationship("Supplier", backref="Supplier")
    payment = db.relationship("Payment", backref="payment_")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def set_price_id(self):
        for detail in self.order_details:
            price = PriceHistory.get_latest_by_product_id(
                detail.product_id, PriceTypeEnum.BUY
            )
            detail.price_id = price.id


class BuyOrderSchema(SQLAlchemySchema):
    class Meta:
        model = BuyOrder
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)
    date = fields.Date()
    description = auto_field()
    provider_id = auto_field(load_only=True)
    provider = fields.Nested(SupplierSchema, dump_only=True)
    salesperson = fields.Nested(
        "SalespersonSchema", exclude=("user", "buy_orders", "customers", "inventory")
    )
    payment = fields.Nested(PaymentSchema)
    order_details = fields.Nested(
        BuyOrderDetailsSchema,
        many=True,
        unknown=EXCLUDE,
        exclude=(
            "product.supplier_catalog",
            "product.buy_price_history",
            "product.price_history",
        ),
    )
