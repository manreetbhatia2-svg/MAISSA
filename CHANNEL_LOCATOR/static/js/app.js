// Multilingual Translations Dictionary
const i18n = {
  en: {
    title: "Partner Locator", profile: "Beneficiary Profile", save: "Save Profile",
    locate: "📍 Detect Current Location", scheme: "Target Credit Scheme",
    all: "All Available Schemes", topMatch: "Top Recommended", score: "Match Score",
    quota: "Remaining Quota", npa: "NPA Rate", speed: "Disbursal", directions: "Get Directions →",
    savedMsg: "Profile saved successfully!", finding: "Finding verified partners...",
    noMatches: "No matching active partners found within search radius."
  },
  hi: {
    title: "चैनल पार्टनर लोकेटर", profile: "लाभार्थी प्रोफ़ाइल", save: "प्रोफ़ाइल सहेजें",
    locate: "📍 मेरा स्थान पता करें", scheme: "आवश्यक ऋण योजना",
    all: "सभी उपलब्ध योजनाएं", topMatch: "सर्वोत्तम अनुशंसित", score: "मैच स्कोर",
    quota: "शेष कोटा", npa: "एनपीए दर", speed: "औसत समय", directions: "दिशा-निर्देश प्राप्त करें →",
    savedMsg: "प्रोफ़ाइल सफलतापूर्वक सहेजी गई!", finding: "सत्यापित साझेदार खोजे जा रहे हैं...",
    noMatches: "इस दायरे में कोई सक्रिय पात्र भागीदार नहीं मिला।"
  },
  mr: {
    title: "भागीदार शोधक", profile: "लाभार्थी माहिती", save: "माहिती जतन करा",
    locate: "📍 माझे स्थान शोधा", scheme: "कर्ज योजना निवडा",
    all: "सर्व उपलब्ध योजना", topMatch: "उत्कृष्ट पर्याय", score: "सुसंगतता गुण",
    quota: "शिल्लक निधी", npa: "एनपीए दर", speed: "मंजुरी कालावधी", directions: "रस्ता दाखवा →",
    savedMsg: "माहिती जतन झाली आहे!", finding: "अधिकृत भागीदार शोधत आहे...",
    noMatches: "जवळच्या भागात कोणतेही पात्र भागीदार उपलब्ध नाहीत."
  }
};

let curLang = "en";
let userLat = 18.5204, userLng = 73.8567; // Default coordinates: Pune
let map, userMarker, partnerMarkers = [];

// Initialize the Interactive Leaflet Map
function initMap() {
  map = L.map('map').setView([userLat, userLng], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  userMarker = L.circleMarker([userLat, userLng], {
    radius: 9,
    fillColor: '#2563eb',
    color: '#ffffff',
    weight: 3,
    fillOpacity: 1
  }).addTo(map).bindPopup("<b>Your Location</b>").openPopup();
}

// Switch UI Language Dynamically
function changeLanguage(lang) {
  curLang = lang;
  const t = i18n[lang];
  document.getElementById("txtTitle").innerText = t.title;
  document.getElementById("txtProfileHead").innerText = t.profile;
  document.getElementById("btnSave").innerText = t.save;
  document.getElementById("btnLocate").innerText = t.locate;
  document.getElementById("lblScheme").innerText = t.scheme;
  document.getElementById("optAll").innerText = t.all;
  loadPartners();
}

// Save Profile to LocalStorage & Optional POST to Backend
function saveProfile() {
  const name = document.getElementById("userName").value.trim();
  const type = document.getElementById("userType").value;

  if (!name) {
    alert("Please enter a name first.");
    return;
  }

  localStorage.setItem("sih_name", name);
  localStorage.setItem("sih_type", type);

  // Background sync if backend is active
  fetch("/api/user/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_name: name, user_type: type })
  }).catch(() => console.log("Profile stored locally in browser."));

  alert(i18n[curLang].savedMsg);
}

// Detect User Location using HTML5 Geolocation API
function locateUser() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }
  document.getElementById("locText").innerText = "Detecting GPS coordinates...";
  navigator.geolocation.getCurrentPosition(
    pos => {
      userLat = pos.coords.latitude;
      userLng = pos.coords.longitude;
      userMarker.setLatLng([userLat, userLng]);
      map.setView([userLat, userLng], 13);
      document.getElementById("locText").innerText = `Located: (${userLat.toFixed(3)}, ${userLng.toFixed(3)})`;
      loadPartners();
    },
    () => {
      document.getElementById("locText").innerText = "GPS access denied. Using Pune Center.";
      loadPartners();
    }
  );
}

