import os
import json
import math
from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
from flask_cors import CORS
import google.generativeai as genai

try:
    from SCHEME_RECOMMENDER_WITH_AI.recommender import recommend_schemes, get_overall_rejection_reason
except ImportError:
    from recommender import recommend_schemes, get_overall_rejection_reason

app = Flask(__name__, 
            static_folder=".", 
            template_folder=".")
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DIST_DIR = os.path.join(BASE_DIR, "EMI_CALCULATOR", "dist")
COMBINED_SCHEMES_FILE = os.path.join(BASE_DIR, "combined_schemes.json")

# -------------------------------------------------------------
# STABLE GEMINI MODEL CONFIGURATION
# -------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ai_model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Directly use the standard stable flash model
        ai_model = genai.GenerativeModel("gemini-1.5-flash")
        print("✓ Gemini AI Model Active: gemini-1.5-flash")
    except Exception as e:
        print(f"Gemini configuration error: {e}")
        ai_model = None
else:
    print("Gemini Notice: GEMINI_API_KEY environment variable not detected.")
# -------------------------------------------------------------
# CHANNEL LOCATOR DATA HANDLING
# -------------------------------------------------------------
DEFAULT_PARTNERS = [
    { "id": "p1", "name": "State Bank of India - Kothrud SME Branch", "type": "PSB", "latitude": 18.5074, "longitude": 73.8077, "remaining_quota_lakhs": 65.0, "npa_rate": 0.038, "avg_disbursal_days": 24, "supported_schemes": ["Term Loan (TL)", "Educational Loan Scheme (ELS)", "Micro Finance Scheme (MFS)"] },
    { "id": "p2", "name": "Mahatma Phule Backward Class Dev Corp", "type": "SCA", "latitude": 18.5126, "longitude": 73.8782, "remaining_quota_lakhs": 38.0, "npa_rate": 0.045, "avg_disbursal_days": 18, "supported_schemes": ["Micro Finance Scheme (MFS)", "Aajeevika Micro-Finance Yojana (AMY)", "Government of India Post-Matric Scholarship", "Pre-Matric Scholarship for Children of Parents Engaged in Unclean Occupations"] },
    { "id": "p3", "name": "Maharashtra Gramin Bank - Hadapsar", "type": "RRB", "latitude": 18.5089, "longitude": 73.9260, "remaining_quota_lakhs": 25.0, "npa_rate": 0.049, "avg_disbursal_days": 15, "supported_schemes": ["Term Loan (TL)", "Micro Finance Scheme (MFS)", "Udyam Nidhi Yojana (UNY)"] },
    { "id": "p4", "name": "Bank of Baroda - Deccan Gymkhana Branch", "type": "PSB", "latitude": 18.5177, "longitude": 73.8438, "remaining_quota_lakhs": 42.0, "npa_rate": 0.041, "avg_disbursal_days": 20, "supported_schemes": ["Term Loan (TL)", "Micro Finance Scheme (MFS)", "Educational Loan Scheme (ELS)", "Udyam Nidhi Yojana (UNY)"] },
    { "id": "p5", "name": "Fusion Microfinance - Shivajinagar Hub", "type": "NBFC-MFI", "latitude": 18.5314, "longitude": 73.8446, "remaining_quota_lakhs": 15.0, "npa_rate": 0.021, "avg_disbursal_days": 8, "supported_schemes": ["Micro Finance Scheme (MFS)", "Aajeevika Micro-Finance Yojana (AMY)"] },
    { "id": "p6", "name": "Central Bank of India - Swargate Branch", "type": "PSB", "latitude": 18.5018, "longitude": 73.8586, "remaining_quota_lakhs": 28.0, "npa_rate": 0.052, "avg_disbursal_days": 22, "supported_schemes": ["Term Loan (TL)", "Educational Loan Scheme (ELS)", "Government of India Post-Matric Scholarship"] }
]

def load_combined_schemes():
    if os.path.exists(COMBINED_SCHEMES_FILE):
        try:
            with open(COMBINED_SCHEMES_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("schemes", [])
        except Exception:
            pass
    return []

def load_partners_data():
    possible_paths = [
        os.path.join(BASE_DIR, "CHANNEL_LOCATOR", "data", "partners.json"),
        os.path.join(BASE_DIR, "data", "partners.json"),
        os.path.join(BASE_DIR, "partners.json")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return DEFAULT_PARTNERS

def calculate_haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return round(r * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))), 2)

# -------------------------------------------------------------
# 1. SCHEME MATCHER (HOME)
# -------------------------------------------------------------
@app.route("/")
def home():
    return render_template("SCHEME_RECOMMENDER_WITH_AI/templates/index.html")

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if request.method == "GET":
        return redirect("/")

    project_type = request.form.get("project_type", "business").strip().lower()
    try: cost = float(request.form.get("cost", 500000))
    except (ValueError, TypeError): cost = 500000.0
    try: income = float(request.form.get("income", 180000))
    except (ValueError, TypeError): income = 180000.0

    raw_education = request.form.get("education_status", "not_student").strip()
    raw_target = (request.form.get("target_group") or request.form.get("category") or "SC").strip()

    target_group = "Scheduled Castes" if (raw_target.upper() == "SC" or "caste" in raw_target.lower()) else raw_target
    education_status = "not_required" if raw_education in ["not_student", "not_required"] else ("student" if "student" in raw_education else raw_education)

    eligible_schemes = recommend_schemes(project_type, cost, income, education_status, target_group)
    reasons = [] if eligible_schemes else get_overall_rejection_reason(project_type, cost, income, education_status, target_group)

    return render_template("SCHEME_RECOMMENDER_WITH_AI/templates/results.html", eligible_schemes=eligible_schemes, reasons=reasons)

