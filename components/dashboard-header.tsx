"use client"

import { Leaf, Wifi, WifiOff, Activity } from "lucide-react"

interface DashboardHeaderProps {
  isConnected: boolean
  lastUpdate: string
}

export function DashboardHeader({
  isConnected,
  lastUpdate,
}: DashboardHeaderProps) {
  return (
    <header className="flex flex-col gap-4 border-b border-border px-6 py-4 md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
          <Leaf className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-foreground tracking-tight">
            Victori Carbon Credits
          </h1>
          <p className="text-sm text-muted-foreground">
            Real-time IoT Carbon Credit Score Calculator
          </p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-md border border-border bg-card px-3 py-1.5">
          <Activity className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-xs text-muted-foreground font-mono">
            {lastUpdate
              ? `Last: ${new Date(lastUpdate).toLocaleTimeString()}`
              : "Awaiting data..."}
          </span>
        </div>
        <div
          className={`flex items-center gap-2 rounded-md border px-3 py-1.5 ${
            isConnected
              ? "border-primary/30 bg-primary/5"
              : "border-destructive/30 bg-destructive/5"
          }`}
        >
          {isConnected ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
              </span>
              <Wifi className="h-3.5 w-3.5 text-primary" />
              <span className="text-xs text-primary font-medium">
                ESP32 Live
              </span>
            </>
          ) : (
            <>
              <span className="h-2 w-2 rounded-full bg-destructive" />
              <WifiOff className="h-3.5 w-3.5 text-destructive" />
              <span className="text-xs text-destructive font-medium">
                Simulated
              </span>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
