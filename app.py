from flask import Flask
from flask_cors import CORS
from routes.chat import chat_bp
from routes.report import report_bp
from config import LM_BASE_URL
import logging

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")

    logging.basicConfig(level=logging.INFO)
    app.logger.info(f"LM Studio endpoint : {LM_BASE_URL}")

    return app

if __name__ == "__main__":
    create_app().run(debug=True, port=5000)