from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.models.admin_warehouse import AdminWarehouse
from api.models.products import Product, ProductSchema

from api.models.warehouse import WarehouseSchema
from api.utils.database import db
from api.utils.exceptions import InventoryNotFoundException, StocksException


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    quantity_available = db.Column(db.Integer, default=0, nullable=False)
    minimun_stock_level = db.Column(db.Integer, default=5, nullable=False)
    maximun_stock_level = db.Column(db.Integer, default=30, nullable=False)
    reorder_point = db.Column(db.Integer, default=18, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product = db.relationship("Product", backref="inventory_product")
    warehouse = db.relationship("Warehouse", backref="inventory_warehouse")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_inventory_by_admin_id(cls, admin_id: int):
        return cls.query.filter_by(admin_id=admin_id).all()

    @classmethod
    def find_inventory(cls, admin_id: int, product_id: int):
        try:
            return (
                cls.query.filter_by(admin_id=admin_id)
                .filter_by(product_id=product_id)
                .one()
            )
        except Exception:
            raise InventoryNotFoundException(product_id, admin_id)

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

    @classmethod
    def add_product(cls, product_id: int, admin_id: int):
        product = Product.find_product_by_id(product_id)
        warehouse = AdminWarehouse.query.filter_by(admin_id=admin_id).one()

        inventory = InventorySchema().load(
            {
                "product_id": product.id,
                "warehouse_id": warehouse.id,
                "admin_id": admin_id,
            }
        )
        return inventory.create()


class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        sqla_session = db.session

    product_id = auto_field(required=True)
    warehouse_id = auto_field(required=True)
    admin_id = auto_field(required=True)
    product = fields.Nested(ProductSchema)
    warehouse = fields.Nested(WarehouseSchema)
