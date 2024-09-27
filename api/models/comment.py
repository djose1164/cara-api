from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    content = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    def __init__(self, content, user_id) -> None:
        super().__init__()
        self.content = content
        self.user_id = user_id



class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        load_instance = True
        sqla_session = db.session

    user_id = auto_field()
    user = fields.Nested("UserSchema", exclude=("salesperson", "customer"))
