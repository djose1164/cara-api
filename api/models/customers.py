"""
Copyright Cara Daniel Victoriano 2022
"""
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.models.contact import Contact
from werkzeug.exceptions import NotFound


from api.utils.database import db
from api.utils.exceptions import CustomerNotFound


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    salesperson_id = db.Column(
        db.Integer, db.ForeignKey("salesperson.id"), nullable=False
    )
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=False)
    contact = db.relationship("Contact", backref="customer")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_id(cls, customer_id) -> "Customer":
        try:
            return cls.query.get_or_404(customer_id)
        except NotFound:
            raise CustomerNotFound(customer_id)

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter(cls.name.like(f"%{name}%")).all()

    @classmethod
    def customers_by_admin_id(cls, salesperson_id: int):
        return (
            cls.query.join(Contact)
            .filter(Customer.salesperson_id == salesperson_id)
            .order_by(Contact.forename, Contact.surname)
            .all()
        )

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
    customer_id = fields.Function(lambda obj: obj.id)
    salesperson_id = auto_field(required=True)
    contact = fields.Nested("ContactSchema")
    name = fields.Function(lambda obj: obj.contact.forename + " " + obj.contact.surname)
    orders = fields.Nested("OrderSchema", many=True, exclude=("customer",))


class CustomerSummarySchema(Schema):
    payment_status_id = fields.Integer()
    total = fields.Integer()
