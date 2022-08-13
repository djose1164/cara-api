from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer, nullable=False, default=0)
    paid_amount = db.Column(db.Integer, default=0)
    amount_to_pay = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)

    def __init__(self, status, paid_amount, amount_to_pay):
        self.status = status
        self.paid_amount = paid_amount
        self.amount_to_pay = amount_to_pay

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class PaymentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    status = fields.Integer(required=True)
    paid_amount = fields.Integer()
    amount_to_pay = fields.Integer(required=True)
    order_id = fields.Integer(required=True)
