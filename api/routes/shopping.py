from flask import request
from flask_restful import Resource
from api.models.customers import Customer
from api.models.order_details import OrderDetail, OrderDetailSchema
from api.models.orders import Order, OrderQueue, OrderSchema
from api.models.payments import PaymentSchema
from api.models.price_history import PriceHistory, PriceTypeEnum
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp


class ShoppingList(Resource):
    def post(self):
        try:
            data = request.get_json()
            import pprint as pp

            pp.pprint(data)

            Order.sanity_check(data)

            payment = PaymentSchema().load(data["pay"])
            new_order = Order(
                customer=Customer.find_by_id(data["customer_id"]),
                payment=payment,
                date=data["date"],
            )
            db.session.add(new_order)
            db.session.flush()

            _ = [
                product.update({"order_id": new_order.id})
                for product in data["products"]
            ]

            new_order.order_details = [
                OrderDetail(
                    product_id=x["product_id"],
                    quantity=x["quantity"],
                    price_id=PriceHistory.get_latest_price(
                        x["product_id"], PriceTypeEnum.BUY
                    ),
                )
                for x in data["products"]
            ]
            new_order.create()
            new_order.add_to_queue()

            new_order = OrderSchema().dump(new_order)
            print("OrderQueue.add_order")
            
            pp.pprint(new_order)
            return response_with(resp.SUCCESS_200, value={"order": new_order})
        except Exception as e:
            print(e)
            return response_with(resp.BAD_REQUEST_400)

    def get(self):
        return response_with(resp.SUCCESS_200, message="Hola")
