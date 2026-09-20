export type TenureUnit = "years" | "months";

export interface EmiInput {
  principal: number;
  annualRate: number;
  tenureMonths: number;
}

export interface AmortizationRow {
  month: number;
  year: number;
  openingBalance: number;
  emi: number;
  principal: number;
  interest: number;
  closingBalance: number;
}

export interface PrepaymentInput {
  lumpSum?: number;
  lumpSumMonth?: number;
  extraMonthly?: number;
}

export interface LoanCalculation {
  emi: number;
  totalInterest: number;
  totalPayable: number;
  schedule: AmortizationRow[];
}

export interface PrepaymentResult extends LoanCalculation {
  interestSaved: number;
  monthsReduced: number;
}

const roundPaise = (value: number) => Math.round((value + Number.EPSILON) * 100) / 100;

export function calculateEmi({ principal, annualRate, tenureMonths }: EmiInput): number {
  if (principal <= 0 || tenureMonths <= 0) return 0;
  if (annualRate === 0) return roundPaise(principal / tenureMonths);

  const monthlyRate = annualRate / 100 / 12;
  const factor = Math.pow(1 + monthlyRate, tenureMonths);
  return roundPaise((principal * monthlyRate * factor) / (factor - 1));
}

export function calculateSchedule(input: EmiInput): AmortizationRow[] {
  const { principal, annualRate, tenureMonths } = input;
  if (principal <= 0 || tenureMonths <= 0) return [];

  const scheduledEmi = calculateEmi(input);
  const monthlyRate = annualRate / 100 / 12;
  let balance = roundPaise(principal);
  const schedule: AmortizationRow[] = [];

  for (let month = 1; month <= tenureMonths && balance > 0; month++) {
    const openingBalance = balance;
    const interest = roundPaise(openingBalance * monthlyRate);

    let payment = scheduledEmi;
    let principalPaid = roundPaise(payment - interest);

    if (month === tenureMonths || principalPaid > openingBalance) {
      principalPaid = openingBalance;
      payment = roundPaise(principalPaid + interest);
    }

    // Floating-point and paise rounding protection.
    principalPaid = Math.max(0, Math.min(principalPaid, openingBalance));
    const closingBalance = roundPaise(Math.max(0, openingBalance - principalPaid));

    schedule.push({
      month,
      year: Math.ceil(month / 12),
      openingBalance,
      emi: roundPaise(payment),
      principal: principalPaid,
      interest,
      closingBalance,
    });

    balance = closingBalance;
  }

  return schedule;
}

export function calculateLoan(input: EmiInput): LoanCalculation {
  const schedule = calculateSchedule(input);
  const totalInterest = roundPaise(schedule.reduce((sum, row) => sum + row.interest, 0));
  const totalPayable = roundPaise(schedule.reduce((sum, row) => sum + row.emi, 0));

  return {
    emi: schedule[0]?.emi ?? 0,
    totalInterest,
    totalPayable,
    schedule,
  };
}

export function calculatePrepayment(
  input: EmiInput,
  prepayment: PrepaymentInput
): PrepaymentResult {
  const base = calculateLoan(input);
  const lumpSum = Math.max(0, prepayment.lumpSum ?? 0);
  const lumpSumMonth = Math.max(1, Math.floor(prepayment.lumpSumMonth ?? 1));
  const extraMonthly = Math.max(0, prepayment.extraMonthly ?? 0);

  if (lumpSum === 0 && extraMonthly === 0) {
    return { ...base, interestSaved: 0, monthsReduced: 0 };
  }

  const monthlyRate = input.annualRate / 100 / 12;
  const baseEmi = base.emi;
  const schedule: AmortizationRow[] = [];
  let balance = roundPaise(input.principal);

  for (let month = 1; month <= input.tenureMonths && balance > 0; month++) {
    const openingBalance = balance;
    const interest = roundPaise(openingBalance * monthlyRate);
    let payment = roundPaise(baseEmi + extraMonthly);
    let principalPaid = roundPaise(payment - interest);

    if (principalPaid <= 0) {
      // Prevent an infinite loop for pathological inputs.
      payment = interest;
      principalPaid = 0;
    }

    if (lumpSum > 0 && month === lumpSumMonth) {
      const lump = Math.min(lumpSum, Math.max(0, openingBalance - principalPaid));
      principalPaid = roundPaise(principalPaid + lump);
      payment = roundPaise(payment + lump);
    }

    if (principalPaid >= openingBalance) {
      principalPaid = openingBalance;
      payment = roundPaise(principalPaid + interest);
    }

    const closingBalance = roundPaise(Math.max(0, openingBalance - principalPaid));

    schedule.push({
      month,
      year: Math.ceil(month / 12),
      openingBalance,
      emi: payment,
      principal: principalPaid,
      interest,
      closingBalance,
    });

    balance = closingBalance;
  }

  const totalInterest = roundPaise(schedule.reduce((sum, row) => sum + row.interest, 0));
  const totalPayable = roundPaise(schedule.reduce((sum, row) => sum + row.emi, 0));
  const monthsReduced = Math.max(0, base.schedule.length - schedule.length);

  return {
    emi: schedule[0]?.emi ?? 0,
    totalInterest,
    totalPayable,
    schedule,
    interestSaved: roundPaise(Math.max(0, base.totalInterest - totalInterest)),
    monthsReduced,
  };
}

export function formatINR(value: number, maximumFractionDigits = 0): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: maximumFractionDigits,
    maximumFractionDigits: maximumFractionDigits,
  }).format(Math.round(value * 100) / 100);
}

export function formatNumberIN(value: number, maximumFractionDigits = 0): string {
  return new Intl.NumberFormat("en-IN", {
    minimumFractionDigits: maximumFractionDigits,
    maximumFractionDigits: maximumFractionDigits,
  }).format(value);
}

export function amountInWords(value: number): string {
  const n = Math.round(value);
  if (n === 0) return "Zero rupees";

  const ones = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen"
  ];
  const tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];

  const under100 = (x: number): string => {
    if (x < 20) return ones[x];
    return `${tens[Math.floor(x / 10)]}${x % 10 ? ` ${ones[x % 10]}` : ""}`;
  };

  const under1000 = (x: number): string => {
    if (x < 100) return under100(x);
    return `${ones[Math.floor(x / 100)]} Hundred${x % 100 ? ` ${under100(x % 100)}` : ""}`;
  };

  const parts: string[] = [];
  let remaining = n;

  const crore = Math.floor(remaining / 10000000);
  if (crore) {
    parts.push(`${under1000(crore)} Crore`);
    remaining %= 10000000;
  }

  const lakh = Math.floor(remaining / 100000);
  if (lakh) {
    parts.push(`${under1000(lakh)} Lakh`);
    remaining %= 100000;
  }

  const thousand = Math.floor(remaining / 1000);
  if (thousand) {
    parts.push(`${under1000(thousand)} Thousand`);
    remaining %= 1000;
  }

  if (remaining) parts.push(under1000(remaining));

  return `${parts.join(" ")} Rupees`;
}

export function downloadScheduleCsv(schedule: AmortizationRow[], filename = "emi-amortization.csv"): void {
  const headers = ["Month", "Year", "Opening Balance", "EMI", "Principal", "Interest", "Closing Balance"];
  const rows = schedule.map((row) => [
    row.month,
    row.year,
    row.openingBalance.toFixed(2),
    row.emi.toFixed(2),
    row.principal.toFixed(2),
    row.interest.toFixed(2),
    row.closingBalance.toFixed(2),
  ]);

  const csv = [headers, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(","))
    .join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
