from time import sleep
from flask import request
from flask_restful import Resource

from api.models.commissions import Commission, CommissionItem, CommissionSchema
from api.utils.database import db
from api.utils.responses import pagination_to_dict, response_with
import api.utils.responses as resp


class CommissionResource(Resource):
    def get(self, commission_id: int):
        commission = db.get_or_404(Commission, commission_id)
        res = CommissionSchema(many=True).dump(commission)
        return response_with(
            resp.SUCCESS_200,
            value={"commission": res},
        )
    
    def patch(self, commission_id: int):
        data = request.json
        print(data)
        sleep(3)
        if data.get("paymentDate") is None:
            return response_with(resp.BAD_REQUEST_400, error="paymentDate is missing.")
        
        commission = db.get_or_404(Commission, commission_id)
        if data.get("paymentDate"):
            if data["paymentDate"].endswith("Z"):
                data["paymentDate"] = data["paymentDate"][:-1]
            commission.payment_date = data["paymentDate"]
        
        commission.create()
        response_with(resp.SUCCESS_200)


class CommissionResourceList(Resource):
    def get(self):
        query = db.select(Commission).order_by(Commission.created_at)
        pag = db.paginate(query)
        res = CommissionSchema(many=True).dump(pag.items)
        return response_with(
            resp.SUCCESS_200,
            value={"commissions": res},
            pagination=pagination_to_dict(pag),
        )

    def post(self):
        try:
            data = request.json
            print(data)
            if data.get("commissionItems") is None:
                return response_with(
                    resp.BAD_REQUEST_400, error="commissionItems is missing."
                )
            if len(data["commissionItems"]) == 0:
                return response_with(
                    resp.BAD_REQUEST_400, error="commission_items cannot be empty."
                )

            commission = Commission(
                rate=data["rate"],
                payment_date=data["paymentDate"],
                admin_id=data["adminId"],
                salesperson_id=data["salespersonId"],
            )

            commission.commission_items = [
                CommissionItem(
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    supplier_id=item["supplier_id"],
                )
                for item in data["commissionItems"]
            ]
            commission.calculate_unit_commission()
            
            for item in commission.commission_items:
                print(item.unit_commission)

            db.session.add(commission)
            db.session.flush()
            print("commission.id:",commission.id)
            db.session.execute(
                db.text("call commission_api_calculate_amount(:commission_id)"),
                {"commission_id": commission.id},
            )
            commission.create()
            return response_with(
                resp.SUCCESS_201,
                value={"commission": CommissionSchema().dump(commission)},
            )
        except Exception as e:
            print(e)
            db.session.rollback()
            response_with(resp.BAD_REQUEST_400, error=str(e))
