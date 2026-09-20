import json


# ==================================================
# LOAD COMBINED SCHEME DATA
# ==================================================

with open(
    "combined_schemes.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)

schemes = data["schemes"]


# ==================================================
# CHECK INDIVIDUAL SCHEME
# ==================================================

def check_scheme(
    scheme,
    project_type,
    cost,
    income,
    education_status
):

    # ------------------------------------------------
    # CHECK INCOME
    # ------------------------------------------------

    income_limit = scheme.get("income_limit")

    # If income_limit is not None,
    # check whether user's income exceeds it
    if income_limit is not None:

        if income > income_limit:
            return False


    # ------------------------------------------------
    # CHECK PROJECT TYPE
    # ------------------------------------------------

    if project_type not in scheme.get(
        "project_type",
        []
    ):
        return False


    # ------------------------------------------------
    # CHECK MINIMUM PROJECT COST
    # ------------------------------------------------

    if scheme.get("min_project_cost") is not None:
        if cost <= scheme["min_project_cost"]:
            return False


    # ------------------------------------------------
    # CHECK MAXIMUM PROJECT COST
    # ------------------------------------------------

    if scheme.get("max_project_cost") is not None:
        if cost > scheme["max_project_cost"]:
            return False


    # ------------------------------------------------
    # CHECK EDUCATION STATUS
    # ------------------------------------------------

    education_requirements = scheme.get(
        "education_status"
    )

    if education_requirements:

        if "student" in education_requirements:

            if education_status != "student":
                return False


    # ------------------------------------------------
    # ALL CONDITIONS PASSED
    # ------------------------------------------------

    return True


# ==================================================
# FIND ELIGIBLE SCHEMES
# ==================================================

def recommend_schemes(
    project_type,
    cost,
    income,
    education_status
):

    eligible_schemes = []

    for scheme in schemes:

        if check_scheme(
            scheme,
            project_type,
            cost,
            income,
            education_status
        ):

            eligible_schemes.append(
                scheme
            )

    return eligible_schemes


# ==================================================
# FIND OVERALL REJECTION REASONS
# ==================================================

def get_overall_rejection_reason(
    project_type,
    cost,
    income,
    education_status
):

    reasons = []


    # ------------------------------------------------
    # 1. INCOME CHECK
    # ------------------------------------------------

    income_limits = [
        scheme["income_limit"]
        for scheme in schemes
        if scheme.get("income_limit") is not None
    ]

    if income_limits:

        maximum_income = max(
            income_limits
        )

        if income > maximum_income:

            reasons.append(
                f"Your annual income of ₹{income:,.0f} "
                f"exceeds the maximum eligible limit of "
                f"₹{maximum_income:,.0f}."
            )


    # ------------------------------------------------
    # 2. PROJECT TYPE CHECK
    # ------------------------------------------------

    project_type_exists = False

    for scheme in schemes:

        if project_type in scheme.get(
            "project_type",
            []
        ):

            project_type_exists = True
            break


    if not project_type_exists:

        reasons.append(
            f"Your selected project type "
            f"'{project_type}' is not supported "
            f"by the available schemes."
        )


    # ------------------------------------------------
    # 3. PROJECT COST CHECK
    # ------------------------------------------------

    cost_matches = False

    for scheme in schemes:

        if project_type not in scheme.get(
            "project_type",
            []
        ):
            continue


        min_cost = scheme.get(
            "min_project_cost",
            0
        )

        max_cost = scheme.get(
            "max_project_cost",
            float("inf")
        )


        if min_cost < cost <= max_cost:

            cost_matches = True
            break


    if not cost_matches:

        reasons.append(
            f"Your estimated project cost of "
            f"₹{cost:,.0f} does not fall within "
            f"the supported project-cost range."
        )


    # ------------------------------------------------
    # 4. EDUCATION STATUS CHECK
    # ------------------------------------------------

    if project_type == "education":

        if education_status != "student":

            reasons.append(
                "The education scheme requires "
                "the applicant to have student status."
            )


    # ------------------------------------------------
    # RETURN REASONS
    # ------------------------------------------------

    if not reasons:

        reasons.append(
            "No suitable scheme was found "
            "based on the given eligibility criteria."
        )


    return reasons