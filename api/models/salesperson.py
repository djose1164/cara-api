from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from sqlalchemy import func
from api.models.buy_order import BuyOrderSchema
from api.models.customers import CustomerSchema
from api.models.inventory import InventorySchema
from api.utils.database import db
from api.models.salesperson_types import SalespersonTypesSchema


class SalespersonCredit(db.Model):
    __tablename__ = "salesperson_credit"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    salesperson_id = db.Column(
        db.Integer, db.ForeignKey("salesperson.id"), nullable=False
    )
    credit_increase = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


class SalespersonCreditSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SalespersonCredit
        load_instance = True
        sqla_session = db.session

    salesperson = fields.Nested("SalespersonSchema", exclude=("salesperson_credit", ))


class Salesperson(db.Model):
    __tablename__ = "salesperson"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    salesperson_type_id = db.Column(db.Integer, db.ForeignKey("salesperson_types.id"))
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    credit_limit = db.Column(db.Integer, nullable=False, default=1_000)
    credit_available = db.Column(db.Integer, nullable=False, default=1_000)
    credit_consumed = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    salesperson_type = db.relationship("SalespersonTypes", backref="salesperson_type")
    buy_orders = db.relationship("BuyOrder", backref="salesperson")
    inventory = db.relationship("Inventory", backref="salesperson")
    warehouse = db.relationship("Warehouse", backref="salesperson", uselist=False)
    customers = db.relationship("Customer", backref="salesperson")
    salesperson_credit = db.relationship(SalespersonCredit, backref="salesperson")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def is_associate(self) -> bool:
        return self.salesperson_type_id == 2

    def is_admin(self) -> bool:
        return self.salesperson_type_id == 1

    @classmethod
    def get_by_id(cls, id_: int) -> "Salesperson":
        return cls.query.filter_by(id=id_).one_or_404()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.all()


class SalespersonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Salesperson
        load_instance = True
        sqla_session = db.session

    salesperson_type_id = auto_field()
    admin_id = auto_field()
    user = fields.Nested("UserSchema", exclude=("salesperson",))
    admin_warehouse = fields.Nested("AdminWarehouseSchema")
    salesperson_type = fields.Nested(SalespersonTypesSchema)
    warehouse = fields.Nested("WarehouseSchema", exclude=("salesperson",))
    buy_orders = fields.Nested(BuyOrderSchema, exclude=("salesperson",), many=True)
    inventory = fields.Nested("InventorySchema", exclude=("salesperson",), many=True)
    customers = fields.Nested(CustomerSchema, many=True)
    salesperson_credit = fields.Nested(SalespersonCreditSchema, many=True, exclude=("salesperson",))