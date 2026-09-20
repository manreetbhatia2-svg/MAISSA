import { useMemo, useState } from "react";
import { calculatePrepayment, formatINR } from "../lib/emi";
import type { EmiInput } from "../lib/emi";
import { en } from "../i18n/en";

interface Props {
  input: EmiInput;
}

export function PrepaymentSimulator({ input }: Props) {
  const [lumpSum, setLumpSum] = useState(0);
  const [month, setMonth] = useState(12);
  const [extraMonthly, setExtraMonthly] = useState(0);

  const result = useMemo(
    () => calculatePrepayment(input, { lumpSum, lumpSumMonth: month, extraMonthly }),
    [input, lumpSum, month, extraMonthly]
  );

  const maxMonth = Math.max(1, input.tenureMonths);

  return (
    <section className="tool-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{en.prepayment}</p>
          <p className="helper">Model optional payments against the same reducing-balance loan.</p>
        </div>
      </div>

      <div className="two-controls">
        <label className="field-label">
          {en.lumpSum}
          <input
            className="field-input mt-2"
            type="number"
            min={0}
            step={1000}
            value={lumpSum}
            onChange={(e) => setLumpSum(Math.max(0, Number(e.target.value)))}
          />
        </label>

        <label className="field-label">
          {en.prepaymentMonth}
          <input
            className="field-input mt-2"
            type="number"
            min={1}
            max={maxMonth}
            step={1}
            value={Math.min(month, maxMonth)}
            onChange={(e) => setMonth(Math.min(maxMonth, Math.max(1, Number(e.target.value))))}
          />
        </label>
      </div>

      <label className="field-label block mt-5">
        {en.extraMonthly}
        <input
          className="field-input mt-2"
          type="number"
          min={0}
          step={500}
          value={extraMonthly}
          onChange={(e) => setExtraMonthly(Math.max(0, Number(e.target.value)))}
        />
      </label>

      <div className="prepayment-results">
        <div>
          <span className="metric-label">{en.interestSaved}</span>
          <strong>{formatINR(result.interestSaved)}</strong>
        </div>
        <div>
          <span className="metric-label">{en.monthsReduced}</span>
          <strong>{result.monthsReduced}</strong>
        </div>
      </div>
    </section>
  );
}
