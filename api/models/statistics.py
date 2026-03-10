from api.utils.database import ma
from marshmallow import Schema, fields


class CustomerStatisticsSchema(ma.Schema):
    class Meta:
        fields = (
            "name",
            "customer_id",
            "bill_quantity",
            "status",
            "paid_amount",
            "amount_to_pay",
        )


class ProductStatisticsSchema(ma.Schema):
    class Meta:
        fields = ("sold_quantity", "name", "product_id")


class MonthVsOrderQtySchema(ma.Schema):
    class Meta:
        fields = ("order_qty", "month", "year")

class PaymentStatusStatisticsSchema(ma.Schema):
    class Meta:
        fields = ("status", "qty", "year")

class PaymentSummary(ma.Schema):
    class Meta:
        fields = ("status", "qty")

class MostSellingSummary(ma.Schema):
    name = fields.Str()
    category_id = fields.Int()
    product_id = fields.Int()
    image_url = fields.Str()
    sold_qty = fields.Int()

class SalesSummary(ma.Schema):
    order_qty = fields.Int()

class RunningOuttaStocksSummary(ma.Schema):
    product_name = fields.Str()
    quantity_available = fields.Int()
    reorder_point = fields.Int()


