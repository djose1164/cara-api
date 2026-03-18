from enum import IntEnum
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field, load_instance_mixin
from marshmallow import EXCLUDE, fields
from api.models.customers import Customer, CustomerSchema
from api.models.inventory import Inventory

from api.models.price_history import PriceHistory, PriceTypeEnum
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp
from api.models.payments import Payment, PaymentSchema
from api.models.order_details import OrderDetail, OrderDetailSchema
from api.models.order_status import OrderStatusEnum, OrderStatusSchema
from api.utils.exceptions import OrderNotDoneException, StocksException
from api.models.comment import Comment


class OrderComment(db.Model):
    __tablename__ = "order_comment"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    comment = db.relationship(Comment, backref="order_comment")

    def create(self) -> "OrderComment":
        db.session.add(self)
        db.session.commit()
        return self

    @staticmethod
    def fetch_by_order_id(order_id: int):
        query = (
            db.select(Comment)
            .join(OrderComment)
            .filter(OrderComment.order_id == order_id)
        )
        return db.session.execute(query).scalars()


class OrderQueueStatus(db.Model):
    __tablename__ = "order_queue_status"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(25))
    description = db.Column(db.String(255))


class OrderQueueEnum(IntEnum):
    NoAssigned = 1
    Assigned = 2
    Completed = 3
    Cancelled = 4
    Returned = 5
    Refunded = 6


