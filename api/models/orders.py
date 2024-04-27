from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import EXCLUDE, fields
from api.models.customers import Customer, CustomerSchema
from api.models.inventory import Inventory

from api.utils.database import db
from api.models.payments import Payment, PaymentSchema
from api.models.order_details import OrderDetail, OrderDetailSchema
from api.models.order_status import OrderStatusSchema
from api.utils.exceptions import StocksException


class TakenOrder(db.Model):
    __tablename__ = "taken_order"
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), primary_key=True, nullable=False
    )
    salesperson_id = db.Column(
        db.Integer, db.ForeignKey("salesperson.id"), nullable=False, primary_key=True
    )
    is_done = db.Column(db.Boolean, default=False, nullable=False)

    def create(self) -> "TakenOrder":
        db.session.add(self)
        db.session.commit()
        return self


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    date = db.Column(db.Date)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    order_status_id = db.Column(
        db.Integer, db.ForeignKey("order_status.id"), nullable=False, default=1
    )
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())
    is_taken = db.Column(db.Boolean, default=False)
    payment = db.relationship("Payment", backref="payment", uselist=False)
    order_details = db.relationship("OrderDetail", backref="order_details")
    order_status = db.relationship("OrderStatus", backref="order_status")
    customer = db.relationship("Customer", backref="orders")
    queue = db.relationship(
        "TakenOrder",
        backref="order",
        uselist=False,
        primaryjoin="Order.id == TakenOrder.order_id",
    )

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

    def validate_order(self, salesperson_id: int):
        for detail in self.order_details:
            self._validate(salesperson_id, detail)

    def mark_as_delivered(self):
        self.queue.is_done = True
        self.place(self.queue.salesperson_id)

    def _validate(self, salesperson_id: int, detail: OrderDetail):
        product_id: int = detail.product_id
        inventory = Inventory.find_inventory(salesperson_id, product_id)

        if not (inventory and inventory.enough_stocks_for(product_id, detail.quantity)):
            raise StocksException(inventory.product.name)

    @classmethod
    def find_order_by_id(cls, order_id: int) -> "Order":
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
    def find_orders_by_status_id(cls, order_status_id: int, admin_id: int = None):
        if admin_id is None:
            return cls.query.filter(Order.order_status_id == order_status_id).all()

        return (
            cls.query.join(Customer)
            .filter(Customer.admin_id == admin_id)
            .filter(Order.order_status_id == order_status_id)
            .all()
        )

    @classmethod
    def find_orders_by_payment_status_id(cls, payment_status_id: int):
        return (
            cls.query.join(Payment)
            .filter(Payment.payment_status_id == payment_status_id)
            .all()
        )

    @classmethod
    def get_orders_in_queue(cls):
        return (
            cls.query.join(Customer)
            .join(Payment)
            .filter(Customer.salesperson_id == None)
            .all()
        )


class OrderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        sqla_session = db.session
        include_fk = True

    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    customer = fields.Nested(CustomerSchema, exclude=("orders",))
    payment = fields.Nested(PaymentSchema, required=True, unknown=EXCLUDE)
    order_details = fields.List(
        fields.Nested(OrderDetailSchema, exclude=("order_id",), unknown=EXCLUDE)
    )
    order_status = fields.Nested(OrderStatusSchema, dump_only=True)
    queue = fields.Nested(
        "TakenOrderSchema",
        dump_only=True,
        only=("order_id", "salesperson_id", "is_done"),  # Adjust fields as needed
    )


class TakenOrderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TakenOrder
        sqla_session = db.session
        load_instance = True

    order_id = auto_field(required=True)
    salesperson_id = auto_field(required=True)
    is_done = auto_field()
    order = fields.Nested("OrderSchema")
    salesperson = fields.Nested(
        "SalespersonSchema", exclude=("buy_orders", "customers"), dump_only=True
    )
