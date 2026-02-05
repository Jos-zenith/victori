import { DashboardHeader } from "@/components/dashboard-header";
import { HeroMetric } from "@/components/hero-metric";
import { TreeScanCard } from "@/components/tree-scan-card";
import { IoTDataGrid } from "@/components/iot-data-grid";
import { AnalyticsChart } from "@/components/analytics-chart";
import { ActionCenter } from "@/components/action-center";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-background to-primary-50">
      <DashboardHeader />

      <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="mx-auto max-w-7xl flex flex-col gap-8">
          <HeroMetric />

          <div className="flex flex-col gap-6 lg:flex-row lg:gap-6">
            <div className="w-full lg:w-1/3">
              <TreeScanCard />
            </div>
            <div className="w-full lg:w-2/3">
              <IoTDataGrid />
            </div>
          </div>

          <AnalyticsChart />

          <ActionCenter />
        </div>
      </main>
    </div>
  );
}
