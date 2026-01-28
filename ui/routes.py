from flask import Blueprint, render_template, request

from services.paper_service import process_paper, process_text

ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files.get("file")
        text = request.form.get("text", "")
        level = request.form.get("level", "beginner")

        # If a PDF is uploaded, use the PDF pipeline
        if file and file.filename:
            data, error, _ = process_paper(file, level)

        # If text is provided, use the text pipeline
        elif text and text.strip():
            data, error, _ = process_text(text, level)

        # Otherwise, user provided nothing
        else:
            return render_template("index.html", error="Please provide either a PDF or some text.")

        if error:
            return render_template("index.html", error=error)

        return render_template(
            "index.html",
            explanation=data["explanation"],
            level=data["level"]
        )

    return render_template("index.html")