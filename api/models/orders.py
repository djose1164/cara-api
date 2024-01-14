from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE, fields
from api.models.customers import Customer, CustomerSchema
from api.models.inventory import Inventory

from api.utils.database import SantoDomingoDatetime, db
from api.models.payments import PaymentSchema
from api.models.order_details import OrderDetail, OrderDetailSchema
from api.models.order_status import OrderStatusSchema
from api.utils.exceptions import StocksException


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    date = db.Column(db.Date)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    order_status_id = db.Column(
        db.Integer, db.ForeignKey("order_status.id"), nullable=False, default=1
    )
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"))
    payment = db.relationship("Payment", backref="payment", uselist=False)
    order_details = db.relationship("OrderDetail", backref="order_details")
    order_status = db.relationship("OrderStatus", backref="order_status")
    customer = db.relationship("Customer", backref="orders")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def place(self, salesperson_id: int):
        detail: OrderDetail
        for detail in self.order_details:
            self._validate(salesperson_id, detail)
            inventory = Inventory.find_inventory(salesperson_id, detail.product_id)
            inventory.quantity_available -= detail.quantity
            db.session.add(inventory)
            db.session.flush()
        db.session.commit()

    def _validate(self, salesperson_id: int, detail: OrderDetail):
        product_id: int = detail.product_id
        inventory = Inventory.find_inventory(salesperson_id, product_id)

        if not (inventory and inventory.enough_stocks_for(product_id, detail.quantity)):
            raise StocksException(inventory.product.name)

    @classmethod
    def find_order_by_id(cls, order_id: int):
        return cls.query.filter_by(id=order_id).first_or_404()

    @classmethod
    def find_orders_by_customer_id(cls, customer_id: int, filter=None):
        if filter is None:
            return cls.query.filter_by(customer_id=customer_id).all()
        else:
            return cls.query.filter(
                cls.customer_id == customer_id,
                cls.payment.has(payment_status_id=filter),
            ).all()

    @classmethod
    def find_orders_by_status_id(cls, order_status_id: int, admin_id: int):
        if admin_id is None:
            return (
                cls.query.join(Customer)
                .filter(Order.order_status_id == order_status_id)
                .all()
            )

        return (
            cls.query.join(Customer)
            .filter(Customer.admin_id == admin_id)
            .filter(Order.order_status_id == order_status_id)
            .all()
        )

    @staticmethod
    def validate_order(order: dict):
        salesperson_id: int = order.get("salesperson_id")
        if salesperson_id:
            return OrderDetail.validate_admin_order(
                salesperson_id, order["order_details"]
            )

        OrderDetail.validate_customer_order(order["order_details"])


class OrderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        sqla_session = db.session
        include_fk = True

    id = fields.Integer(dump_only=True)
    date = fields.Date(format="%d/%m/%Y")
    customer = fields.Nested(CustomerSchema, exclude=("orders",))
    payment = fields.Nested(PaymentSchema, required=True, unknown=EXCLUDE)
    order_details = fields.List(
        fields.Nested(OrderDetailSchema, exclude=("order_id",), unknown=EXCLUDE)
    )
    order_status = fields.Nested(OrderStatusSchema, dump_only=True)