# -------------------------------------------------------------
# 2. CHANNEL LOCATOR
# -------------------------------------------------------------
@app.route("/locator")
def channel_locator():
    return render_template("CHANNEL_LOCATOR/templates/index.html")

@app.route("/api/user/profile", methods=["POST", "GET"])
def user_profile():
    return jsonify({"status": "success", "message": "Profile synced successfully"})

@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    return jsonify({"success": True, "schemes": load_combined_schemes()})

@app.route("/api/partners/locate", methods=["GET"])
def locate_partners():
    try:
        user_lat = float(request.args.get("lat", 18.5204))
        user_lng = float(request.args.get("lng", 73.8567))
    except ValueError:
        user_lat, user_lng = 18.5204, 73.8567

    selected_scheme = request.args.get("scheme", "").strip()
    raw_partners = load_partners_data()
    scored_partners = []

    for p in raw_partners:
        if selected_scheme:
            schemes = p.get("supported_schemes", [])
            if not any(selected_scheme.lower() in s.lower() or s.lower() in selected_scheme.lower() for s in schemes):
                continue

        dist_km = calculate_haversine(user_lat, user_lng, p.get("latitude", 0), p.get("longitude", 0))
        dist_score = max(0, round((1 - dist_km / 30.0) * 100))
        npa_score = max(0, round((1 - p.get("npa_rate", 0) / 0.15) * 100))
        quota_score = min(100, round((p.get("remaining_quota_lakhs", 0) / 50.0) * 100))
        tat_score = max(0, round((1 - p.get("avg_disbursal_days", 30) / 30.0) * 100))

        composite_score = round((0.40 * dist_score) + (0.30 * npa_score) + (0.20 * quota_score) + (0.10 * tat_score), 1)

        item = dict(p)
        item["distance_km"] = dist_km
        item["routing_score"] = composite_score
        item["breakdown"] = {"proximity": dist_score, "npa": npa_score, "quota": quota_score, "tat": tat_score}
        scored_partners.append(item)

    scored_partners.sort(key=lambda x: x.get("routing_score", 0), reverse=True)
    return jsonify({"success": True, "count": len(scored_partners), "data": scored_partners})

@app.route("/api/partner/ai-review", methods=["POST"])
def get_ai_partner_review():
    data = request.get_json() or {}
    name = data.get("name", "Accredited Lending Branch")
    p_type = data.get("type", "PSB")
    npa_rate = float(data.get("npa_rate", 0.04))
    quota = data.get("remaining_quota_lakhs", 25)
    tat = data.get("avg_disbursal_days", 20)
    schemes = ", ".join(data.get("supported_schemes", ["Social Credit"]))
    dist = data.get("distance_km", 2.5)

    prompt = f"""
    You are an encouraging, expert community banking advisor helping a first-time entrepreneur.
    Write a specific, friendly, and practical review for this particular branch:
    - Branch: {name}
    - Institution Type: {p_type}
    - Distance from user: {dist} km
    - Unpaid Loan Rate (NPA): {npa_rate * 100:.1f}% 
    - Available Government Loan Funds: ₹{quota} Lakhs
    - Approval & Disbursal Speed: ~{tat} Days
    - Available Schemes: {schemes}

    CRITICAL RULES:
    1. Do NOT use complex banking jargon. Keep it conversational.
    2. Make the review 100% specific to {name}.
    3. Format the response with exactly these 4 clear bullet points:
       • Best Suited For: (What kind of business or project this specific branch funds best)
       • Why Their Numbers Help You: (Explain in simple words why low unpaid loans and ₹{quota}L available quota makes getting approved easy here)
       • Approval Speed: (State the ~{tat} days timeline clearly)
       • Next Step / Who to Ask For: (Which specific counter or officer to meet)
    """
    
    if ai_model:
        try:
            response = ai_model.generate_content(
                prompt,
                generation_config={"temperature": 0.8}
            )
            if response and response.text: 
                return jsonify({"review": response.text.strip()})
        except Exception as e:
            print("Gemini API Error:", e)

    return jsonify({"review": f"• Best Suited For: Priority community financing under {schemes}.\n• Why Their Numbers Help You: Clean recovery record ({npa_rate * 100:.1f}%) with ₹{quota} Lakhs unexhausted funding.\n• Approval Speed: Approximately {tat} days.\n• Next Step: Visit the desk directly."})

# -------------------------------------------------------------
# 3. EMI CALCULATOR
# -------------------------------------------------------------
@app.route("/calculator")
@app.route("/calculator/")
def serve_calculator_root():
    return send_from_directory(DIST_DIR, "index.html")

@app.route("/calculator/<path:filename>")
def serve_calculator_files(filename):
    target_path = os.path.join(DIST_DIR, filename)
    if os.path.exists(target_path):
        return send_from_directory(DIST_DIR, filename)
    return send_from_directory(DIST_DIR, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)