from flask import request, jsonify, Blueprint
from sqlalchemy.exc import IntegrityError
from models.string_model import StringAnalysis
from services.analyzer_service import analyze_string
from models.string_model import db

string_db = Blueprint('string_db', __name__)

@string_db.route("/strings", methods=["POST"])
def create_string_analyzer():
    data = request.get_json()
    if not data or "value" not in data:
        return jsonify({"error": "missing value field"}), 400
    value = data["value"]

    existing_strings = StringAnalysis.query.filter_by(value=value).first()
    if existing_strings:
        return jsonify({"error": "string already exist"}),409

    props = analyze_string(value)
    string_hash = props["properties"]["sha256_hash"]

    record = StringAnalysis(
        id = string_hash,
        value = value,
        properties = props["properties"],
    )

    try:
        db.session.add(record)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database Conflict"}), 409

    response = {
        "id": string_hash,
        "value": value,
        "properties": props,
        "created_at": record.created_at.isoformat() + "Z"
    }

    return jsonify(response), 201