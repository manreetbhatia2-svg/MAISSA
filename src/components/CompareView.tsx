import { useMemo, useState } from "react";
import { calculateLoan, formatINR } from "../lib/emi";
import { en } from "../i18n/en";

interface Props {
  principal: number;
  annualRate: number;
  tenureMonths: number;
}

export function CompareView({ principal, annualRate, tenureMonths }: Props) {
  const [rateB, setRateB] = useState(Math.max(0, annualRate - 1));
  const [monthsB, setMonthsB] = useState(tenureMonths);

  const a = useMemo(() => calculateLoan({ principal, annualRate, tenureMonths }), [principal, annualRate, tenureMonths]);
  const b = useMemo(() => calculateLoan({ principal, annualRate: rateB, tenureMonths: monthsB }), [principal, rateB, monthsB]);

  return (
    <section className="tool-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{en.compare}</p>
          <p className="helper">Compare the current loan with a second rate or tenure.</p>
        </div>
      </div>

      <div className="compare-controls">
        <label className="field-label">
          Scenario B rate
          <input className="small-number mt-2" type="number" min={0} max={50} step={0.05} value={rateB} onChange={(e) => setRateB(Number(e.target.value))} />
        </label>
        <label className="field-label">
          Scenario B tenure (months)
          <input className="small-number mt-2" type="number" min={1} max={600} step={1} value={monthsB} onChange={(e) => setMonthsB(Number(e.target.value))} />
        </label>
      </div>

      <div className="compare-grid">
        <CompareColumn title={en.scenarioA} rate={annualRate} months={tenureMonths} emi={a.emi} interest={a.totalInterest} />
        <CompareColumn title={en.scenarioB} rate={rateB} months={monthsB} emi={b.emi} interest={b.totalInterest} />
      </div>
    </section>
  );
}

function CompareColumn({ title, rate, months, emi, interest }: {
  title: string;
  rate: number;
  months: number;
  emi: number;
  interest: number;
}) {
  return (
    <div className="compare-column">
      <h3>{title}</h3>
      <dl>
        <div><dt>Rate</dt><dd>{rate.toFixed(2)}%</dd></div>
        <div><dt>Tenure</dt><dd>{months} months</dd></div>
        <div><dt>EMI</dt><dd>{formatINR(emi)}</dd></div>
        <div><dt>Total interest</dt><dd>{formatINR(interest)}</dd></div>
      </dl>
    </div>
  );
}
