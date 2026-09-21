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

    # -----------------------------
    # PROJECT TYPE
    # -----------------------------
    project_type = request.form.get(
        "project_type",
        "business"
    ).strip().lower()

    # -----------------------------
    # PROJECT COST
    # -----------------------------
    try:
        cost = float(request.form.get("cost", 500000))
    except (ValueError, TypeError):
        cost = 500000.0

    # -----------------------------
    # ANNUAL FAMILY INCOME
    # -----------------------------
    try:
        income = float(request.form.get("income", 180000))
    except (ValueError, TypeError):
        income = 180000.0

    # -----------------------------
    # EDUCATION STATUS
    # -----------------------------
    raw_education = request.form.get(
        "education_status",
        "not_student"
    ).strip().lower()

    if raw_education in ["not_student", "not_required"]:
        education_status = "not_required"

    elif raw_education == "student":
        education_status = "student"

    else:
        education_status = raw_education

    # -----------------------------
    # TARGET GROUP
    # -----------------------------
    raw_target = request.form.get(
        "target_group",
        ""
    ).strip()

    # Convert dropdown value into
    # the exact wording used in JSON
    if raw_target == "Scheduled Castes":
        target_group = "Scheduled Castes"

    elif raw_target == "Children of parents engaged in unclean occupations":
        target_group = "Children of parents engaged in unclean occupations"

    else:
        target_group = raw_target

    # -----------------------------
    # RECOMMEND SCHEMES
    # -----------------------------
    eligible_schemes = recommend_schemes(
        project_type,
        cost,
        income,
        education_status,
        target_group
    )

    # -----------------------------
    # IF NO SCHEME MATCHES
    # -----------------------------
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

    # -----------------------------
    # SHOW RESULTS
    # -----------------------------
    return render_template(
        "results.html",
        eligible_schemes=eligible_schemes,
        reasons=reasons
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )