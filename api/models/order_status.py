import enum
from api.utils.database import db

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

class OrderStatusEnum(enum.Enum):
    Pending = 1
    Processing = 2
    Sent = 3
    Delivered = 4
    Canceled = 5
    OnHold = 6

class OrderStatus(db.Model):
    __tablename__ = "order_status"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(32), nullable="False", unique=True)

    @classmethod
    def find_status_by_id(cls, status_id: int):
        return cls.query.filter_by(id=status_id).first_or_404()


class OrderStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        sqla_session = db.session
        load_instance = True
        model = OrderStatus

    id = auto_field(dump_only=True)
    status = auto_field()
