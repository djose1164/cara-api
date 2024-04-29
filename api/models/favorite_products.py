from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.utils.database import db

class FavoriteProduct(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product = db.relationship("Product", backref="favorite_product")
    user = db.relationship("User", backref="favorites")

    def create(self) -> "FavoriteProduct":
        db.session.add(self)
        db.session.commit()
        return self


class FavoriteProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FavoriteProduct
        sqla_session = db.session
        load_instance = True

    product_id = auto_field()
    user_id = auto_field()
    