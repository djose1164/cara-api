"""
Copyright Cara Daniel Victoriano 20202
"""
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from sqlalchemy.orm import contains_eager

from api.utils.database import db
from api.models.orders import OrderSchema, Order
from api.models.payments import Payment
from api.models.person_info import PersonInfoSchema


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    orders = db.relationship("Order", backref="customer", order_by="Order.date")
    person_info = db.relationship("PersonInfo", backref="customer", uselist=False)

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

    @classmethod
    def filter_by_payment_status(cls, status):
        return (
            cls.query.join(cls.orders)
            .join(Order.payment)
            .options(contains_eager(cls.orders))
            .filter_by(status=status)
            .populate_existing()
            .all()
        )


class CustomerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    orders = fields.Nested(OrderSchema, many=True)
    person_info = fields.Nested(PersonInfoSchema)
