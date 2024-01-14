from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.models.products import Product, ProductSchema

from api.models.warehouse import Warehouse, WarehouseSchema
from api.utils.database import db


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    minimum_stock_level = db.Column(db.Integer, default=5, nullable=False)
    maximum_stock_level = db.Column(db.Integer, default=30, nullable=False)
    reorder_point = db.Column(db.Integer, default=18, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    salesperson_id = db.Column(db.Integer, db.ForeignKey("salesperson.id"), nullable=False)
    product = db.relationship("Product", backref="inventory_product")
    warehouse = db.relationship("Warehouse", backref="inventory_warehouse")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_inventory_by_salesperson_id(cls, salesperson_id: int):
        return cls.query.filter_by(salesperson_id=salesperson_id).all()

    @classmethod
    def find_inventory(cls, salesperson_id: int, product_id: int) -> "Inventory":
        return (
            cls.query.filter_by(salesperson_id=salesperson_id)
            .filter_by(product_id=product_id)
            .first()
        )


    @classmethod
    def find_inventory_by_id(cls, inventory_id: int):
        return cls.query.filter_by(id=inventory_id).one()

    def enough_stocks_for(self, product_id:int, quantity: int) -> bool:
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

    product_id = auto_field(required=True)
    warehouse_id = auto_field(required=True)
    salesperson_id = auto_field(required=True)
    salesperson = fields.Nested("SalespersonSchema", exclude=("inventory", "customers", "buy_orders"))
    product = fields.Nested(ProductSchema)
    warehouse = fields.Nested(WarehouseSchema)
