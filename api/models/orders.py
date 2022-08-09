from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    payment_status = db.Column(db.Integer)
    date = db.Column(db.Date, server_default=db.func.now())
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    
    def __init__(self, payment_status, client_id):
        self.payment_status = payment_status
        self.client_id = client_id
        
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
    payment_status = fields.Boolean(required=True)
    date = fields.Date()
    client_id = fields.Integer(required=True)
        