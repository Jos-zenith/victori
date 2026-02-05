"use client"

import type { ReactNode } from "react"

interface SensorCardProps {
  icon: ReactNode
  label: string
  value: string
  unit: string
  status: "optimal" | "warning" | "critical"
  subtext?: string
}

export function SensorCard({
  icon,
  label,
  value,
  unit,
  status,
  subtext,
}: SensorCardProps) {
  const statusColors = {
    optimal: "text-primary",
    warning: "text-[hsl(45,93%,58%)]",
    critical: "text-destructive",
  }

  const statusBg = {
    optimal: "bg-primary/5 border-primary/20",
    warning: "bg-[hsl(45,93%,58%)]/5 border-[hsl(45,93%,58%)]/20",
    critical: "bg-destructive/5 border-destructive/20",
  }

  return (
    <div
      className={`rounded-lg border p-4 transition-all hover:shadow-md ${statusBg[status]}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className={`${statusColors[status]}`}>{icon}</span>
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {label}
          </span>
        </div>
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            status === "optimal"
              ? "bg-primary"
              : status === "warning"
                ? "bg-[hsl(45,93%,58%)]"
                : "bg-destructive"
          }`}
        />
      </div>
      <div className="mt-3">
        <div className="flex items-baseline gap-1">
          <span className={`text-2xl font-semibold font-mono ${statusColors[status]}`}>
            {value}
          </span>
          <span className="text-xs text-muted-foreground">{unit}</span>
        </div>
        {subtext && (
          <p className="mt-1 text-xs text-muted-foreground">{subtext}</p>
        )}
      </div>
    </div>
  )
}
