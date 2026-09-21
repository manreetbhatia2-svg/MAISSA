import os
import json


# ==================================================
# LOAD COMBINED SCHEME DATA
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "combined_schemes.json")

with open(
    json_path,
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)

schemes = data["schemes"]


# ==================================================
# NORMALIZE TARGET GROUP
# ==================================================

def normalize_target_group(target_group):

    if not target_group:
        return ""

    target_group = target_group.strip()

    # Scheduled Caste
    if target_group.upper() in [
        "SC",
        "SCHEDULED CASTE",
        "SCHEDULED CASTES"
    ]:
        return "Scheduled Castes"

    # Children of parents engaged in unclean occupations
    if target_group.lower() == (
        "children of parents engaged in unclean occupations"
    ):
        return "Children of parents engaged in unclean occupations"

    return target_group


# ==================================================
# CHECK INDIVIDUAL SCHEME
# ==================================================

def check_scheme(
    scheme,
    project_type,
    cost,
    income,
    education_status,
    target_group
):

    # ------------------------------------------------
    # NORMALIZE TARGET GROUP
    # ------------------------------------------------

    target_group = normalize_target_group(target_group)


    # ------------------------------------------------
    # CHECK INCOME
    # ------------------------------------------------

    income_limit = scheme.get("income_limit")

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

    min_project_cost = scheme.get("min_project_cost")

    if min_project_cost is not None:

        if cost <= min_project_cost:
            return False


    # ------------------------------------------------
    # CHECK MAXIMUM PROJECT COST
    # ------------------------------------------------

    max_project_cost = scheme.get("max_project_cost")

    if max_project_cost is not None:

        if cost > max_project_cost:
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
    # CHECK TARGET GROUP
    # ------------------------------------------------

    scheme_target_groups = scheme.get(
        "target_groups",
        []
    )

    if scheme_target_groups:

        # Normalize the values stored in JSON
        normalized_scheme_groups = [
            normalize_target_group(group)
            for group in scheme_target_groups
        ]

        if target_group not in normalized_scheme_groups:
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
    education_status,
    target_group
):

    eligible_schemes = []

    target_group = normalize_target_group(
        target_group
    )

    for scheme in schemes:

        if check_scheme(
            scheme,
            project_type,
            cost,
            income,
            education_status,
            target_group
        ):

            eligible_schemes.append(scheme)

    return eligible_schemes


# ==================================================
# FIND OVERALL REJECTION REASONS
# ==================================================

def get_overall_rejection_reason(
    project_type,
    cost,
    income,
    education_status,
    target_group
):

    reasons = []

    target_group = normalize_target_group(
        target_group
    )


    # ------------------------------------------------
    # 1. INCOME CHECK
    # ------------------------------------------------

    income_limits = [
        scheme["income_limit"]
        for scheme in schemes
        if scheme.get("income_limit") is not None
    ]

    if income_limits:

        maximum_income = max(income_limits)

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
            "min_project_cost"
        )

        max_cost = scheme.get(
            "max_project_cost"
        )

        # No minimum restriction
        if min_cost is None:
            min_cost = float("-inf")

        # No maximum restriction
        if max_cost is None:
            max_cost = float("inf")

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
    # 5. TARGET GROUP CHECK
    # ------------------------------------------------

    target_group_exists = False

    for scheme in schemes:

        scheme_target_groups = scheme.get(
            "target_groups",
            []
        )

        normalized_scheme_groups = [
            normalize_target_group(group)
            for group in scheme_target_groups
        ]

        if target_group in normalized_scheme_groups:

            target_group_exists = True
            break


    if not target_group_exists:

        reasons.append(
            "No available scheme was found "
            "for the selected target group."
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

