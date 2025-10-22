from flask import Flask, jsonify
from models.string_model import db
from routes.string_route import string_db
import os

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(string_db)

    with app.app_context():
        db.create_all()
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to String-Analysis API!"})

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
