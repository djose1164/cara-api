from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from api.utils.database import db

class ProductCategory(db.Model):
    __tablename__ = "product_category"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(128))

class ProductCategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductCategory
        load_instance = True
        sqla_session = db.session