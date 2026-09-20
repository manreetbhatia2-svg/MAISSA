import os
import json
import math
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configure Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    ai_model = None

# Default seed partners dataset
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
        "supported_schemes": ["Term Loan", "Educational Loan Scheme", "MFS"]
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
        "supported_schemes": ["MFS", "Aajeevika Micro-Finance Yojana", "MSY"]
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
        "supported_schemes": ["Term Loan", "MFS"]
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
        "supported_schemes": ["Term Loan", "MFS", "Educational Loan Scheme"]
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
        "supported_schemes": ["MFS", "Aajeevika Micro-Finance Yojana"]
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
        "supported_schemes": ["Term Loan", "Educational Loan Scheme"]
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
    return render_template("index.html")

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
            if not any(selected_scheme.lower() in s.lower() for s in schemes):
                continue

        dist_km = calculate_haversine(user_lat, user_lng, p["latitude"], p["longitude"])
       
        # Scoring weights: 40% Distance, 30% NPA Health, 20% Quota, 10% Turnaround Speed
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
    p_id = data.get("id", "")
    name = data.get("name", "Accredited Lending Branch")
    p_type = data.get("type", "PSB")
    npa_rate = float(data.get("npa_rate", 0.04))
    quota = data.get("remaining_quota_lakhs", 25)
    tat = data.get("avg_disbursal_days", 20)
    schemes = ", ".join(data.get("supported_schemes", ["Social Credit"]))
    dist = data.get("distance_km", 2.5)

    prompt = f"""
    You are an encouraging, expert community banking advisor helping a first-time or marginalized entrepreneur (SC community).
    Write a specific, friendly, and practical review for this particular branch:
    - Branch: {name}
    - Institution Type: {p_type}
    - Distance from user: {dist} km
    - Unpaid Loan Rate (NPA): {npa_rate * 100:.1f}% (Regional average is 12%)
    - Available Government Loan Funds: ₹{quota} Lakhs
    - Approval & Disbursal Speed: ~{tat} Days
    - Available Schemes: {schemes}

    CRITICAL RULES:
    1. Do NOT use complex banking jargon. Never say "financial headroom" or "debt burden". Instead say things like "The bank has plenty of spare money to lend" or "The manager will not hesitate to approve your file".
    2. Make the review 100% specific to {name} and {p_type}.
       - If it is MPBCDC (State Channelizing Agency), highlight that it is an official Scheduled Caste Development Corporation offering massive government subsidies and lowest interest rates.
       - If it is Fusion Microfinance (NBFC-MFI), highlight its lightning-fast {tat}-day approval for small startup cash without complex collateral.
       - If it is SBI or Bank of Baroda (PSB), highlight their huge ₹{quota}L funding capacity for big machinery or shop expansion.
       - If it is Maharashtra Gramin Bank (RRB), highlight friendly village-level service with minimal red tape.
    3. Format the response with exactly these 4 clear bullet points:
       • Best Suited For: (What kind of business or project this specific branch funds best)
       • Why Their Numbers Help You: (Explain in simple words why low unpaid loans and ₹{quota}L available quota makes getting approved easy here)
       • Approval Speed: (State the ~{tat} days timeline clearly)
       • Next Step / Who to Ask For: (Which specific counter or officer to meet, and what basic documents to bring)
   
    Total length: around 90-110 words. Clear, respectful, and easy to read.
    """

    if ai_model:
        try:
            response = ai_model.generate_content(prompt)
            return jsonify({"review": response.text.strip()})
        except Exception as e:
            print("Gemini API error, switching to tailored fallback:", e)

    # In-depth, simplified bank-specific fallbacks
    bank_specific_fallbacks = {
        "p1": (
            "• Best Suited For: Ideal for larger machinery purchases, commercial transport vehicles, and high-value technical education loans.\n"
            "• Why Their Numbers Help You: SBI Kothrud has a very low unpaid loan rate (3.8%), meaning the branch manager is confident and has an active ₹65 Lakh quota specifically waiting to be sanctioned to small enterprises.\n"
            "• Approval Speed: Around 24 days because of thorough public sector bank documentation.\n"
            "• Next Step / Who to Ask For: Ask directly for the 'SME / Priority Sector Loan Officer'. Carry 6 months of bank statements, your Aadhaar card, caste certificate, and vendor quotations for your machinery."
        ),
        "p2": (
            "• Best Suited For: Best choice for SC community entrepreneurs needing maximum government capital subsidies with little to no collateral.\n"
            "• Why Their Numbers Help You: As an official State Channelizing Agency (MPBCDC), their primary mandate is affirmative social welfare lending. They have ₹38 Lakhs reserved specifically to back community micro-enterprises at low 4% to 5% interest rates.\n"
            "• Approval Speed: Average of 18 days from file verification to fund sanction.\n"
            "• Next Step / Who to Ask For: Go to the 'Welfare Scheme Desk' at Ambedkar Bhavan. Bring your Tehsildar-issued Caste Certificate, Ration Card, and a basic one-page estimate of your business expenses."
        ),
        "p3": (
            "• Best Suited For: Excellent for rural transport, small agro-processing, local retail, and community service centers.\n"
            "• Why Their Numbers Help You: Maharashtra Gramin Bank provides a supportive process with much less red tape than giant commercial banks, backed by an active ₹25 Lakh affirmative loan pool.\n"
            "• Approval Speed: Quick 15-day turnaround for local business applicants.\n"
            "• Next Step / Who to Ask For: Meet the 'Agricultural & Rural Credit Field Officer'. Carry your shop or land agreement, Aadhaar card, and two passport-sized photographs."
        ),
        "p4": (
            "• Best Suited For: Established retail stores, repair workshops, and service businesses requiring working capital under Mudra or Term Loans.\n"
            "• Why Their Numbers Help You: This Deccan Gymkhana branch maintains a strong 4.1% loan recovery rate with ₹42 Lakhs unexhausted quota, giving the manager ready capacity to sanction new files.\n"
            "• Approval Speed: Approximately 20 working days.\n"
            "• Next Step / Who to Ask For: Ask for the 'MSME Desk Relationship Manager'. Bring your business registration (Udyam Aadhaar), PAN card, and community certificate."
        ),
        "p5": (
            "• Best Suited For: Smallest micro-loans (₹20,000 to ₹1,50,000) for home production, tailoring, street vending, and self-help group activities.\n"
            "• Why Their Numbers Help You: Unlike commercial banks that demand collateral, Fusion Microfinance operates on trust-based micro-credit with the lowest default rate (2.1%).\n"
            "• Approval Speed: Ultra-fast 8 days with doorstep document verification.\n"
            "• Next Step / Who to Ask For: Ask for the 'Micro-Credit Loan Coordinator'. You only need your Aadhaar card, voter ID, and active bank passbook."
        ),
        "p6": (
            "• Best Suited For: Small businesses looking to add stock inventory or upgrade shop infrastructure.\n"
            "• Why Their Numbers Help You: Located centrally at Swargate, this branch maintains ₹28 Lakhs in credit reserves dedicated to government-sponsored priority sector programs.\n"
            "• Approval Speed: Standard 22-day public sector processing timeline.\n"
            "• Next Step / Who to Ask For: Head to Counter 3 and ask for the 'Lead Bank Scheme Officer'. Bring your shop address proof, caste document, and cost estimate."
        )
    }

    fallback_text = bank_specific_fallbacks.get(p_id, (
        f"• Best Suited For: Priority community financing under {schemes}.\n"
        f"• Why Their Numbers Help You: Clean recovery record ({npa_rate * 100:.1f}% default rate) with ₹{quota} Lakhs unexhausted funding reserved for eligible community applicants.\n"
        f"• Approval Speed: Approximately {tat} days.\n"
        f"• Next Step / Who to Ask For: Visit the Priority Sector Lending desk directly with your caste certificate and project estimate."
    ))

    return jsonify({"review": fallback_text})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)