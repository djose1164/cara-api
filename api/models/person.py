from api.models.address import AddressSchema
from api.models.contact import ContactSchema
from api.utils.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


class Person(db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    forename = db.Column(db.String(32), nullable=False)
    surname = db.Column(db.String(32))
    birthday = db.Column(db.Date)
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"))
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))
    address = db.relationship("Address", backref="contact_address", uselist=False)
    contact = db.relationship("Contact", backref="person", uselist=False)

    @staticmethod
    def find_person_by_id(person_id):
        return db.get_or_404(Person, person_id)



class PersonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        sqla_session = db.session
        load_instance = True

    contact = fields.Nested(ContactSchema)
    birthday = fields.DateTime(allow_none=True)
    address = fields.Nested(AddressSchema, allow_none=True)
