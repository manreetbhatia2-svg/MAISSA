import { describe, expect, it } from "vitest";
import {
  calculateEmi,
  calculateLoan,
  calculatePrepayment,
  calculateSchedule,
  amountInWords,
} from "./emi";

describe("calculateEmi", () => {
  it("calculates ₹10 lakh at 9% for 20 years", () => {
    const emi = calculateEmi({
      principal: 1_000_000,
      annualRate: 9,
      tenureMonths: 240,
    });
    expect(emi).toBeCloseTo(8997.38, 1);
  });

  it("handles 0% interest", () => {
    expect(
      calculateEmi({ principal: 120_000, annualRate: 0, tenureMonths: 12 })
    ).toBe(10_000);
  });

  it("handles a one-month tenure", () => {
    expect(
      calculateLoan({ principal: 50_000, annualRate: 12, tenureMonths: 1 })
        .schedule.at(-1)?.closingBalance
    ).toBe(0);
  });
});

describe("schedule", () => {
  it("ends with exactly zero balance", () => {
    const schedule = calculateSchedule({
      principal: 1_000_000,
      annualRate: 9,
      tenureMonths: 240,
    });
    expect(schedule.at(-1)?.closingBalance).toBe(0);
  });

  it("has no negative balances", () => {
    const schedule = calculateSchedule({
      principal: 500_000,
      annualRate: 13.5,
      tenureMonths: 37,
    });
    expect(schedule.every((row) => row.closingBalance >= 0)).toBe(true);
  });
});

describe("prepayment", () => {
  const input = { principal: 1_000_000, annualRate: 10, tenureMonths: 120 };

  it("saves interest with a lump sum", () => {
    const result = calculatePrepayment(input, {
      lumpSum: 100_000,
      lumpSumMonth: 12,
    });
    expect(result.interestSaved).toBeGreaterThan(0);
    expect(result.monthsReduced).toBeGreaterThan(0);
  });

  it("saves interest with extra monthly payments", () => {
    const result = calculatePrepayment(input, { extraMonthly: 2_000 });
    expect(result.interestSaved).toBeGreaterThan(0);
    expect(result.monthsReduced).toBeGreaterThan(0);
  });
});

describe("amountInWords", () => {
  it("uses Indian lakh/crore units", () => {
    expect(amountInWords(1_250_000)).toBe("Twelve Lakh Fifty Thousand Rupees");
    expect(amountInWords(10_000_000)).toBe("One Crore Rupees");
  });
});
