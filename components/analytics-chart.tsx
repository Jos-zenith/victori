"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

const monthlyData = [
  { month: "Jan", absorption: 2800, footprint: 1200, net: 1600 },
  { month: "Feb", absorption: 3200, footprint: 1100, net: 2100 },
  { month: "Mar", absorption: 2290, footprint: 1300, net: 990 },
  { month: "Apr", absorption: 2000, footprint: 980, net: 1020 },
  { month: "May", absorption: 2181, footprint: 1200, net: 981 },
  { month: "Jun", absorption: 2500, footprint: 1100, net: 1400 },
  { month: "Jul", absorption: 2100, footprint: 1500, net: 600 },
  { month: "Aug", absorption: 2200, footprint: 1200, net: 1000 },
  { month: "Sep", absorption: 2290, footprint: 1300, net: 990 },
  { month: "Oct", absorption: 3400, footprint: 1100, net: 2300 },
  { month: "Nov", absorption: 3490, footprint: 1300, net: 2190 },
  { month: "Dec", absorption: 3200, footprint: 900, net: 2300 },
];

export function AnalyticsChart() {
  return (
    <div className="bg-card rounded-lg border border-border shadow-sm p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-2">
          Monthly Carbon Analysis
        </h2>
        <p className="text-sm text-muted-foreground">
          Comparing tree absorption vs household footprint
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Bar Chart */}
        <div className="flex-1 rounded-lg bg-background p-4">
          <h3 className="text-sm font-medium text-foreground mb-4">
            Absorption vs Footprint
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                }}
                labelStyle={{ color: "hsl(var(--foreground))" }}
              />
              <Legend />
              <Bar dataKey="absorption" fill="hsl(var(--chart-1))" name="Absorption" />
              <Bar dataKey="footprint" fill="hsl(var(--chart-3))" name="Footprint" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Line Chart - Net Credits */}
        <div className="flex-1 rounded-lg bg-background p-4">
          <h3 className="text-sm font-medium text-foreground mb-4">
            Net Credit Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                }}
                labelStyle={{ color: "hsl(var(--foreground))" }}
              />
              <Line
                type="monotone"
                dataKey="net"
                stroke="hsl(var(--chart-1))"
                strokeWidth={2}
                dot={{ fill: "hsl(var(--primary))", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stats */}
      <div className="flex flex-col gap-4 mt-6 pt-6 border-t border-border sm:flex-row sm:gap-4">
        <div className="flex-1 text-center">
          <p className="text-xs text-muted-foreground mb-1">Avg Monthly Absorption</p>
          <p className="text-xl font-bold text-accent">2,768 kg CO₂</p>
        </div>
        <div className="flex-1 text-center">
          <p className="text-xs text-muted-foreground mb-1">Avg Monthly Footprint</p>
          <p className="text-xl font-bold text-destructive">1,192 kg CO₂</p>
        </div>
        <div className="flex-1 text-center">
          <p className="text-xs text-muted-foreground mb-1">Annual Net Credit</p>
          <p className="text-xl font-bold text-primary">18,912 kg CO₂</p>
        </div>
      </div>
    </div>
  );
}
