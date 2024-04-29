from typing import TYPE_CHECKING
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from api.utils.database import db

from api.models.salesperson import Salesperson

class Organization(db.Model):
    __tablename__ = "organization"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(256))
    short_description = db.Column(db.String(32))
    members = db.relationship("Salesperson", backref="organization")

    def create(self) -> "Organization":
        db.session.add(self)
        db.session.commit()
        return self
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id},name={self.name}, short_description={self.short_description})"


class OrganizationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Organization
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)
    members = fields.List(fields.Nested("SalespersonSchema", only=("user", "id", "salesperson_type")))
