from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import EXCLUDE, fields
from api.models.contact import ContactSchema

from api.utils.database import db


class PersonInfo(db.Model):
    __tablename__ = "person_info"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    forename = db.Column(db.String(32), nullable=False)
    surname = db.Column(db.String(32))
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    contact = db.relationship("Contact", backref="contacto", uselist=False)
    
    def __init__(
        self,
        forename,
        surname,
        contact=None,
        user_id=None,
        customer_id=None
    ):
        self.forename = forename
        self.surname = surname
        self.contact = contact
        self.user_id = user_id
        self.customer_id = customer_id

    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

class PersonInfoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PersonInfo
        sqla_session = db.session
        load_instance = True
        unknown = EXCLUDE


    id = auto_field(dump_only=True)
    name = fields.Function(lambda obj: f"{obj.forename} {obj.surname}", dump_only=True)
    contact = fields.Nested(ContactSchema)
    customer_id = auto_field()
