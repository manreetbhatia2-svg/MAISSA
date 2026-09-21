import { en } from "../i18n/en";
import presets from "../data/loanPresets.json";
import type { TenureUnit } from "../lib/emi";

export type LoanType = keyof typeof presets;

export interface InputValues {
  amount: number;
  annualRate: number;
  tenureValue: number;
  tenureUnit: TenureUnit;
}

interface Props {
  loanType: LoanType;
  values: InputValues;
  errors: Record<string, string>;
  onLoanTypeChange: (type: LoanType) => void;
  onChange: (values: Partial<InputValues>) => void;
}

export function LoanInputs({
  loanType,
  values,
  errors,
  onLoanTypeChange,
  onChange,
}: Props) {
  const preset = presets[loanType];

  const amountInput = (
    <input
      id="loan-amount-number"
      aria-describedby="loan-amount-help loan-amount-error"
      className="field-input"
      type="number"
      min={preset.amount.min}
      max={preset.amount.max}
      step={preset.amount.step}
      value={values.amount}
      onChange={(e) => onChange({ amount: Number(e.target.value) })}
    />
  );

  return (
    <section className="space-y-7">
      <div>
        <label htmlFor="loan-type" className="field-label">{en.loanType}</label>
        <select
          id="loan-type"
          className="field-input"
          value={loanType}
          onChange={(e) => onLoanTypeChange(e.target.value as LoanType)}
        >
          {(Object.keys(presets) as LoanType[])
  .filter((type) => type === "education" || type === "business")
  .map((type) => (
    <option key={type} value={type}>
      {presets[type].label}
    </option>
  ))}
        </select>
      </div>

      <div className="control-block">
        <div className="field-heading">
          <label htmlFor="loan-amount-number" className="field-label">{en.loanAmount}</label>
          <span className="figure">{amountInput}</span>
        </div>
        <input
          id="loan-amount-range"
          className="range-input"
          aria-label={`${en.loanAmount} slider`}
          type="range"
          min={preset.amount.min}
          max={preset.amount.max}
          step={preset.amount.step}
          value={values.amount}
          onChange={(e) => onChange({ amount: Number(e.target.value) })}
        />
        <p id="loan-amount-help" className="helper">
          {new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(preset.amount.min)}
          {" "}to{" "}
          {new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(preset.amount.max)}
        </p>
        {errors.amount && <p id="loan-amount-error" className="error">{errors.amount}</p>}
      </div>

      <div className="control-block">
        <div className="field-heading">
          <label htmlFor="rate-number" className="field-label">{en.annualRate}</label>
          <input
            id="rate-number"
            aria-describedby="rate-error"
            className="small-number"
            type="number"
            min={preset.rate.min}
            max={preset.rate.max}
            step={preset.rate.step}
            value={values.annualRate}
            onChange={(e) => onChange({ annualRate: Number(e.target.value) })}
          />
        </div>
        <input
          id="rate-range"
          className="range-input"
          aria-label={`${en.annualRate} slider`}
          type="range"
          min={preset.rate.min}
          max={preset.rate.max}
          step={preset.rate.step}
          value={values.annualRate}
          onChange={(e) => onChange({ annualRate: Number(e.target.value) })}
        />
        {errors.rate && <p id="rate-error" className="error">{errors.rate}</p>}
      </div>

      <div className="control-block">
        <div className="field-heading">
          <label htmlFor="tenure-number" className="field-label">{en.tenure}</label>
          <div className="flex items-center gap-2">
            <input
              id="tenure-number"
              className="small-number"
              type="number"
              min={values.tenureUnit === "years" ? preset.tenureYears.min : 1}
              max={values.tenureUnit === "years" ? preset.tenureYears.max : preset.tenureYears.max * 12}
              step={1}
              value={values.tenureValue}
              onChange={(e) => onChange({ tenureValue: Number(e.target.value) })}
            />
            <div className="segmented" aria-label="Tenure unit">
              {(["years", "months"] as TenureUnit[]).map((unit) => (
                <button
                  key={unit}
                  type="button"
                  className={values.tenureUnit === unit ? "segment active" : "segment"}
                  aria-pressed={values.tenureUnit === unit}
                  onClick={() => {
                    const months = values.tenureUnit === "years"
                      ? Math.round(values.tenureValue * 12)
                      : values.tenureValue;
                    onChange({
                      tenureUnit: unit,
                      tenureValue: unit === "years" ? Math.max(1, Math.round(months / 12)) : Math.max(1, months),
                    });
                  }}
                >
                  {unit === "years" ? en.years : en.months}
                </button>
              ))}
            </div>
          </div>
        </div>
        <input
          id="tenure-range"
          className="range-input"
          aria-label={`${en.tenure} slider`}
          type="range"
          min={values.tenureUnit === "years" ? preset.tenureYears.min : 1}
          max={values.tenureUnit === "years" ? preset.tenureYears.max : preset.tenureYears.max * 12}
          step={1}
          value={values.tenureValue}
          onChange={(e) => onChange({ tenureValue: Number(e.target.value) })}
        />
        {errors.tenure && <p className="error">{errors.tenure}</p>}
      </div>
    </section>
  );
}
