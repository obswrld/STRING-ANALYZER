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

@string_db.route("/strings", methods=["GET"])
def get_all_strings():
    query = StringAnalysis.query
    is_palindrome = request.args.get("is_palindrome")
    min_length = request.args.get("min_length", type=int)
    max_length = request.args.get("max_length", type=int)
    word_count = request.args.get("word_count", type=int)
    contains_character = request.args.get("contains_character")

    results = []

    for record in query.all():
        props = record.properties

        if is_palindrome is not None:
            if props.get("is_palindrome") != (is_palindrome.lower() == "true"):
                continue
            if min_length is not None and props.get("length", 0) < min_length:
                continue
            if max_length is not None and props.get("length", 0) > max_length:
                continue
            if word_count is not None and props.get("count", 0) != word_count:
                continue
            if contains_character and contains_character.lower() not in record.value.lower():
                continue

            results.append({
                "id": record.id,
                "value": record.value,
                "properties": props,
                "created_at": record.created_at.isoformat() + "Z"
            })

        response = {
            "data": results,
            "count": len(results),
            "filters_applied": {
                "is_palindrome": is_palindrome,
                "min_length": min_length,
                "max_length": max_length,
                "word_count": word_count,
                "contains_character": contains_character,
            }
        }

        return jsonify(response), 200