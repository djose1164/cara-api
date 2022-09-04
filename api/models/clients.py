"""
Copyright Cara Daniel Victoriano 20202
"""
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db
from api.models.orders import OrderSchema


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    forename = db.Column(db.String(64), nullable=False)
    surname = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64))
    phone_number = db.Column(db.String(12))
    orders = db.relationship("Order", backref="Client")
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    def __init__(self, forename, surname, address_id, phone_number=None):
        self.forename = forename
        self.surname = surname
        self.address_id = address_id
        self.phone_number = phone_number

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).one()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter(cls.name.like(f"%{name}%")).all()


class ClientSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    forname = fields.String(required=True)
    surname = fields.String(required=True)
    address = fields.String()
    phone_number = fields.String()
    address_id = fields.Integer(required=True)
    orders = fields.Nested(OrderSchema, many=True, only=["id", "date"])
