import os
from flask import Flask

from api.routes.users import user_routes
from api.config.config import ProductionConfig, TestingConfig, DevelopmentConfig

app = Flask(__name__)

match os.environ.get("WORK_ENV"):
    case "PROD":
        app_config = ProductionConfig
    case "TEST":
        app_config = TestingConfig
    case _:
        app_config = DevelopmentConfig
app.config.from_object(app_config)

app.register_blueprint(user_routes, url_prefix="/api/user")

@app.route("/")
def index():
	return "<h1>Welcome to Author Manager</h1>"


@app.route("/")
def hello():
    return "Hello"


if __name__ == "__main__":
    app.run(debug=True)
