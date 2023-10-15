from flask import Blueprint

from api.models.product_category import ProductCategory, ProductCategorySchema
from api.utils.responses import response_with
import api.utils.responses as resp

category_routes = Blueprint("category_routes", __name__)

@category_routes.route("/")
def index():
    fetched = ProductCategory.query.all()
    fetched = ProductCategorySchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"categories": fetched})
