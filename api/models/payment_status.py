from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.utils.database import db


class PaymentStatus(db.Model):
    __tablename__ = "payment_status"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(8), unique=True, nullable=False)

    @classmethod
    def find_status(cls, status: str):
        return cls.query.filter_by(status=status).one()


class PaymentStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentStatus
        sqla_session = db.session
        load_instance = True
        include_fk = True

    id = auto_field(dump_only=True)
