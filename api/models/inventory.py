from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from api.models.products import ProductSchema

from api.models.warehouse import WarehouseSchema
from api.utils.database import db


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    minimun_stock_level = db.Column(db.Integer, default=5, nullable=False)
    maximun_stock_level = db.Column(db.Integer, default=30, nullable=False)
    reorder_point = db.Column(db.Integer, default=18, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), unique=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product = db.relationship("Product", backref="inventory_product")
    warehouse = db.relationship("Warehouse", backref="inventory_warehouse")

    @classmethod
    def find_inventory_by_admin_id(cls, admin_id: int):
        return cls.query.filter_by(admin_id=admin_id).all()

    @classmethod
    def find_inventory(cls, admin_id: int, product_id: int):
        return (
            cls.query.filter_by(admin_id=admin_id)
            .filter_by(product_id=product_id)
            .one_or_none()
        )

    @classmethod
    def find_inventory_by_id(cls, inventory_id: int):
        return cls.query.filter_by(id=inventory_id).one()

    def enough_stocks_for(self, quantity: int) -> bool:
        return self.quantity_available >= quantity

    @classmethod
    def find_inventories_with_stocks_for(cls, product_id: int):
        return (
            cls.query.filter_by(product_id=product_id)
            .filter(Inventory.quantity_available > 0)
            .all()
        )


class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        sqla_session = db.session

    product = fields.Nested(ProductSchema)
    warehouse = fields.Nested(WarehouseSchema)
