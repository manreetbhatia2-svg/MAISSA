import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { formatINR } from "../lib/emi";
import type { AmortizationRow } from "../lib/emi";

interface Props {
  schedule: AmortizationRow[];
}

export function OutstandingChart({ schedule }: Props) {
  const data = schedule.map((row) => ({
    month: row.month,
    balance: row.closingBalance,
  }));

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 10, left: 0, bottom: 8 }}>
          <CartesianGrid stroke="#E5E5E0" vertical={false} />
          <XAxis dataKey="month" tickLine={false} axisLine={false} />
          <YAxis
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => `₹${Math.round(Number(value) / 100000)}L`}
            width={45}
          />
          <Tooltip
            formatter={(value: number | undefined) => formatINR(value ?? 0)}
            labelFormatter={(label) => `Month ${label}`}
            contentStyle={{
              border: "1px solid #E5E5E0",
              borderRadius: 5,
              background: "#FAFAF7",
            }}
          />
          <Line type="monotone" dataKey="balance" stroke="#0B6E4F" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
