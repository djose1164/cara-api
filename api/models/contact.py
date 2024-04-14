from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.models.address import AddressSchema
from api.utils.database import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    forename = db.Column(db.String(32), nullable=False)
    surname = db.Column(db.String(32))
    telephone = db.Column(db.String(11), unique=True)
    email = db.Column(db.String(64), unique=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))
    address = db.relationship("Address", backref="contact_address", uselist=False)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class ContactSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Contact
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    address_id = auto_field()
    address = fields.Nested(AddressSchema)
    email = fields.Email(allow_none=True, required=False)
