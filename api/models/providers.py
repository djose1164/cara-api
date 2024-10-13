from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from api.models.contact import ContactSchema

# from api.models.price_history import PriceHistory, PriceHistorySchema
from api.models.price_history import PriceHistory, PriceTypeEnum
from api.utils.database import db


class Supplier(db.Model):
    __tablename__ = "providers"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"))
    contact = db.relationship("Contact", backref="contact", uselist=False)
    price_history = db.relationship("PriceHistory", backref="supplier", uselist=False)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class SupplierSchema(SQLAlchemySchema):
    class Meta:
        model = Supplier
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    name = auto_field(required=True)
    contact = fields.Nested(ContactSchema)


class SupplierCatalog(db.Model):
    __tablename__ = "supplier_catalog"

    id: int = db.Column(db.Integer, nullable=False, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("providers.id"), nullable=False)
    product = db.relationship("Product", backref="supplier_catalog")
    supplier = db.relationship("Supplier")

    @property
    def price(self):
        return PriceHistory.get_latest_price(
            self.product_id, PriceTypeEnum.BUY, self.supplier_id
        )

    # @staticmethod
    # def get_by_supplier_id(supplier_id: int):
    #     query = db.select(SupplierCatalog).filter_by(supplier_id=supplier_id).order_by(Product.category_id)
    #     fetched = db.session.execute(query).scalars()


class SupplierCatalogSchema(SQLAlchemySchema):
    class Meta:
        model = SupplierCatalog
        sqla_session = db.session
        load_instance = True

    product = fields.Nested("ProductSchema")
    supplier = fields.Nested("SupplierSchema")
    price = fields.Function(lambda obj: obj.price)
    price_history = fields.List(fields.Nested("PriceHistorySchema"))
