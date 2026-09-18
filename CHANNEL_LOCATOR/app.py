import json
import math
import os
import urllib.parse
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Use dynamic relative paths so no local computer paths or IPs are exposed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "partners.json")

# Serve frontend directly so all API calls can be relative
@app.route("/")
def index():
    return render_template("index.html")

def get_partners():
    if not os.path.exists(DATA_PATH):
        # Fallback dataset if partners.json is not yet created
        return [
            {
                "name": "State Bank of India - Kothrud SME Branch", "type": "PSB", 
                "latitude": 18.5074, "longitude": 73.8077,
                "address": "Paud Road, Kothrud, Pune", 
                "remaining_quota_lakhs": 65.0, "npa_rate": 0.038, "avg_disbursal_days": 24,
                "supported_schemes": ["Term Loan", "Educational Loan Scheme", "MFS"]
            },
            {
                "name": "Mahatma Phule Backward Class Dev Corp (MPBCDC)", "type": "SCA", 
                "latitude": 18.5126, "longitude": 73.8782,
                "address": "Ambedkar Bhavan, Camp, Pune", 
                "remaining_quota_lakhs": 38.0, "npa_rate": 0.045, "avg_disbursal_days": 18,
                "supported_schemes": ["MFS", "Aajeevika Micro-Finance Yojana", "MSY"]
            },
            {
                "name": "Maharashtra Gramin Bank - Hadapsar", "type": "RRB", 
                "latitude": 18.5089, "longitude": 73.9260,
                "address": "Pune-Solapur Rd, Hadapsar, Pune", 
                "remaining_quota_lakhs": 25.0, "npa_rate": 0.049, "avg_disbursal_days": 15,
                "supported_schemes": ["Term Loan", "MFS"]
            },
            {
                "name": "Bank of Baroda - Deccan Gymkhana Branch", "type": "PSB", 
                "latitude": 18.5177, "longitude": 73.8438,
                "address": "Ashok Chambers, Jangali Maharaj Rd, Pune", 
                "remaining_quota_lakhs": 42.0, "npa_rate": 0.041, "avg_disbursal_days": 20,
                "supported_schemes": ["Term Loan", "MFS", "Educational Loan Scheme"]
            },
            {
                "name": "Fusion Microfinance - Shivajinagar Hub", "type": "NBFC-MFI", 
                "latitude": 18.5314, "longitude": 73.8446,
                "address": "FC Road, Shivajinagar, Pune", 
                "remaining_quota_lakhs": 15.0, "npa_rate": 0.021, "avg_disbursal_days": 8,
                "supported_schemes": ["MFS", "Aajeevika Micro-Finance Yojana"]
            },
            {
                "name": "Central Bank of India - Swargate Branch", "type": "PSB", 
                "latitude": 18.5018, "longitude": 73.8586,
                "address": "Swargate Chowk, Pune", 
                "remaining_quota_lakhs": 28.0, "npa_rate": 0.052, "avg_disbursal_days": 22,
                "supported_schemes": ["Term Loan", "Educational Loan Scheme"]
            }
        ]
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def calculate_routing_score(distance_km, npa_rate, remaining_quota, disbursal_days):
    norm_dist = max(0.0, 1.0 - (distance_km / 30.0))
    norm_npa = max(0.0, 1.0 - (npa_rate / 0.15))
    norm_quota = min(1.0, remaining_quota / 50.0)
    norm_speed = max(0.0, 1.0 - (disbursal_days / 40.0))

    score = (
        0.40 * norm_dist
        + 0.30 * norm_npa
        + 0.20 * norm_quota
        + 0.10 * norm_speed
    ) * 100

    return round(score, 1)

@app.route("/api/partners/locate", methods=["GET"])
def locate_partners():
    try:
        user_lat = float(request.args.get("lat", 18.5204))
        user_lng = float(request.args.get("lng", 73.8567))
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid coordinates"}), 400

    scheme_filter = request.args.get("scheme", "").strip()
    partners = get_partners()

    active_matches = []
    suspended_count = 0

    for p in partners:
        # Automatic risk filtration
        if p.get("disbursement_status") == "Suspended" or p.get("npa_rate", 0.0) >= 0.15:
            suspended_count += 1
            continue

        if scheme_filter and not any(scheme_filter.lower() in s.lower() for s in p.get("supported_schemes", [])):
            continue

        dist = calculate_distance(user_lat, user_lng, p["latitude"], p["longitude"])
        score = calculate_routing_score(
            dist,
            p.get("npa_rate", 0.05),
            p.get("remaining_quota_lakhs", 10.0),
            p.get("avg_disbursal_days", 20),
        )

        partner_entry = dict(p)
        partner_entry["distance_km"] = dist
        partner_entry["routing_score"] = score
        active_matches.append(partner_entry)

    active_matches.sort(key=lambda x: x["routing_score"], reverse=True)

    return jsonify({
        "status": "success",
        "total_matches": len(active_matches),
        "suspended_filtered": suspended_count,
        "data": active_matches
    })

if __name__ == "__main__":
    # Bound to standard localhost; no IP exposed
    app.run(host="127.0.0.1", port=5002, debug=True, use_reloader=False)