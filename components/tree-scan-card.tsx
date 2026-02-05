"use client";

import { Badge } from "@/components/ui/badge";
import { AlertCircle, Camera } from "lucide-react";
import { useState, useEffect } from "react";

export function TreeScanCard() {
  const [imageUrl, setImageUrl] = useState<string>("");

  useEffect(() => {
    // Generate a placeholder tree image
    setImageUrl("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Crect fill='%23e8f5e9' width='300' height='300'/%3E%3Ccircle cx='150' cy='100' r='60' fill='%23388e3c'/%3E%3Ccircle cx='120' cy='80' r='50' fill='%234caf50'/%3E%3Ccircle cx='180' cy='80' r='50' fill='%234caf50'/%3E%3Crect x='140' y='160' width='20' height='120' fill='%238d6e63'/%3E%3Ctext x='150' y='280' text-anchor='middle' font-size='12' fill='%23333'%3ENeem Tree - Healthy%3C/text%3E%3C/svg%3E");
  }, []);

  return (
    <div className="bg-card rounded-lg border border-border shadow-sm overflow-hidden">
      {/* Image Section */}
      <div className="relative bg-gradient-to-b from-primary-50 to-background w-full h-48 flex items-center justify-center">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Latest ESP32-CAM capture"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex flex-col items-center gap-2 text-muted-foreground">
            <Camera className="w-8 h-8" />
            <span className="text-sm">Loading...</span>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-6 space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-foreground mb-2">
            Latest Tree Scan
          </h3>
          <div className="flex items-center gap-2 mb-3">
            <Badge className="bg-accent text-accent-foreground">
              87% Confidence
            </Badge>
            <Badge variant="outline">ESP32-CAM Active</Badge>
          </div>
        </div>

        {/* Species Info */}
        <div className="bg-primary-50 rounded-lg p-3 space-y-1">
          <p className="text-xs text-muted-foreground">Species Identified</p>
          <p className="font-semibold text-primary-700">
            Neem (Azadirachta indica)
          </p>
          <p className="text-xs text-muted-foreground">
            Excellent carbon sequestration capacity
          </p>
        </div>

        {/* Health Status */}
        <div className="flex items-start gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
          <AlertCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-green-700">
            Tree health: <span className="font-semibold">Excellent</span>
          </div>
        </div>

        {/* Metadata */}
        <div className="text-xs text-muted-foreground space-y-1 border-t border-border pt-3">
          <p>Last updated: 2 minutes ago</p>
          <p>Location: Chennai, India</p>
        </div>
      </div>
    </div>
  );
}
