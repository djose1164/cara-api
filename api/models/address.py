from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db

class Address(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(64))
    province = db.Column(db.String(64))
    municipality = db.Column(db.String(64))
    street = db.Column(db.String(64))
    house_number = db.Column(db.Integer)


class AddressSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Address
        load_instance = True
        sqla_session = db.session
        
    country = fields.String()
    province = fields.String()
    municipality = fields.String()
    street = fields.String()
    house_number = fields.Integer()
    