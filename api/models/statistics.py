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
