from flask import Flask, render_template, request, redirect
from flask_cors import CORS

from recommender import (
    recommend_schemes,
    get_overall_rejection_reason
)

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if request.method == "GET":
        return redirect("/")

    project_type = request.form.get("project_type", "business").strip().lower()

    try:
        cost = float(request.form.get("cost", 500000))
    except (ValueError, TypeError):
        cost = 500000.0

    try:
        income = float(request.form.get("income", 180000))
    except (ValueError, TypeError):
        income = 180000.0

    raw_education = request.form.get("education_status", "not_student").strip()
    raw_target = (request.form.get("target_group") or request.form.get("category") or "SC").strip()

    # 1. Normalize Target Group to match schemes.json
    if raw_target.upper() == "SC" or "caste" in raw_target.lower():
        target_group = "Scheduled Castes"
    else:
        target_group = raw_target

    # 2. Normalize Education Status to match schemes.json
    if raw_education in ["not_student", "not_required"]:
        education_status = "not_required"
    elif "student" in raw_education:
        education_status = "student"
    else:
        education_status = raw_education

    # Evaluate schemes
    eligible_schemes = recommend_schemes(
        project_type,
        cost,
        income,
        education_status,
        target_group
    )

    if eligible_schemes:
        reasons = []
    else:
        reasons = get_overall_rejection_reason(
            project_type,
            cost,
            income,
            education_status,
            target_group
        )

    return render_template(
        "results.html",
        eligible_schemes=eligible_schemes,
        reasons=reasons
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)