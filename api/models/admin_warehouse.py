from api.utils.database import db
from api.models.warehouse import Warehouse, WarehouseSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


class AdminWarehouse(db.Model):
    __tablename__ = "admin_warehouse"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    warehouse = db.relationship("Warehouse", backref="admin_warehouse")

    @staticmethod
    def get_warehouse_by_admin_id(admin_id: int) -> Warehouse:
        return db.first_or_404(
            db.select(Warehouse)
            .join(AdminWarehouse)
            .filter(AdminWarehouse.admin_id == admin_id)
        )


class AdminWarehouseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AdminWarehouse
        load_instance = True
        sqla_session = db.session

    warehouse = fields.Nested(WarehouseSchema)
