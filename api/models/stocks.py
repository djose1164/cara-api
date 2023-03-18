from api.utils.database import db

from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

class Stocks(db.Model):
    __tablename__ = "stocks"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    in_stock = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    def __init__(self, in_stock, product_id):
        self.in_stock = in_stock
        self.product_id = product_id
        

class StocksSchema(SQLAlchemySchema):
    class Meta:
        model = Stocks
        sqla_session = db.session
        load_instance = True
    
    in_stock = auto_field()
    product_id = auto_field()
    