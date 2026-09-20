import { DonutChart } from "./DonutChart";
import { formatINR, amountInWords } from "../lib/emi";
import { en } from "../i18n/en";

interface Props {
  principal: number;
  emi: number;
  totalInterest: number;
  totalPayable: number;
}

export function ResultSummary({ principal, emi, totalInterest, totalPayable }: Props) {
  return (
    <section className="summary-section">
      <div>
        <p className="eyebrow">{en.monthlyEmi}</p>
        <div className="emi-figure tabular">{formatINR(emi)}</div>
        <p className="helper">{en.interestHelper}</p>
      </div>

      <div className="summary-grid">
        <div>
          <p className="metric-label">{en.totalInterest}</p>
          <p className="metric-value">{formatINR(totalInterest)}</p>
        </div>
        <div>
          <p className="metric-label">{en.totalPayable}</p>
          <p className="metric-value">{formatINR(totalPayable)}</p>
        </div>
      </div>

      <div className="chart-section">
        <div className="section-heading">
          <h3>Payment split</h3>
        </div>
        <DonutChart principal={principal} interest={totalInterest} />
        <div className="legend">
          <span><i className="legend-dot principal" />Principal <b>{formatINR(principal)}</b></span>
          <span><i className="legend-dot interest" />Interest <b>{formatINR(totalInterest)}</b></span>
        </div>
      </div>

      <div className="amount-words">
        <span className="metric-label">{en.amountWords}</span>
        <span>{amountInWords(principal)}</span>
      </div>
    </section>
  );
}
