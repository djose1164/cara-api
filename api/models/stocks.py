from api.utils.database import db

from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field


class Stocks(db.Model):
    __tablename__ = "stocks"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    in_stock = db.Column(db.Integer, nullable=False)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_stocks_by_id(cls, stock_id: int):
        return cls.query.filter_by(id=stock_id).one()

    @property
    def stocks(self):
        return self.in_stock

    @stocks.setter
    def stocks(self, quantity):
        self.in_stock = quantity


class StocksSchema(SQLAlchemySchema):
    class Meta:
        model = Stocks
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    in_stock = auto_field()
