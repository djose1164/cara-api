"""
Copyright Cara 2024
"""

from flask import request
from flask_restful import Resource

from api.models.comment import Comment, CommentSchema
from api.models.orders import Order, OrderComment, OrderCommentSchema
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp


class CommentResource(Resource):
    def get(self, identifier: int):
        fetched = db.get_or_404(Comment, identifier)
        return response_with(
            resp.SUCCESS_200, value={"comment": CommentSchema().dump(fetched)}
        )


class CommentResourceList(Resource):
    def get(self):
        order_id: int = request.args.get("order_id")

        if order_id:
            fetched = OrderComment.fetch_by_order_id(order_id)
            return response_with(
            resp.SUCCESS_200, value={"comments": CommentSchema(many=True).dump(fetched)}
        )
        else:
            return response_with(
                resp.BAD_REQUEST_400, error="order_id argument is missing."
            )

    def post(self):
        data = request.get_json()
        order_id: int = int(request.args.get("order_id", 0))
        if order_id:
            new_comment = Comment(content=data["content"], user_id=data["user_id"])
            db.session.add(new_comment)
            db.session.flush()
            order_coment = OrderComment(comment=new_comment, order_id=order_id)
            order_coment.create()
            print(OrderCommentSchema().dump(order_coment))
            return response_with(resp.SUCCESS_200, value={"comment": CommentSchema().dump(order_coment.comment)})
        return response_with(resp.BAD_REQUEST_400, error="You need to provide an order_id.")
