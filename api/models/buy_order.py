from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import EXCLUDE, fields
from api.models.buy_order_details import BuyOrderDetailsSchema
from api.models.payments import PaymentSchema
from api.models.providers import ProviderSchema
from api.utils.database import db


class BuyOrder(db.Model):
    __tablename__ = "buy_orders"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date)
    description = db.Column(db.String(255))
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id"))
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    order_details = db.relationship("BuyOrderDetails", backref="order_details")
    provider = db.relationship("Provider", backref="provider")
    payment = db.relationship("Payment", backref="payment_")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class BuyOrderSchema(SQLAlchemySchema):
    class Meta:
        model = BuyOrder
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)
    date = fields.Date(format="%d/%m/%Y")
    description = auto_field()
    provider_id = auto_field(load_only=True)
    provider = fields.Nested(ProviderSchema, dump_only=True)
    admin_id = auto_field(load_only=True)
    payment = fields.Nested(PaymentSchema)
    order_details = fields.Nested(BuyOrderDetailsSchema, many=True, unknown=EXCLUDE)
