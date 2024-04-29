from api.utils.database import db

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


class Warehouse(db.Model):
    __tablename__ = "warehouse"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"), nullable=False)
    address = db.relationship("Address")


class WarehouseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Warehouse
        load_instance = True
        sqla_session = db.session

    salesperson = fields.Nested("SalespersonSchema", exclude=("warehouse",))
    address = fields.Nested("AddressSchema")
    address_name = fields.Method("get_address_name")

    def get_address_name(self, obj):
        if obj.address is None:
            return ""
        return f"{obj.address.country.name}, {obj.address.municipality.name}, {obj.address.sector.name}, {obj.address.street or str()}"
