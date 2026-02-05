"use client"

import type { CarbonCreditScore } from "@/lib/types"
import { TrendingUp, TrendingDown, DollarSign, Award } from "lucide-react"

interface CarbonScoreDisplayProps {
  score: CarbonCreditScore
}

export function CarbonScoreDisplay({ score }: CarbonScoreDisplayProps) {
  const gradeColors: Record<string, string> = {
    "A+": "text-primary",
    A: "text-primary",
    "B+": "text-[hsl(180,60%,45%)]",
    B: "text-[hsl(180,60%,45%)]",
    C: "text-[hsl(45,93%,58%)]",
    D: "text-[hsl(30,80%,55%)]",
    F: "text-destructive",
  }

  const gradeBg: Record<string, string> = {
    "A+": "bg-primary/10 border-primary/30",
    A: "bg-primary/10 border-primary/30",
    "B+": "bg-[hsl(180,60%,45%)]/10 border-[hsl(180,60%,45%)]/30",
    B: "bg-[hsl(180,60%,45%)]/10 border-[hsl(180,60%,45%)]/30",
    C: "bg-[hsl(45,93%,58%)]/10 border-[hsl(45,93%,58%)]/30",
    D: "bg-[hsl(30,80%,55%)]/10 border-[hsl(30,80%,55%)]/30",
    F: "bg-destructive/10 border-destructive/30",
  }

  const breakdownItems = [
    {
      label: "Sequestration",
      value: score.breakdown.sequestrationScore,
      description: "Chave equation biomass carbon capture",
    },
    {
      label: "Emission Offset",
      value: score.breakdown.emissionOffset,
      description: "CO2 absorbed vs vehicle emissions",
    },
    {
      label: "Environmental Health",
      value: score.breakdown.environmentalHealth,
      description: "Sensor conditions quality",
    },
    {
      label: "O2 Production",
      value: score.breakdown.oxygenProduction,
      description: "Oxygen released by trees",
    },
  ]

  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Carbon Credit Score
        </h2>
        <Award className="h-4 w-4 text-muted-foreground" />
      </div>

      {/* Main Score */}
      <div className="flex items-center gap-6 mb-6">
        <div className="relative flex items-center justify-center">
          <svg className="h-28 w-28 -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="hsl(var(--muted))"
              strokeWidth="6"
            />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="hsl(var(--primary))"
              strokeWidth="6"
              strokeLinecap="round"
              strokeDasharray={`${(score.totalScore / 100) * 251.2} 251.2`}
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className="text-2xl font-bold font-mono text-foreground">
              {score.totalScore}
            </span>
            <span className="text-xs text-muted-foreground">/100</span>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <div
            className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 ${gradeBg[score.grade] || "bg-muted border-border"}`}
          >
            <span
              className={`text-lg font-bold ${gradeColors[score.grade] || "text-foreground"}`}
            >
              {score.grade}
            </span>
            <span className="text-xs text-muted-foreground">Grade</span>
          </div>
          <div className="flex items-center gap-1.5">
            {score.netCarbonBalance >= 0 ? (
              <TrendingUp className="h-3.5 w-3.5 text-primary" />
            ) : (
              <TrendingDown className="h-3.5 w-3.5 text-destructive" />
            )}
            <span
              className={`text-sm font-mono ${score.netCarbonBalance >= 0 ? "text-primary" : "text-destructive"}`}
            >
              {score.netCarbonBalance >= 0 ? "+" : ""}
              {score.netCarbonBalance.toFixed(1)} ppm
            </span>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="space-y-3">
        {breakdownItems.map((item) => (
          <div key={item.label}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-muted-foreground">
                {item.label}
              </span>
              <span className="text-xs font-mono text-foreground">
                {item.value}%
              </span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div
                className="h-full rounded-full bg-primary transition-all duration-700"
                style={{ width: `${item.value}%` }}
              />
            </div>
            <p className="mt-0.5 text-[10px] text-muted-foreground/70">
              {item.description}
            </p>
          </div>
        ))}
      </div>

      {/* Credits Earned */}
      <div className="mt-5 flex items-center justify-between rounded-md border border-primary/20 bg-primary/5 p-3">
        <div className="flex items-center gap-2">
          <DollarSign className="h-4 w-4 text-primary" />
          <div>
            <p className="text-xs text-muted-foreground">Credits Earned</p>
            <p className="text-sm font-semibold font-mono text-primary">
              {score.creditsEarned.toFixed(4)} tCO2e
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Value</p>
          <p className="text-sm font-semibold font-mono text-foreground">
            ${score.creditValueUSD.toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  )
}
