from flask import request, jsonify, Blueprint
from sqlalchemy.exc import IntegrityError
from models.string_model import StringAnalysis, db
from services.analyzer_service import analyze_string, parse_natural_language_query

string_db = Blueprint('string_db', __name__)

@string_db.route("/strings", methods=["POST"])
def create_string_analyzer():
    data = request.get_json()
    if not data or "value" not in data:
        return jsonify({"error": "missing value field"}), 400
    value = data["value"].strip()

    existing_strings = StringAnalysis.query.filter_by(value=value).first()
    if existing_strings:
        return jsonify({"error": "string already exist"}),409

    props = analyze_string(value)
    string_hash = props["id"]

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
        "properties": props["properties"],
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

        if is_palindrome is not None and props.get("is_palindrome") != (is_palindrome.lower() == "true"):
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

@string_db.route("/strings/<string_value>", methods=["GET"])
def get_single_string(string_value):
    record = StringAnalysis.query.filter_by(value=string_value).first()
    if not record:
        return jsonify({"error": "string not found"}), 404

    response = {
        "id": record.id,
        "value": record.value,
        "properties": record.properties,
        "created_at": record.created_at.isoformat() + "Z"
    }

    return jsonify(response), 200

@string_db.route("/strings/<string_value>", methods=["DELETE"])
def delete_string(string_value):
    record = StringAnalysis.query.filter_by(value=string_value).first()
    if not record:
        return jsonify({"error": "string not found"}), 404
    db.session.delete(record)
    db.session.commit()
    return '', 204

@string_db.route("/strings/filter-by-natural-language", methods=["GET"])
def filter_by_natural_language():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "missing query parameter"}), 400

    try:
        filters = parse_natural_language_query(query)
    except Exception as e:
        return jsonify({"error": "unable to parse natural language"}), 400

    if not filters:
        return jsonify({"error": "no filter could be interpreted from the query"}), 422

    results = []
    for record in StringAnalysis.query.all():
        props = record.properties
        if "is_palindrome" in filters and props.get("is_palindrome") != filters["is_palindrome"]:
            continue
        if "word_count" in filters and props.get("word_count", 0) != filters["word_count"]:
            continue
        if "min_length" in filters and props.get("length", 0) < filters["min_length"]:
            continue
        if "max_length" in filters and props.get("length", 0) > filters["max_length"]:
            continue
        if "contains_character" in filters and filters["contains_character"].lower() not in record.value.lower():
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
        "interpreted_query": {
            "original": query,
            "parsed_filters": filters
        }
    }

    return jsonify(response), 200