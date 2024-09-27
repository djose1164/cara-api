from datetime import datetime, timezone
import enum

from sqlalchemy import ScalarResult
from api.utils.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


class PriceTypeEnum(enum.Enum):
    SELL = "sell"
    BUY = "buy"


class PriceHistory(db.Model):
    __tablename__ = "price_history"
    id: int = db.Column(db.Integer, primary_key=True, nullable=False)
    price: float = db.Column(db.Numeric(10, 2), nullable=False)
    product_id: int = db.Column(db.Integer, db.ForeignKey("products.id"))
    supplier_id: int = db.Column(db.Integer, db.ForeignKey("providers.id"))
    price_type: PriceTypeEnum = db.Column(
        db.Enum(PriceTypeEnum, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    start_date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    thru_date = db.Column(db.DateTime)
    db.CheckConstraint("thru_date IS NULL OR start_date < thru_date")
    db.CheckConstraint(
        "price_type = 'sell' or (price_type = 'buy' and supplier_id is not null)"
    )

    def invalidate_current_price(self):
        self.thru_date = datetime.now(timezone.utc)
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_latest_by_product_id(product_id: int) -> "PriceHistory":
        return db.session.execute(
            db.select(PriceHistory).filter_by(product_id=product_id, thru_date=None)
        ).scalar_one()

    @staticmethod
    def get_latest_price(
        product_id: int, price_type: PriceTypeEnum, supplier_id: int = None
    ):
        query = db.select(PriceHistory).filter_by(
            product_id=product_id, price_type=price_type
        )
        if supplier_id:
            query = query.filter_by(supplier_id=supplier_id)

        price_history: ScalarResult[PriceHistory] = db.session.execute(query).scalars()
        return next(
            (ph.price for ph in price_history if ph.thru_date is None),
            None,
        )

    @staticmethod
    def get_history_by_product_id(product_id: int):
        query = (
            db.select(PriceHistory)
            .filter_by(product_id=product_id)
            .order_by(PriceHistory.price_type)
        )
        return db.session.execute(query).scalars()


class PriceHistorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PriceHistory
        sqla_session = db.session
        load_instance = True

    price_type = fields.Enum(PriceTypeEnum, by_value=True)
