from api.utils.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class AdminWarehouse(db.Model):
    __tablename__ = "admin_warehouse"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)


class AdminWarehouseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AdminWarehouse
        load_instance = True
        sqla_session = db.session
