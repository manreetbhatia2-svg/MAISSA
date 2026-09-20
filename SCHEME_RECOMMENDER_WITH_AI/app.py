from flask import Flask, render_template, request

from recommender import (
    recommend_schemes,
    get_overall_rejection_reason
)


# Create Flask application
app = Flask(__name__)


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# RECOMMENDATION
# ==================================================

@app.route("/recommend", methods=["POST"])
def recommend():

    # Get data from the HTML form
    project_type = request.form["project_type"]

    cost = float(request.form["cost"])

    income = float(request.form["income"])

    education_status = request.form["education_status"]


    # Get eligible schemes
    eligible_schemes = recommend_schemes(
        project_type,
        cost,
        income,
        education_status
    )


    # If no schemes are found,
    # get the overall rejection reasons
    if eligible_schemes:

        reasons = []

    else:

        reasons = get_overall_rejection_reason(
            project_type,
            cost,
            income,
            education_status
        )


    # Send results to results.html
    return render_template(
        "results.html",
        eligible_schemes=eligible_schemes,
        reasons=reasons
    )


# ==================================================
# RUN FLASK
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)