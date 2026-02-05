import { Leaf, Wifi, User } from "lucide-react";
import { Button } from "@/components/ui/button";

export function DashboardHeader() {
  return (
    <header className="border-b border-border bg-card shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <Leaf className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">HCCMS</h1>
              <p className="text-xs text-muted-foreground">Green Wallet</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="h-3 w-3 animate-pulse rounded-full bg-accent"></div>
            <span className="text-sm font-medium text-foreground">Live Sync</span>
            <Wifi className="h-4 w-4 text-accent" />
          </div>

          <Button
            variant="outline"
            size="icon"
            className="h-10 w-10 rounded-full"
          >
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
