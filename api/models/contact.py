from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.utils.database import db


class Contact(db.Model):
    __tablename__ = "contact"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    telephone = db.Column(db.String(11), unique=True)
    homephone = db.Column(db.String(11))
    email = db.Column(db.String(64), unique=True)


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
    email = fields.Email(allow_none=True, required=False)
