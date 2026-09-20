import { useEffect, useMemo, useState } from "react";
import presets from "../data/loanPresets.json";
import schemes from "../data/schemes.json";
import { en } from "../i18n/en";
import {
  amountInWords,
  calculateLoan,
  formatINR,
  type TenureUnit,
} from "../lib/emi";
import { LoanInputs, type InputValues, type LoanType } from "./LoanInputs";
import { ResultSummary } from "./ResultSummary";
import { OutstandingChart } from "./OutstandingChart";
import { AmortizationTable } from "./AmortizationTable";
import { PrepaymentSimulator } from "./PrepaymentSimulator";
import { CompareView } from "./CompareView";

export interface EmiCalculatorProps {
  initialValues?: Partial<InputValues>;
  loanType?: LoanType;
  schemeId?: string;
  onChange?: (value: EmiCalculatorChange) => void;
}

export interface EmiCalculatorChange {
  values: InputValues;
  loanType: LoanType;
  schemeId: string;
  emi: number;
  totalInterest: number;
  totalPayable: number;
}

const defaultType: LoanType = "home";

function defaultValues(type: LoanType): InputValues {
  const preset = presets[type];
  return {
    amount: preset.amount.default,
    annualRate: preset.rate.default,
    tenureValue: preset.tenureYears.default,
    tenureUnit: "years",
  };
}

export function EmiCalculator({
  initialValues,
  loanType: initialLoanType = defaultType,
  schemeId: initialSchemeId = "",
  onChange,
}: EmiCalculatorProps) {
  const [loanType, setLoanType] = useState<LoanType>(initialLoanType);
  const [values, setValues] = useState<InputValues>({
    ...defaultValues(initialLoanType),
    ...initialValues,
  });
  const [schemeId, setSchemeId] = useState(initialSchemeId);

  const preset = presets[loanType];
  const tenureMonths = values.tenureUnit === "years" ? values.tenureValue * 12 : values.tenureValue;

  const errors = useMemo(() => {
    const next: Record<string, string> = {};
    if (!Number.isFinite(values.amount) || values.amount < preset.amount.min || values.amount > preset.amount.max) {
      next.amount = en.invalidAmount;
    }
    if (!Number.isFinite(values.annualRate) || values.annualRate < preset.rate.min || values.annualRate > preset.rate.max) {
      next.rate = en.invalidRate;
    }
    if (!Number.isFinite(tenureMonths) || tenureMonths < 1 || tenureMonths > preset.tenureYears.max * 12) {
      next.tenure = en.invalidTenure;
    }
    return next;
  }, [preset, tenureMonths, values.amount, values.annualRate]);

  const calculation = useMemo(() => {
    if (Object.keys(errors).length > 0) {
      return { emi: 0, totalInterest: 0, totalPayable: 0, schedule: [] };
    }
    return calculateLoan({
      principal: values.amount,
      annualRate: values.annualRate,
      tenureMonths,
    });
  }, [errors, tenureMonths, values.amount, values.annualRate]);

  const selectedScheme = schemes.find((scheme) => scheme.id === schemeId);

  const schemeCalculation = useMemo(() => {
    if (!selectedScheme || Object.keys(errors).length > 0) return null;
    const rate = selectedScheme.rate;
    const cappedAmount = Math.min(Math.max(values.amount, selectedScheme.minAmount), selectedScheme.maxAmount);
    return {
      requestedAmount: values.amount,
      calculation: calculateLoan({
        principal: cappedAmount,
        annualRate: rate,
        tenureMonths,
      }),
      subsidy: selectedScheme.subsidy,
      cappedAmount,
    };
  }, [errors, selectedScheme, tenureMonths, values.amount]);

  useEffect(() => {
    onChange?.({
      values,
      loanType,
      schemeId,
      emi: calculation.emi,
      totalInterest: calculation.totalInterest,
      totalPayable: calculation.totalPayable,
    });
  }, [calculation, loanType, onChange, schemeId, values]);

  const updateValues = (patch: Partial<InputValues>) => setValues((current) => ({ ...current, ...patch }));

  const handleLoanType = (type: LoanType) => {
    setLoanType(type);
    setValues(defaultValues(type));
    setSchemeId("");
  };

  return (
    <div className="emi-tool">
      <div className="tool-header">
        <div>
          <p className="eyebrow">Personal finance</p>
          <h1>{en.title}</h1>
        </div>
        <div className="scheme-control">
          <label htmlFor="scheme" className="field-label">{en.scheme}</label>
          <select id="scheme" className="field-input" value={schemeId} onChange={(e) => setSchemeId(e.target.value)}>
            <option value="">{en.selectScheme}</option>
            {schemes.map((scheme) => <option key={scheme.id} value={scheme.id}>{scheme.name}</option>)}
          </select>
        </div>
      </div>

      <div className="tool-layout">
        <main className="tool-left">
          <LoanInputs
            loanType={loanType}
            values={values}
            errors={errors}
            onLoanTypeChange={handleLoanType}
            onChange={updateValues}
          />

          <div className="tool-divider" />

          <PrepaymentSimulator
            input={{
              principal: values.amount,
              annualRate: values.annualRate,
              tenureMonths,
            }}
          />

          <CompareView
            principal={values.amount}
            annualRate={values.annualRate}
            tenureMonths={tenureMonths}
          />
        </main>

        <aside className="tool-right">
          <div className="sticky-summary">
            <ResultSummary
              principal={values.amount}
              emi={calculation.emi}
              totalInterest={calculation.totalInterest}
              totalPayable={calculation.totalPayable}
            />

            {selectedScheme && schemeCalculation && (
              <section className="tool-section scheme-box">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">{selectedScheme.name}</p>
                    <p className="helper">{selectedScheme.description}</p>
                  </div>
                </div>
                <p className="scheme-warning">{en.indicative}</p>
                <div className="summary-grid">
                  <div>
                    <span className="metric-label">{en.regularLoan}</span>
                    <strong>{formatINR(calculation.totalInterest)}</strong>
                  </div>
                  <div>
                    <span className="metric-label">{en.schemeLoan}</span>
                    <strong>{formatINR(schemeCalculation.calculation.totalInterest)}</strong>
                  </div>
                </div>
                <div className="savings-line">
                  <span>{en.schemeSavings}</span>
                  <strong>
                    {formatINR(
                      Math.max(
                        0,
                        calculation.totalInterest -
                        schemeCalculation.calculation.totalInterest +
                        schemeCalculation.subsidy
                      )
                    )}
                  </strong>
                </div>
                <p className="helper">
                  The preset uses ₹{new Intl.NumberFormat("en-IN").format(schemeCalculation.cappedAmount)} as its indicative eligible amount.
                </p>
              </section>
            )}

            <section className="tool-section">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">{en.outstanding}</p>
                  <p className="helper">Balance remaining after each payment.</p>
                </div>
              </div>
              <OutstandingChart schedule={calculation.schedule} />
            </section>

            <AmortizationTable schedule={calculation.schedule} />

            <div className="amount-footnote">
              <span>{en.amountWords}</span>
              <strong>{amountInWords(values.amount)}</strong>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
