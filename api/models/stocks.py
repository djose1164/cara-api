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
        
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_stocks_by_product_id(cls, product_id: int):
        return cls.query.filter_by(product_id=product_id).one()
    
    @property
    def stocks(self):
        return self.in_stock

    @stocks.setter
    def stocks(self, quantity):
        self.in_stock += quantity
        self.create()
        


class StocksSchema(SQLAlchemySchema):
    class Meta:
        model = Stocks
        sqla_session = db.session
        load_instance = True

    in_stock = auto_field()
    product_id = auto_field()
