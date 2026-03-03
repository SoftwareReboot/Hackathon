from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from routes.chat import chat_bp
from routes.report import report_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(chat_bp)
    app.register_blueprint(report_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)