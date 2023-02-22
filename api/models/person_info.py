from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from api.utils.database import db


class PersonInfo(db.Model):
    __tablename__ = "person_info"
    ID = db.Column(db.Integer, primary_key=True, nullable=False)
    forename = db.Column(db.String(32), nullable=False)
    surname = db.Column(db.String(32))
    telephone = db.Column(db.String(11))
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)

    def __init__(
        self,
        forename,
        surname,
        telephone,
        address_id=None,
        user_id=None,
        customer_id=None,
    ):
        self.forename = forename
        self.surname = surname
        self.telephone = telephone
        self.address_id = address_id
        self.user_id = user_id
        self.customer_id = customer_id


class PersonInfoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PersonInfo
        sqla_session = db.session
        load_instance = True

    id = fields.Integer()
    forename = fields.String()
    surname = fields.String()
    telephone = fields.Integer(allow_none=True)
    address_id = fields.Integer()
    user_id = fields.Integer()
    customer_id = fields.Integer()
