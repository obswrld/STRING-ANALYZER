from flask import Flask
from models.string_model import db
from routes.string_route import string_db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

app.register_blueprint(string_db)

@app.route('/')
def home():
    return {"message": "Welcome to StringAnalysis API!"}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)