from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from api.models.customers import CustomerSchema
from api.utils.database import db


class CustomersRating(db.Model):
    __tablename__ = "customers_rating"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    review = db.Column(db.String(256))
    posted_date = db.Column(db.DateTime, nullable=False)
    customer = db.relationship("Customer", backref="customer", lazy=True, uselist=False)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_rating_by_customer_id(cls, id_):
        return cls.query.filter_by(customer_id=id_).first_or_none()

    @classmethod
    def get_rating_by_id(cls, rating_id):
        return cls.query.filter_by(id=rating_id).first_or_404()

    @classmethod
    def find_rating(cls, customer_id, product_id):
        return cls.query.filter(
            cls.customer_id == customer_id, cls.product_id == product_id
        ).one_or_none()

    @classmethod
    def find_product_rating(cls, product_id):
        return cls.query.filter_by(product_id=product_id).all()


class CustomersRatingSchema(SQLAlchemySchema):
    class Meta:
        model = CustomersRating
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)
    customer_id = auto_field(required=True)
    product_id = auto_field(required=True)
    rating = auto_field(required=True)
    review = auto_field(nullable=False)
    posted_date = auto_field()
    customer = fields.Nested(CustomerSchema, only=("contact",))
    name = fields.Function(
        lambda obj: f"{obj.customer.contact.forename} {obj.customer.contact.surname}",
        dump_only=True,
    )
