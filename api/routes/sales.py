from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy import text
from api.models.sales import Sale, SalesSchema
from api.utils.database import db
import api.utils.responses as resp
from api.utils.responses import response_with, pagination_to_dict


class SalesResource(Resource):
    decorators = [jwt_required()]

    def get(self, sale_id: int):
        query = text("call sales.get_sale(:sale_id)")
        res = db.session.execute(query, {"sale_id": sale_id}).one()
        sale = SalesSchema().dump(res)
        return response_with(resp.SUCCESS_200, value={"sale": sale})


class SalesResourceList(Resource):
    decorators = [jwt_required()]

    def get(self):
        res = db.paginate(db.select(Sale).order_by(Sale.created_at), per_page=1)
        sale = SalesSchema().dump(res.items, many=True)

        print(db.paginate(db.select(Sale).order_by(Sale.created_at)))
        return response_with(
            resp.SUCCESS_200,
            value={"sales": sale},
            pagination=pagination_to_dict(res)
        )

    def post(self):
        try:
            data = request.json
            if data.get("customer_id") is None:
                return response_with(resp.BAD_REQUEST_400, error="Missing customer_id")

            query = text("call sales.add_sale(:customer_id, :order_id)")
            res = db.session.execute(
                query, {"customer_id": data["customer_id"], "order_id": None}
            )
            db.session.flush()

            sale_id = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]
            for item in data["sale_items"]:
                query = text("call sales.add_sale_item(:sale_id, :product_id, :qty)")
                params = {
                    "sale_id": sale_id,
                    "product_id": item["product_id"],
                    "qty": item["qty"],
                }
                res = db.session.execute(query, params)
                db.session.flush()

            query = text("call sales.update_sale_total(:sale_id)")
            db.session.execute(query, {"sale_id": sale_id})
            db.session.commit()

            print("sale_id:", sale_id)
            query = text("call sales.get_sale(:sale_id)")
            res = db.session.execute(query, {"sale_id": sale_id}).one()
            return response_with(
                resp.SUCCESS_200, value={"sale": SalesSchema().dump(res)}
            )
        except Exception as e:
            db.session.rollback()
            print(e)
            resp.response_with(resp.BAD_REQUEST_400)
