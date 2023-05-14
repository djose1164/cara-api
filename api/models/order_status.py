from api.utils.database import db

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


class OrderStatus(db.Model):
    __tablename__ = "order_status"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(32), nullable="False", unique=True)
    
    
class OrderStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        sqla_session = db.session
        load_instance = True
        model = OrderStatus
        
    id = auto_field(dump_only=True)
    status = auto_field()
        
