from api.utils.database import db
from marshmallow_sqlalchemy  import SQLAlchemyAutoSchema, auto_field

class SalespersonTypes(db.Model):
    __tablename__ = "salesperson_types"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False, unique=True)

class SalespersonTypesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SalespersonTypes
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)