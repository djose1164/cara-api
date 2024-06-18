"""
Copyright Cara Daniel Victoriano 2022
"""
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from werkzeug.exceptions import NotFound


from api.models.person import Person, PersonSchema
from api.utils.database import db
from api.utils.exceptions import CustomerNotFound


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    salesperson_id = db.Column(
        db.Integer, db.ForeignKey("salesperson.id")
    )
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    person = db.relationship("Person", backref="customer")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

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
            cls.query.join(Person)
            .filter(Customer.salesperson_id == salesperson_id)
            .order_by(Person.forename, Person.surname)
            .all()
        )
    
    @property
    def forename(self):
        return self.person.forename
    
    @property
    def surname(self):
        return self.person.surname
    

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
    person = fields.Nested(PersonSchema)
    name = fields.Function(lambda obj: obj.person.forename + " " + obj.person.surname)
    orders = fields.Nested("OrderSchema", many=True, exclude=("customer",))
    forename = fields.String(attribute="person.forename")
    surname = fields.String(attribute="person.surname")


class CustomerSummarySchema(Schema):
    payment_status_id = fields.Integer()
    total = fields.Integer()
