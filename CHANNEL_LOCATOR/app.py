import os
import json
import math
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# -------------------------------------------------------------
# PATH TO MASTER COMBINED SCHEMES DATASET
# -------------------------------------------------------------
COMBINED_SCHEMES_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "combined_schemes.json")
)

def load_combined_schemes():
    """Loads the master schemes from combined_schemes.json"""
    if os.path.exists(COMBINED_SCHEMES_FILE):
        try:
            with open(COMBINED_SCHEMES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("schemes", [])
        except Exception as e:
            print(f"Error loading combined_schemes.json: {e}")
    return []

# -------------------------------------------------------------
# DYNAMIC GEMINI MODEL AUTO-DETECTION & CONFIGURATION
# -------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ai_model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        supported_models = [
            m.name for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        chosen_model = next(
            (m for m in supported_models if "flash" in m),
            supported_models[0] if supported_models else "gemini-1.5-flash"
        )
        ai_model = genai.GenerativeModel(chosen_model)
        print(f"✓ Gemini AI Model Active: {chosen_model}")
    except Exception as e:
        print(f"Gemini configuration error: {e}")
        ai_model = None
else:
    print("Gemini Notice: GEMINI_API_KEY environment variable not detected.")

# -------------------------------------------------------------
# DEFAULT SEED PARTNERS DATASET (Aligned with Schemes)
# -------------------------------------------------------------
DEFAULT_PARTNERS = [
    {
        "id": "p1",
        "name": "State Bank of India - Kothrud SME Branch",
        "type": "PSB",
        "latitude": 18.5074,
        "longitude": 73.8077,
        "address": "Paud Road, Kothrud, Pune",
        "remaining_quota_lakhs": 65.0,
        "npa_rate": 0.038,
        "avg_disbursal_days": 24,
        "supported_schemes": [
            "Term Loan (TL)", 
            "Educational Loan Scheme (ELS)", 
            "Micro Finance Scheme (MFS)"
        ]
    },
    {
        "id": "p2",
        "name": "Mahatma Phule Backward Class Dev Corp (MPBCDC)",
        "type": "SCA",
        "latitude": 18.5126,
        "longitude": 73.8782,
        "address": "Ambedkar Bhavan, Camp, Pune",
        "remaining_quota_lakhs": 38.0,
        "npa_rate": 0.045,
        "avg_disbursal_days": 18,
        "supported_schemes": [
            "Micro Finance Scheme (MFS)", 
            "Aajeevika Micro-Finance Yojana (AMY)", 
            "Government of India Post-Matric Scholarship",
            "Pre-Matric Scholarship for Children of Parents Engaged in Unclean Occupations"
        ]
    },
    {
        "id": "p3",
        "name": "Maharashtra Gramin Bank - Hadapsar",
        "type": "RRB",
        "latitude": 18.5089,
        "longitude": 73.9260,
        "address": "Pune-Solapur Rd, Hadapsar, Pune",
        "remaining_quota_lakhs": 25.0,
        "npa_rate": 0.049,
        "avg_disbursal_days": 15,
        "supported_schemes": [
            "Term Loan (TL)", 
            "Micro Finance Scheme (MFS)", 
            "Udyam Nidhi Yojana (UNY)"
        ]
    },
    {
        "id": "p4",
        "name": "Bank of Baroda - Deccan Gymkhana Branch",
        "type": "PSB",
        "latitude": 18.5177,
        "longitude": 73.8438,
        "address": "Ashok Chambers, Jangali Maharaj Rd, Pune",
        "remaining_quota_lakhs": 42.0,
        "npa_rate": 0.041,
        "avg_disbursal_days": 20,
        "supported_schemes": [
            "Term Loan (TL)", 
            "Micro Finance Scheme (MFS)", 
            "Educational Loan Scheme (ELS)", 
            "Udyam Nidhi Yojana (UNY)"
        ]
    },
    {
        "id": "p5",
        "name": "Fusion Microfinance - Shivajinagar Hub",
        "type": "NBFC-MFI",
        "latitude": 18.5314,
        "longitude": 73.8446,
        "address": "FC Road, Shivajinagar, Pune",
        "remaining_quota_lakhs": 15.0,
        "npa_rate": 0.021,
        "avg_disbursal_days": 8,
        "supported_schemes": [
            "Micro Finance Scheme (MFS)", 
            "Aajeevika Micro-Finance Yojana (AMY)"
        ]
    },
    {
        "id": "p6",
        "name": "Central Bank of India - Swargate Branch",
        "type": "PSB",
        "latitude": 18.5018,
        "longitude": 73.8586,
        "address": "Swargate Chowk, Pune",
        "remaining_quota_lakhs": 28.0,
        "npa_rate": 0.052,
        "avg_disbursal_days": 22,
        "supported_schemes": [
            "Term Loan (TL)", 
            "Educational Loan Scheme (ELS)", 
            "Government of India Post-Matric Scholarship"
        ]
    }
]

def load_partners_data():
    file_path = os.path.join(os.path.dirname(__file__), "data", "partners.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_PARTNERS
    return DEFAULT_PARTNERS

def calculate_haversine(lat1, lon1, lat2, lon2):
    r = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)

@app.route("/")
def index():
    schemes_data = load_combined_schemes()
    scheme_names = [s["name"] for s in schemes_data]
    return render_template("index.html", schemes=scheme_names)

@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    schemes_data = load_combined_schemes()
    return jsonify({"success": True, "schemes": schemes_data})

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

        dist_km = calculate_haversine(user_lat, user_lng, p["latitude"], p["longitude"])
        
        dist_score = max(0, round((1 - dist_km / 30.0) * 100))
        npa_score = max(0, round((1 - p["npa_rate"] / 0.15) * 100))
        quota_score = min(100, round((p["remaining_quota_lakhs"] / 50.0) * 100))
        tat_score = max(0, round((1 - p["avg_disbursal_days"] / 30.0) * 100))

        composite_score = round(
            (0.40 * dist_score) +
            (0.30 * npa_score) +
            (0.20 * quota_score) +
            (0.10 * tat_score),
            1
        )

        item = dict(p)
        item["distance_km"] = dist_km
        item["routing_score"] = composite_score
        item["breakdown"] = {
            "proximity": dist_score,
            "npa": npa_score,
            "quota": quota_score,
            "tat": tat_score
        }
        scored_partners.append(item)

    scored_partners.sort(key=lambda x: x["routing_score"], reverse=True)
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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)