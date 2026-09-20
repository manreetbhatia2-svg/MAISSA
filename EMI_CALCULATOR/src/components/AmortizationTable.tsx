import { useState } from "react";
import type { AmortizationRow } from "../lib/emi";
import { downloadScheduleCsv, formatINR } from "../lib/emi";
import { en } from "../i18n/en";

interface Props {
  schedule: AmortizationRow[];
}

export function AmortizationTable({ schedule }: Props) {
  const years = Array.from(new Set(schedule.map((row) => row.year)));
  const [openYears, setOpenYears] = useState<Set<number>>(new Set([1]));

  const toggle = (year: number) => {
    setOpenYears((current) => {
      const next = new Set(current);
      if (next.has(year)) next.delete(year);
      else next.add(year);
      return next;
    });
  };

  return (
    <section className="tool-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{en.amortization}</p>
          <p className="helper">Interest is calculated on the opening balance each month.</p>
        </div>
        <button className="secondary-button" type="button" onClick={() => downloadScheduleCsv(schedule)}>
          {en.exportCsv}
        </button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Month</th>
              <th>EMI</th>
              <th>Principal</th>
              <th>Interest</th>
              <th>Balance</th>
            </tr>
          </thead>
          <tbody>
            {years.map((year) => (
              <YearRows
                key={year}
                year={year}
                rows={schedule.filter((row) => row.year === year)}
                open={openYears.has(year)}
                onToggle={() => toggle(year)}
              />
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function YearRows({
  year,
  rows,
  open,
  onToggle,
}: {
  year: number;
  rows: AmortizationRow[];
  open: boolean;
  onToggle: () => void;
}) {
  return (
    <>
      <tr className="year-row">
        <td colSpan={5}>
          <button type="button" className="year-button" onClick={onToggle} aria-expanded={open}>
            <span>Year {year}</span>
            <span>{open ? "−" : "+"}</span>
          </button>
        </td>
      </tr>
      {open && rows.map((row) => (
        <tr key={row.month}>
          <td>{row.month}</td>
          <td>{formatINR(row.emi, 0)}</td>
          <td>{formatINR(row.principal, 0)}</td>
          <td>{formatINR(row.interest, 0)}</td>
          <td>{formatINR(row.closingBalance, 0)}</td>
        </tr>
      ))}
    </>
  );
}
