import { Button } from "@/components/ui/button";
import { Download, RefreshCw, ExternalLink } from "lucide-react";

export function ActionCenter() {
  return (
    <div className="bg-gradient-to-r from-primary-50 to-accent/10 rounded-lg border border-primary-200 shadow-sm p-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Action Center
          </h3>
          <p className="text-sm text-muted-foreground">
            Manage your carbon credits, sync data, and access green bonds
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <Button
            variant="outline"
            className="flex items-center gap-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Manual Sync</span>
          </Button>

          <Button
            className="flex items-center gap-2 bg-primary hover:bg-primary-700"
          >
            <Download className="w-4 h-4" />
            <span>Download Certificate</span>
          </Button>

          <Button
            variant="outline"
            className="flex items-center gap-2"
          >
            <ExternalLink className="w-4 h-4" />
            <span>Green Bond (GCC)</span>
          </Button>
        </div>
      </div>

      {/* Info Cards */}
      <div className="flex flex-col gap-4 mt-6 pt-6 border-t border-primary-200 sm:flex-row">
        <div className="flex-1 bg-white rounded-lg p-4">
          <p className="text-xs font-semibold text-primary-700 mb-2">
            SYNC STATUS
          </p>
          <p className="text-2xl font-bold text-foreground">Connected</p>
          <p className="text-xs text-muted-foreground">Updated 2 min ago</p>
        </div>

        <div className="flex-1 bg-white rounded-lg p-4">
          <p className="text-xs font-semibold text-accent mb-2">
            CREDITS EARNED
          </p>
          <p className="text-2xl font-bold text-accent">+324.50</p>
          <p className="text-xs text-muted-foreground">This month</p>
        </div>

        <div className="flex-1 bg-white rounded-lg p-4">
          <p className="text-xs font-semibold text-primary-700 mb-2">
            CERTIFICATES
          </p>
          <p className="text-2xl font-bold text-foreground">5</p>
          <p className="text-xs text-muted-foreground">Ready to download</p>
        </div>
      </div>
    </div>
  );
}
