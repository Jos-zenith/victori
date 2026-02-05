"use client";

import { useEffect, useState } from "react";

interface GaugeProps {
  value: number;
  max: number;
}

function CarbonGauge({ value, max }: GaugeProps) {
  const percentage = (value / max) * 100;
  const angle = (percentage / 100) * 180 - 90;

  return (
    <div className="flex flex-col items-center justify-center py-8">
      {/* Gauge SVG */}
      <svg width="200" height="140" viewBox="0 0 200 140" className="mb-4">
        {/* Background arc */}
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(var(--primary-600))" />
            <stop offset="100%" stopColor="hsl(var(--accent))" />
          </linearGradient>
        </defs>

        {/* Gauge track */}
        <path
          d="M 20 120 A 80 80 0 0 1 180 120"
          stroke="hsl(var(--border))"
          strokeWidth="8"
          fill="none"
        />

        {/* Gauge fill */}
        <path
          d="M 20 120 A 80 80 0 0 1 180 120"
          stroke="url(#gaugeGradient)"
          strokeWidth="8"
          fill="none"
          strokeDasharray={`${(percentage / 100) * 251.33} 251.33`}
          strokeLinecap="round"
        />

        {/* Center circle */}
        <circle cx="100" cy="120" r="6" fill="hsl(var(--primary))" />

        {/* Needle */}
        <line
          x1="100"
          y1="120"
          x2={100 + 70 * Math.cos((angle * Math.PI) / 180)}
          y2={120 + 70 * Math.sin((angle * Math.PI) / 180)}
          stroke="hsl(var(--foreground))"
          strokeWidth="3"
          strokeLinecap="round"
        />

        {/* Labels */}
        <text x="30" y="135" fontSize="11" fill="hsl(var(--muted-foreground))">
          Low
        </text>
        <text x="160" y="135" fontSize="11" fill="hsl(var(--muted-foreground))">
          High
        </text>
      </svg>

      {/* Value display */}
      <div className="text-center">
        <div className="text-4xl font-bold text-primary mb-1">
          ${value.toFixed(2)}
        </div>
        <p className="text-sm text-muted-foreground">
          Carbon Credits | {percentage.toFixed(1)}% Capacity
        </p>
      </div>
    </div>
  );
}

export function HeroMetric() {
  const [credits, setCredits] = useState(2840.5);

  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setCredits((prev) => {
        const change = (Math.random() - 0.5) * 100;
        const newValue = Math.max(0, Math.min(5000, prev + change));
        return parseFloat(newValue.toFixed(2));
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-card rounded-lg border border-border shadow-sm p-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Carbon Credit Balance
        </h2>
        <p className="text-sm text-muted-foreground">
          Equation: $Credits = Tree Absorption - Vehicle Emission
        </p>
      </div>

      <CarbonGauge value={credits} max={5000} />

      {/* Breakdown */}
      <div className="flex gap-4 mt-8 pt-8 border-t border-border">
        <div className="flex-1 text-center">
          <p className="text-xs text-muted-foreground mb-1">Tree Absorption</p>
          <p className="text-xl font-semibold text-accent">+$3,240.50</p>
        </div>
        <div className="flex-1 text-center">
          <p className="text-xs text-muted-foreground mb-1">
            Vehicle Emission
          </p>
          <p className="text-xl font-semibold text-destructive">-$400.00</p>
        </div>
      </div>
    </div>
  );
}
