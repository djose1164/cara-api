from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from api.models.payment_detail import PaymentDetailSchema
from api.models.payment_status import PaymentStatusSchema

from api.utils.database import db


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_status_id = db.Column(db.Integer, db.ForeignKey("payment_status.id"))
    paid_amount = db.Column(db.Integer, default=0)
    amount_to_pay = db.Column(db.Integer, default=0)
    updated_at = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )
    status = db.relationship("PaymentStatus", backref="payment")
    payment_details = db.relationship("PaymentDetail", backref="payment")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_id(cls, id_) -> "Payment":
        return cls.query.filter_by(id=id_).first_or_404()

    def is_paid(self) -> bool:
        return self.amount_to_pay == self.paid_amount

    def is_unpaid(self) -> bool:
        return self.paid_amount == 0

    def set_payment_status(self, status_id=None):
        if status_id is not None:
            self.payment_status_id = status_id
            return

        if self.is_paid():
            self.payment_status_id = 1
        elif self.is_unpaid():
            self.payment_status_id = 2
        else:
            self.payment_status_id = 3

    def update_paid_amount(self):
        self.paid_amount = self.calculate_paid_amount()

    def calculate_paid_amount(self):
        return sum(d.amount for d in self.payment_details)


class PaymentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        load_instance = True
        sqla_session = db.session
        include_fk = True

    id = auto_field(dump_only=True)
    status = fields.Nested(PaymentStatusSchema)
    payment_details = fields.List(
        fields.Nested(PaymentDetailSchema, exclude=("payment",))
    )

