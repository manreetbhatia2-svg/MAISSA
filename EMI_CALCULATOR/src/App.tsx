import React, { useState, useEffect } from "react";
import { EmiCalculator } from "./components/EmiCalculator";

export default function App() {
  const [scheme, setScheme] = useState<string>("");
  const [amount, setAmount] = useState<number | null>(null);
  const [interest, setInterest] = useState<number | null>(null);

  // Extract URL parameters passed from Scheme Matcher or Channel Locator
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlScheme = params.get("scheme");
    const urlAmount = params.get("amount");
    const urlInterest = params.get("interest");

    if (urlScheme) setScheme(decodeURIComponent(urlScheme));
    if (urlAmount && !isNaN(Number(urlAmount))) setAmount(Number(urlAmount));
    if (urlInterest && !isNaN(Number(urlInterest))) setInterest(Number(urlInterest));

    // Auto-fill calculator inputs in case the child component uses standard form fields
    const timer = setTimeout(() => {
      if (urlAmount) {
        const amountInputs = document.querySelectorAll<HTMLInputElement>(
          'input[type="number"], input[name*="amount"], input[id*="amount"], input[type="range"]'
        );
        if (amountInputs.length > 0) {
          amountInputs[0].value = urlAmount;
          amountInputs[0].dispatchEvent(new Event("input", { bubbles: true }));
          amountInputs[0].dispatchEvent(new Event("change", { bubbles: true }));
        }
      }
      if (urlInterest) {
        const rateInputs = document.querySelectorAll<HTMLInputElement>(
          'input[name*="rate"], input[name*="interest"], input[id*="rate"], input[id*="interest"]'
        );
        if (rateInputs.length > 0) {
          rateInputs[0].value = urlInterest;
          rateInputs[0].dispatchEvent(new Event("input", { bubbles: true }));
          rateInputs[0].dispatchEvent(new Event("change", { bubbles: true }));
        }
      }
    }, 400);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "#F8FAFC" }}>
      {/* Top Global Ecosystem Navigation Header */}
      <nav
        style={{
          height: "56px",
          background: "#161538",
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 28px",
          position: "sticky",
          top: 0,
          zIndex: 99999,
          boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
        }}
      >
        <a
          href="http://127.0.0.1:5000"
          style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none" }}
        >
          <div
            style={{
              width: "32px",
              height: "32px",
              background: "linear-gradient(135deg, #4F46E5, #818CF8)",
              borderRadius: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFFFFF",
              fontWeight: 800,
              fontSize: "15px",
            }}
          >
            M
          </div>
          <span style={{ color: "#FFFFFF", fontWeight: 800, fontSize: "15px", letterSpacing: "-0.2px" }}>
            MAISSA{" "}
            <span style={{ fontSize: "11px", color: "#818CF8", fontWeight: 600, marginLeft: "4px" }}>
              Credit Ecosystem
            </span>
          </span>
        </a>

        <div style={{ display: "flex", gap: "10px" }}>
          <a
            href="http://127.0.0.1:5000"
            style={{
              padding: "6px 14px",
              borderRadius: "8px",
              fontSize: "12px",
              fontWeight: 700,
              textDecoration: "none",
              color: "#FFFFFF",
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.12)",
              transition: "all 0.2s ease",
            }}
          >
            1. Scheme Matcher
          </a>
          <a
            href="/locator"
            style={{
              padding: "6px 14px",
              borderRadius: "8px",
              fontSize: "12px",
              fontWeight: 700,
              textDecoration: "none",
              color: "#FFFFFF",
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.12)",
              transition: "all 0.2s ease",
            }}
          >
            2. Channel Locator
          </a>
          <a
  href="/calculator/"
  style={{
    padding: "6px 14px",
    borderRadius: "8px",
    fontSize: "12px",
    fontWeight: 700,
    textDecoration: "none",
    color: "#FFFFFF",
    background: "#4F46E5",
    border: "1px solid #4F46E5",
  }}
>
  3. EMI Calculator
</a>
        </div>
      </nav>

      {/* Dynamic Affirmative Context Notification Strip */}
      {scheme && (
        <aside
          aria-label="Affirmative Scheme Subsidy Notice"
          style={{
            background: "linear-gradient(90deg, #1E1B4B 0%, #312E81 100%)",
            color: "#FFFFFF",
            padding: "10px 28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "13px",
            borderBottom: "1px solid #4338CA",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span
              style={{
                background: "#10B981",
                color: "#FFFFFF",
                fontSize: "10.5px",
                fontWeight: 800,
                padding: "2px 8px",
                borderRadius: "6px",
                textTransform: "uppercase",
              }}
            >
              Affirmative Subvention
            </span>
            <span>
              Pre-filled for: <strong>{scheme}</strong>
              {amount ? ` • Cap: ₹${amount.toLocaleString("en-IN")}` : ""}
              {interest ? ` • Concessional Rate: ${interest}% p.a.` : ""}
            </span>
          </div>

          <a
            href={`/locator/?scheme=${encodeURIComponent(scheme)}`}
            style={{
              color: "#A5B4FC",
              textDecoration: "none",
              fontWeight: 700,
              fontSize: "12px",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            📍 Find Disbursal Branches →
          </a>
        </aside>
      )}

      {/* Child EMI Calculator Rendered with Props */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <EmiCalculator
          loanType="home"
          {...({
            initialAmount: amount,
            initialInterest: interest,
            schemeName: scheme,
          } as any)}
        />
      </main>
    </div>
  );
}