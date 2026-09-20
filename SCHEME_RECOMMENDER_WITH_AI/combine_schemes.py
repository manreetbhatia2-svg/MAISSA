import json


# ==================================================
# LOAD EXISTING SCHEMES
# ==================================================

with open(
    "schemes.json",
    "r",
    encoding="utf-8"
) as file:

    existing_data = json.load(file)


existing_schemes = existing_data["schemes"]


# ==================================================
# LOAD AI-EXTRACTED AND NORMALIZED SCHEMES
# ==================================================

with open(
    "normalized_schemes.json",
    "r",
    encoding="utf-8"
) as file:

    ai_schemes = json.load(file)


# ==================================================
# COMBINE BOTH LISTS
# ==================================================

combined_schemes = existing_schemes + ai_schemes


# ==================================================
# CREATE FINAL JSON STRUCTURE
# ==================================================

combined_data = {
    "schemes": combined_schemes
}


# ==================================================
# SAVE COMBINED SCHEMES
# ==================================================

with open(
    "combined_schemes.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        combined_data,
        file,
        indent=4,
        ensure_ascii=False
    )


# ==================================================
# DISPLAY RESULT
# ==================================================

print("================================")
print("Schemes combined successfully!")
print("================================")

print(
    "Existing schemes:",
    len(existing_schemes)
)

print(
    "AI-extracted schemes:",
    len(ai_schemes)
)

print(
    "Total schemes:",
    len(combined_schemes)
)

print(
    "\nSaved to: combined_schemes.json"
)