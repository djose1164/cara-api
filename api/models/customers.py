"""
Copyright Cara Daniel Victoriano 2022
"""
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from api.models.person_info import PersonInfoSchema
from api.utils.database import db


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    person_info = db.relationship("PersonInfo", backref="customer", uselist=False)
    

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_id(cls, customer_id):
        return cls.query.get_or_404(customer_id)

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter(cls.name.like(f"%{name}%")).all()
        
    @classmethod
    def customers_by_admin_id(cls, admin_id: int):
        return cls.query.filter_by(admin_id=admin_id).all()

    @classmethod
    def next_id(cls):
        customer = Customer()
        db.session.add(customer)
        db.session.flush()
        return customer.id


class CustomerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)
    person_info = fields.Nested(PersonInfoSchema)
    admin_id = auto_field()
    customer_id = fields.Function(lambda obj: obj.id)
    name = fields.Function(lambda obj: obj.person_info.forename + " " + obj.person_info.surname)