// Load Partners from Python Backend API (with built-in fallback)
async function loadPartners() {
  const scheme = document.getElementById("schemeSelect").value;
  const list = document.getElementById("resultsList");
  const t = i18n[curLang];
  list.innerHTML = `<p style="font-size:12px; color:#64748b; padding:10px;">${t.finding}</p>`;

  partnerMarkers.forEach(m => map.removeLayer(m));
  partnerMarkers = [];

  let partners = [];

  try {
    // Queries your Python Flask Server
    const res = await fetch(`/api/partners/locate?lat=${userLat}&lng=${userLng}&scheme=${encodeURIComponent(scheme)}`);
    const data = await res.json();
    partners = data.data;
  } catch (err) {
    console.warn("Backend server not reached on localhost:5002. Using fallback preview data:", err);
    // Offline preview data so her UI renders without requiring the server
    partners = [
      {
        name: "State Bank of India - Kothrud SME Branch", type: "PSB", latitude: 18.5074, longitude: 73.8077,
        address: "Paud Road, Kothrud, Pune", distance_km: 5.36, routing_score: 80.9,
        remaining_quota_lakhs: 65.0, npa_rate: 0.038, avg_disbursal_days: 24,
        directions_url: "https://www.google.com/maps/dir/?api=1&destination=18.5074,73.8077"
      },
      {
        name: "Mahatma Phule Backward Class Dev Corp (MPBCDC)", type: "SCA", latitude: 18.5204, longitude: 73.8567,
        address: "Ambedkar Bhavan, Camp, Pune", distance_km: 0.0, routing_score: 78.7,
        remaining_quota_lakhs: 38.0, npa_rate: 0.045, avg_disbursal_days: 18,
        directions_url: "https://www.google.com/maps/dir/?api=1&destination=18.5204,73.8567"
      }
    ];
  }

  list.innerHTML = "";
  if (!partners || partners.length === 0) {
    list.innerHTML = `<p style="font-size:12px; color:#ef4444; padding:10px;">${t.noMatches}</p>`;
    return;
  }

  partners.forEach((p, idx) => {
    const isTop = idx === 0;

    // Pin on Leaflet Map (Green for top match, Blue for others)
    const marker = L.circleMarker([p.latitude, p.longitude], {
      radius: isTop ? 10 : 8,
      fillColor: isTop ? "#16a34a" : "#0284c7",
      color: isTop ? "#fef08a" : "#ffffff",
      weight: 2,
      fillOpacity: 0.95
    }).addTo(map);

    marker.bindPopup(`
      <b>${p.name}</b><br>
      ${p.address}<br>
      <a href="${p.directions_url}" target="_blank" style="color:#2563eb; font-weight:bold;">${t.directions}</a>
    `);
    partnerMarkers.push(marker);

    // Sidebar Result Card
    const card = document.createElement("div");
    card.className = `partner-card ${isTop ? 'top-choice' : ''}`;
    card.innerHTML = `
      ${isTop ? `<span class="badge badge-top">${t.topMatch}</span>` : ''}
      <span class="badge badge-type">${p.type}</span>
      <span class="score-badge">${t.score}: ${p.routing_score}%</span>
      <div class="partner-name">${p.name}</div>
      <div class="partner-address">${p.address} (${p.distance_km} km)</div>
      <div class="stats-row">
        <div>${t.quota}: <strong>₹${p.remaining_quota_lakhs}L</strong></div>
        <div>${t.npa}: <strong>${(p.npa_rate * 100).toFixed(1)}%</strong></div>
        <div>${t.speed}: <strong>~${p.avg_disbursal_days}d</strong></div>
      </div>
      <a class="direction-btn" target="_blank" href="${p.directions_url}">${t.directions}</a>
    `;
    list.appendChild(card);
  });
}

// Run automatically on window load
window.onload = () => {
  initMap();
  const saved = localStorage.getItem("sih_name");
  if (saved) document.getElementById("userName").value = saved;
  loadPartners();
};