class OrderQueue(db.Model):
    __tablename__ = "order_queue"
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), primary_key=True, nullable=False
    )
    salesperson_id = db.Column(db.Integer, db.ForeignKey("salesperson.id"))
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    order_queue_status_id = db.Column(
        db.Integer,
        db.ForeignKey("order_queue_status.id"),
        nullable=False,
        default=int(OrderQueueEnum.NoAssigned),
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    salesperson = db.relationship("Salesperson", backref="order_queue")

    def create(self) -> "OrderQueue":
        db.session.add(self)
        db.session.commit()
        return self

    def abandon(self):
        self.salesperson_id = None
        self.order_queue_status_id = OrderQueueEnum.NoAssigned

    def set_salesperson_id(self, salesperson_id: int):
        self.salesperson_id = salesperson_id
        self.order_queue_status_id = OrderQueueEnum.Assigned

    # @property
    # def last_comment(self):
    #     query = (
    #         db.select(OrderComment)
    #         .filter_by(order_id=self.order_id)
    #         .order_by(OrderComment.created_at.desc())
    #     )
    #     res = db.session.execute(query).scalar_one_or_none()
    #     return res

    @staticmethod
    def get_queue():
        return Order.get_orders_in_queue()

    @staticmethod
    def get_salesperson_queue(salesperson_id: int = None, status_id: int = None):
        """
        Return any order taken by salesperson. It won't mind whether the order is done or not. Also return any unassigned order.
        """
        query = db.select(OrderQueue)
        if salesperson_id:
            query = query.filter_by(salesperson_id=salesperson_id)
        if status_id:
            query = query.filter_by(order_queue_status_id=status_id)
        return db.session.execute(query).scalars()

    @staticmethod
    def add_order(new_order) -> "OrqueQueue":
        order_queue = OrderQueue(
            order_id=new_order.id,
            customer_id=new_order.customer_id,
            order_queue_status_id=int(OrderQueueEnum.NoAssigned),
        )
        return order_queue.create()

    @staticmethod
    def get_by_order_id(identifier) -> "OrderQueue":
        return db.session.execute(
            db.select(OrderQueue).filter_by(order_id=identifier)
        ).scalar_one_or_none()


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    date = db.Column(db.Date)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    order_status_id = db.Column(
        db.Integer, db.ForeignKey("order_status.id"), nullable=False, default=1
    )
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"))
    last_comment_id = db.Column(db.Integer, db.ForeignKey("order_comment.id"))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())
    payment = db.relationship("Payment", backref="payment", uselist=False)
    order_details = db.relationship("OrderDetail", backref="order_details")
    order_status = db.relationship("OrderStatus", backref="order_status")
    customer = db.relationship("Customer", backref="orders")
    queue = db.relationship(
        "OrderQueue",
        backref="order",
        uselist=False,
        primaryjoin="Order.id == OrderQueue.order_id",
    )
    comments = db.relationship("OrderComment", foreign_keys="[OrderComment.order_id]")
    last_comment = db.relationship("OrderComment", uselist=False, foreign_keys=[last_comment_id])

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

    def validate_order(self, salesperson_id: int):
        for detail in self.order_details:
            self._validate(salesperson_id, detail)

    def mark_as_delivered(self):
        if self.queue is None:
            return
        if OrderStatusEnum(self.order_status_id) != OrderStatusEnum.Delivered:
            raise OrderNotDoneException()

        self.queue.order_queue_status_id = int(OrderQueueEnum.Completed)

    def set_order_details(self, order_deatils: list[dict]):
        for detail in order_deatils:
            price_id: int = PriceHistory.get_latest_by_product_id(
                detail["product_id"], PriceTypeEnum.SELL
            ).id
            detail.update({"order_id": self.id, "price_id": price_id})

        od = OrderDetailSchema(many=True).load(order_deatils)
        self.order_details = od
        print("set_order_details: done")

    def add_to_queue(self):
        return OrderQueue.add_order(self)

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
    def find_orders_by_payment_status_id(cls, payment_status_id):
        return (
            cls.query.join(Payment)
            .filter(Payment.payment_status_id.in_(payment_status_id))
            .all()
        )

    @staticmethod
    def get_orders_in_queue():
        return Order.get_queue_by_salesperson_id()

    @classmethod
    def get_queue_by_salesperson_id(cls, salesperson_id=None):
        return (
            cls.query.join(Customer)
            .filter(Customer.salesperson_id == salesperson_id)
            .all()
        )

    @staticmethod
    def sanity_check(data: dict):
        if data.get("customer") is None:
            return response_with(resp.BAD_REQUEST_400, message="customer is missing.")
        if data.get("products") is None:
            return response_with(resp.BAD_REQUEST_400, message="products is missing.")
        if data.get("pay") is None:
            return response_with(resp.BAD_REQUEST_400, message="pay is missing.")
        if data.get("salesperson") is None:
            return response_with(
                resp.BAD_REQUEST_400, message="salesperson is missing."
            )
        if data.get("orderDate") is None:
            return response_with(resp.BAD_REQUEST_400, message="orderDate is missing.")

    @staticmethod
    def new_order_from_json(data: dict, is_taken: bool = False) -> "Order":
        """
        Creates a new order form json. No furthur stpes are needed to do besides dumping it, if needed.
        This factory takes care of calling place(). And does previous validation as well.
        """
        import pprint

        pprint.pprint(data)
        Order.sanity_check(data)
        customer = data["customer"]
        buyer = Customer.find_by_id(customer["id"])
        if buyer is None:
            return response_with(
                resp.SERVER_ERROR_404, message="No existe ningún cliente con ese ID."
            )

        payment = PaymentSchema().load(data["pay"])

        new_order = Order(customer=buyer, payment=payment, date=data["orderDate"])
        new_order.is_taken = is_taken
        db.session.add(new_order)
        db.session.flush()  # We need to flush before setting the details.

        new_order.set_order_details(data["products"])
        new_order.place(data["salesperson"]["id"])

        new_order.create()
        print("new_order_from_json: done")
        return new_order


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
        "OrderQueueSchema",
        dump_only=True,
        only=(
            "order_id",
            "salesperson_id",
            "order_queue_status_id",
        ),
    )
    comments = fields.List(fields.Nested("OrderCommentSchema", only=("comment",)))


class OrderQueueSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderQueue
        sqla_session = db.session
        load_instance = True

    order_id = auto_field(required=True)
    salesperson_id = auto_field(required=True)
    order_queue_status_id = auto_field()
    order = fields.Nested(
        "OrderSchema", exclude=("order_details.product.price_history",)
    )
    salesperson = fields.Nested(
        "SalespersonSchema",
        exclude=(
            "buy_orders",
            "customers",
            "inventory",
            "user",
            "organization",
            "warehouse",
        ),
        dump_only=True,
    )
    taken = fields.Function(lambda obj: obj.salesperson_id is not None)
    last_comment = fields.String(attribute="order.last_comment.comment.content", dump_only=True)


class OrderQueueStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderQueueStatus
        sqla_session = db.session
        load_instance = True


class OrderCommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrderComment
        sqla_session = db.session
        load_instance = True

    comment = fields.Nested("CommentSchema")
