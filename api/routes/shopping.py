from flask import request
from flask_restful import Resource
from api.models.customers import Customer
from api.models.order_details import OrderDetailSchema
from api.models.orders import Order, OrderSchema
from api.models.payments import PaymentSchema
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp


class ShoppingList(Resource):
    def post(self):
        try:
            data = request.get_json()
            import pprint as pp
            pp.pprint(data)
            if data.get("customer_id") is None:
                return response_with(
                    resp.BAD_REQUEST_400, message="customer_id is missing."
                )
            if data.get("products") is None:
                return response_with(
                    resp.BAD_REQUEST_400, message="products is missing."
                )
            if data.get("pay") is None:
                return response_with(resp.BAD_REQUEST_400, message="pay is missing.")

            customer_id = data["customer_id"]
            buyer = Customer.find_by_id(customer_id)
            if buyer is None:
                return response_with(
                    resp.SERVER_ERROR_404,
                    message="No existe ningún cliente con ese ID.",
                )

            payment = PaymentSchema().load(data["pay"])
            new_order = Order(customer=buyer, payment=payment, date=data["date"])
            db.session.add(new_order)
            db.session.flush()

            _ = [
                product.update({"order_id": new_order.id})
                for product in data["products"]
            ]
            products = OrderDetailSchema(many=True).load(data["products"])
            new_order.order_details = products
            new_order.create()

            new_order = OrderSchema().dump(new_order)
            pp.pprint(new_order)
            return response_with(resp.SUCCESS_200, value={"order": new_order})
        except Exception as e:
            print(e)
            return response_with(resp.BAD_REQUEST_400)

    def get(self):
        return response_with(resp.SUCCESS_200, message="Hola")



