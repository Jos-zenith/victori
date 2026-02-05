"use client"

import type { SensorHistoryPoint } from "@/lib/types"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts"

interface SensorChartsProps {
  history: SensorHistoryPoint[]
}

const chartGreen = "#22c55e"
const chartCyan = "#06b6d4"
const chartAmber = "#eab308"
const chartRed = "#ef4444"

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: Array<{ name: string; value: number; color: string }>
  label?: string
}) {
  if (!active || !payload || !payload.length) return null
  return (
    <div className="rounded-md border border-border bg-card px-3 py-2 shadow-lg">
      <p className="text-xs font-mono text-muted-foreground mb-1">{label}</p>
      {payload.map((entry, idx) => (
        <p key={idx} className="text-xs font-mono" style={{ color: entry.color }}>
          {entry.name}: {typeof entry.value === "number" ? entry.value.toFixed(1) : entry.value}
        </p>
      ))}
    </div>
  )
}

export function TemperatureHumidityChart({ history }: SensorChartsProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Temperature & Humidity
        </h3>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: chartGreen }} />
            <span className="text-[10px] text-muted-foreground">Temp</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: chartCyan }} />
            <span className="text-[10px] text-muted-foreground">Humidity</span>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(150,10%,16%)" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10, fill: "hsl(150,8%,55%)" }}
            axisLine={{ stroke: "hsl(150,10%,16%)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "hsl(150,8%,55%)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="temperature"
            stroke={chartGreen}
            strokeWidth={2}
            dot={false}
            name="Temp (C)"
          />
          <Line
            type="monotone"
            dataKey="humidity"
            stroke={chartCyan}
            strokeWidth={2}
            dot={false}
            name="Humidity (%)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export function CO2BalanceChart({ history }: SensorChartsProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          CO2 Balance
        </h3>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: chartRed }} />
            <span className="text-[10px] text-muted-foreground">Emitted</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: chartGreen }} />
            <span className="text-[10px] text-muted-foreground">Absorbed</span>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={history}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(150,10%,16%)" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10, fill: "hsl(150,8%,55%)" }}
            axisLine={{ stroke: "hsl(150,10%,16%)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "hsl(150,8%,55%)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="co2Emitted"
            stroke={chartRed}
            fill={chartRed}
            fillOpacity={0.1}
            strokeWidth={2}
            name="CO2 Emitted (ppm)"
          />
          <Area
            type="monotone"
            dataKey="co2Absorbed"
            stroke={chartGreen}
            fill={chartGreen}
            fillOpacity={0.15}
            strokeWidth={2}
            name="CO2 Absorbed (ppm)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function OxygenSunlightChart({ history }: SensorChartsProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          O2 & Sunlight
        </h3>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: chartCyan }} />
            <span className="text-[10px] text-muted-foreground">O2</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: chartAmber }} />
            <span className="text-[10px] text-muted-foreground">Light</span>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(150,10%,16%)" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10, fill: "hsl(150,8%,55%)" }}
            axisLine={{ stroke: "hsl(150,10%,16%)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: "hsl(150,8%,55%)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="o2Released"
            stroke={chartCyan}
            strokeWidth={2}
            dot={false}
            name="O2 (ppm)"
          />
          <Line
            type="monotone"
            dataKey="lightIntensity"
            stroke={chartAmber}
            strokeWidth={2}
            dot={false}
            name="Light (umol)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
