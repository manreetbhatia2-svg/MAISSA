import json
import re


def convert_amount(value):
    """
    Convert values like:
    'Rs. 2.5 lakh' -> 250000
    'Rs. 7 crores' -> 70000000
    '500000' -> 500000
    """

    if value is None:
        return None

    # Already a number
    if isinstance(value, (int, float)):
        return int(value)

    value = str(value).lower().replace(",", "").strip()

    # If there is no useful number, return None
    match = re.search(r"\d+(?:\.\d+)?", value)

    if not match:
        return None

    number = float(match.group())

    if "crore" in value:
        number *= 10000000

    elif "lakh" in value:
        number *= 100000

    elif "thousand" in value:
        number *= 1000

    return int(number)

def normalize_education_status(value):

    if value is None:
        return None

    if isinstance(value, list):
        return value

    return [value]


def normalize_scheme(scheme):

    scheme["income_limit"] = convert_amount(
        scheme.get("income_limit")
    )

    scheme["max_project_cost"] = convert_amount(
        scheme.get("max_project_cost")
    )

    scheme["max_loan"] = convert_amount(
        scheme.get("max_loan")
    )

    scheme["education_status"] = normalize_education_status(
        scheme.get("education_status")
    )

    return scheme


# -----------------------------------------
# Read extracted schemes
# -----------------------------------------

with open(
    "extracted_schemes.json",
    "r",
    encoding="utf-8"
) as file:

    schemes = json.load(file)


# -----------------------------------------
# Normalize every scheme
# -----------------------------------------

normalized_schemes = []

for scheme in schemes:

    normalized_scheme = normalize_scheme(
        scheme
    )

    normalized_schemes.append(
        normalized_scheme
    )


# -----------------------------------------
# Save normalized schemes
# -----------------------------------------

with open(
    "normalized_schemes.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        normalized_schemes,
        file,
        indent=4,
        ensure_ascii=False
    )


print("Normalization complete!")

print(
    "Total schemes:",
    len(normalized_schemes)
)

print(
    "Saved to: normalized_schemes.json"
)