from marshmallow import Schema


class CustomerStatisticsSchema(Schema):
    class Meta:
        fields = (
            "name",
            "customer_id",
            "bill_quantity",
            "status",
            "paid_amount",
            "amount_to_pay",
        )


class ProductStatisticsSchema(Schema):
    class Meta:
        fields = ("sold_quantity", "name", "product_id", "image_url")


class MonthVsOrderQtySchema(Schema):
    class Meta:
        fields = ("order_qty", "month", "year")

class PaymentStatusStatisticsSchema(Schema):
    class Meta:
        fields = ("status", "qty", "year")
