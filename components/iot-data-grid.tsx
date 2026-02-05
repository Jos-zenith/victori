"use client";

import { useEffect, useState } from "react";
import { Droplets, Thermometer, AlertTriangle, Wind } from "lucide-react";

interface IoTData {
  soilMoisture: number;
  ambientTemp: number;
  dbh: number;
  airQuality: number;
}

const IoTCard = ({
  icon: Icon,
  label,
  value,
  unit,
  status,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: number;
  unit: string;
  status: "good" | "warning" | "critical";
}) => {
  const statusColors = {
    good: "bg-green-50 border-green-200 text-green-700",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-700",
    critical: "bg-red-50 border-red-200 text-red-700",
  };

  return (
    <div className={`rounded-lg border p-4 ${statusColors[status]}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium">{label}</span>
        <Icon className="w-4 h-4" />
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold">{value}</span>
        <span className="text-xs opacity-75">{unit}</span>
      </div>
    </div>
  );
};

export function IoTDataGrid() {
  const [data, setData] = useState<IoTData>({
    soilMoisture: 65,
    ambientTemp: 28,
    dbh: 45,
    airQuality: 62,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setData({
        soilMoisture: Math.max(30, Math.min(90, 65 + (Math.random() - 0.5) * 20)),
        ambientTemp: Math.max(20, Math.min(35, 28 + (Math.random() - 0.5) * 4)),
        dbh: 45 + (Math.random() - 0.5) * 2,
        airQuality: Math.max(30, Math.min(100, 62 + (Math.random() - 0.5) * 15)),
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getStatus = (
    label: string,
    value: number
  ): "good" | "warning" | "critical" => {
    if (label === "Soil Moisture") return value > 40 && value < 80 ? "good" : "warning";
    if (label === "Ambient Temp") return value > 15 && value < 32 ? "good" : "warning";
    if (label === "Air Quality") return value < 50 ? "good" : value < 75 ? "warning" : "critical";
    return "good";
  };

  return (
    <div className="bg-card rounded-lg border border-border shadow-sm p-6">
      <h3 className="text-lg font-semibold text-foreground mb-4">Live IoT Data</h3>
      <div className="grid grid-cols-2 gap-4">
        <IoTCard
          icon={Droplets}
          label="Soil Moisture"
          value={Math.round(data.soilMoisture)}
          unit="%"
          status={getStatus("Soil Moisture", data.soilMoisture)}
        />
        <IoTCard
          icon={Thermometer}
          label="Ambient Temp"
          value={Math.round(data.ambientTemp)}
          unit="°C"
          status={getStatus("Ambient Temp", data.ambientTemp)}
        />
        <IoTCard
          icon={AlertTriangle}
          label="DBH"
          value={Math.round(data.dbh * 10) / 10}
          unit="cm"
          status="good"
        />
        <IoTCard
          icon={Wind}
          label="Air Quality"
          value={Math.round(data.airQuality)}
          unit="AQI"
          status={getStatus("Air Quality", data.airQuality)}
        />
      </div>
    </div>
  );
}
