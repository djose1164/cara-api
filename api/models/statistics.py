from api.utils.database import ma


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
        fields = ("sold_quantity", "name", "product_id", "image_url")


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
    class Meta:
        fields = ("name", "category_id", "product_id", "image_url", "sold_qty")

class SalesSummary(ma.Schema):
    class Meta:
        fields = ("order_qty",)

class RunningOuttaStocksSummary(ma.Schema):
    class Meta:
        fields = ("product_name", "quantity_available", "reorder_point")


