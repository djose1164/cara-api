from api.utils.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

class PaymentDetail(db.Model):
    __tablename__ = "payment_detail"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"))
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

    
class PaymentDetailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentDetail
        sqla_session = db.session
        load_instance = True

    payment = fields.Nested("PaymentSchema", exclude=("payment_details",))
    