from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer, db.Computed("if((`paid_amount` = `amount_to_pay`),0,if((`paid_amount` > 0),2,1))"))
    paid_amount = db.Column(db.Integer, default=0)
    amount_to_pay = db.Column(db.Integer, default=0)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    def __init__(self, paid_amount, amount_to_pay, order_id):
        self.paid_amount = paid_amount
        self.amount_to_pay = amount_to_pay
        self.order_id = order_id

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    @classmethod
    def find_by_id(cls, id_):
        return cls.query.filter_by(id=id_).first()


class PaymentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    status = fields.Integer(dump_only=True)
    paid_amount = fields.Integer()
    amount_to_pay = fields.Integer(required=True)
    order_id = fields.Integer(required=True)
