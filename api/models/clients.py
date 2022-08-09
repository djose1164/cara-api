"""
Copyright Cara Daniel Victoriano 20202
"""
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64))
    phone_number = db.Column(db.String(12))

    def __init__(self, name, address=None, phone_number=None):
        self.name = name
        self.address = address
        self.phone_number = phone_number

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class ClientSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    address = fields.String()
    phone_number = fields.String
