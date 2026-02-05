import { Leaf, Wifi, User } from "lucide-react";
import { Button } from "@/components/ui/button";

export function DashboardHeader() {
  return (
    <header className="border-b border-border bg-card shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
              <Leaf className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">HCCMS</h1>
              <p className="text-xs text-muted-foreground">Green Wallet</p>
            </div>
          </div>

          {/* Live Sync Status */}
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-accent animate-pulse"></div>
            <span className="text-sm font-medium text-foreground">Live Sync</span>
            <Wifi className="w-4 h-4 text-accent" />
          </div>

          {/* Profile */}
          <Button
            variant="outline"
            size="icon"
            className="rounded-full w-10 h-10"
          >
            <User className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
