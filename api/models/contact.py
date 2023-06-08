from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, fields
from api.models.address import AddressSchema
from api.utils.database import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    telephone = db.Column(db.String(11), unique=True)
    email = db.Column(db.String(64), unique=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class ContactSchema(SQLAlchemySchema):
    class Meta:
        model = Contact
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    telephone = auto_field()
    email = auto_field()
    address = fields.Nested(AddressSchema)
