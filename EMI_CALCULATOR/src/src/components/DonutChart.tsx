import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { formatINR } from "../lib/emi";

interface Props {
  principal: number;
  interest: number;
}

export function DonutChart({ principal, interest }: Props) {
  const data = [
    { name: "Principal", value: principal },
    { name: "Interest", value: interest },
  ];

  return (
    <div className="h-56 w-full" aria-label="Principal versus interest chart">
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={58}
            outerRadius={82}
            paddingAngle={1}
            stroke="#FAFAF7"
            strokeWidth={2}
          >
            <Cell fill="#0B6E4F" />
            <Cell fill="#A9A79F" />
          </Pie>
          <Tooltip
            formatter={(value: number | undefined) => formatINR(value ?? 0)}
            contentStyle={{
              border: "1px solid #E5E5E0",
              borderRadius: 5,
              background: "#FAFAF7",
              fontFamily: "IBM Plex Sans, sans-serif",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
