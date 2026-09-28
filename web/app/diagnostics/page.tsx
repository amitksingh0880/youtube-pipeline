"use client";

import React from "react";
import { RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DiagnosticsTerminal } from "@/components/studio/DiagnosticsTerminal";

export default function DiagnosticsPage() {
  return (
    <div className="h-full flex flex-col justify-between gap-3 overflow-hidden">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-[10px] px-1.5 py-0">
              System Health
            </Badge>
            <Badge variant="secondary" className="text-[10px] px-1.5 py-0 text-emerald-500 border-emerald-500/20 bg-emerald-500/10">
              All Systems Operational
            </Badge>
          </div>
          <h2 className="text-xl font-bold tracking-tight">Engine Diagnostics & Live Logs</h2>
          <p className="text-xs text-muted-foreground">
            Real-time component health telemetry and rendering execution logs.
          </p>
        </div>
        <Button variant="outline" size="sm" className="h-8 text-xs">
          <RefreshCw className="mr-1 h-3.5 w-3.5" /> Re-check Components
        </Button>
      </div>

      {/* DIAGNOSTICS COMPONENT */}
      <div className="flex-1 overflow-hidden">
        <DiagnosticsTerminal />
      </div>
    </div>
  );
}
