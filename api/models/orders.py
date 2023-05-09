from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db
from api.models.payments import PaymentSchema
from api.models.order_details import OrderDetailSchema
from api.models.order_status import OrderStatusSchema


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    date = db.Column(db.Date, server_default=db.func.now())
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    order_status_id = db.Column(db.Integer, db.ForeignKey("order_status.id"), nullable=False, default=1)
    payment = db.relationship("Payment", backref="payment", uselist=False)
    order_details = db.relationship("OrderDetail", backref="order_details")
    order_status = db.relationship("OrderStatus", backref="order_status")

    def __init__(
        self, customer_id, date=db.func.now(), payments=None, order_details=None
    ):
        if order_details is None:
            order_details = list()
        if payments is None:
            payments = list()
        self.customer_id = customer_id
        self.date = date
        self.payments = payments
        self.order_details = order_details

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class OrderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    date = fields.Date(format="%d/%m/%Y", load_default=db.func.now())
    customer_id = fields.Integer(required=True)
    payment = fields.Nested(
        PaymentSchema, many=False, only=("paid_amount", "amount_to_pay", "status", "id")
    )
    order_details = fields.Nested(OrderDetailSchema, many=True, only=("product", "quantity"))
    order_status = fields.Nested(OrderStatusSchema)
