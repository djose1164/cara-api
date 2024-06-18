from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, fields
from api.models.contact import ContactSchema
from api.utils.database import db


class Provider(db.Model):
    __tablename__ = "providers"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"))
    contact = db.relationship("Contact", backref="contact", uselist=False)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class ProviderSchema(SQLAlchemySchema):
    class Meta:
        model = Provider
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    name = auto_field(required=True)
    contact = fields.Nested(ContactSchema)
    
