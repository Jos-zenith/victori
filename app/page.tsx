import { DashboardHeader } from "@/components/dashboard-header";
import { HeroMetric } from "@/components/hero-metric";
import { TreeScanCard } from "@/components/tree-scan-card";
import { IoTDataGrid } from "@/components/iot-data-grid";
import { AnalyticsChart } from "@/components/analytics-chart";
import { ActionCenter } from "@/components/action-center";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-primary-50">
      <DashboardHeader />

      <main className="px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Hero Metric */}
          <HeroMetric />

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Tree Scan Card */}
            <div className="lg:col-span-1">
              <TreeScanCard />
            </div>

            {/* IoT Data Grid */}
            <div className="lg:col-span-2">
              <IoTDataGrid />
            </div>
          </div>

          {/* Analytics Section */}
          <AnalyticsChart />

          {/* Action Center */}
          <ActionCenter />
        </div>
      </main>
    </div>
  );
}
