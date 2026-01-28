from flask import Blueprint, request

from services.paper_service import process_paper, process_text

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    return {
        "status": "ok",
        "service": "medical-paper-explainer"
    }, 200


@api_bp.route("/explain-pdf", methods=["POST"])
def explain():
    file = request.files["file"]
    level = request.form.get("level")

    if not level:
        return {"status": "error", "message": "No explanation level provided"}, 400

    result, error, code = process_paper(file, level)

    if error:
        return {"status": "error", "message": error}, code

    return {
        "status": "success",
        "result": result
    }, 200


@api_bp.route("/explain-text", methods=["POST"])
def explain_text():
    if not request.is_json:
        return {"status": "error", "message": "Content-Type must be application/json"}, 415

    data = request.get_json(silent=True)
    if not data:
        return {"status": "error", "message": "Invalid JSON body"}, 400

    text = data.get("text")
    level = data.get("level")

    if not level:
        return {"status": "error", "message": "No explanation level provided"}, 400

    result, error, code = process_text(text, level)

    if error:
        return {"status": "error", "message": error}, code

    return {"status": "success", "data": result}, 200


@api_bp.route("/levels", methods=["GET"])
def get_levels():
    return {
        "levels": ["beginner", "intermediate", "expert"]
    }, 200
