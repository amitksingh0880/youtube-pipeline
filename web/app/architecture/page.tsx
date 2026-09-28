"use client";

import React from "react";
import { Server } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ArchitectureFAQ } from "@/components/studio/ArchitectureFAQ";
import { ARCHITECTURE_STEPS } from "@/config/studio-config";

export default function ArchitecturePage() {
  return (
    <div className="h-full flex flex-col justify-between gap-3 overflow-hidden">
      {/* PAGE HEADER */}
      <div className="space-y-0.5">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-[10px] px-1.5 py-0">
            Architecture Documentation
          </Badge>
          <Badge variant="secondary" className="text-[10px] px-1.5 py-0 text-emerald-500 border-emerald-500/20 bg-emerald-500/10">
            FFmpeg 9.0 Verified
          </Badge>
        </div>
        <h2 className="text-xl font-bold tracking-tight">Ssemble Architecture & Local Pipeline</h2>
        <p className="text-xs text-muted-foreground">
          Detailed technical guide on local FFmpeg video synthesis, kinetic subtitle parsing, and cloud failovers.
        </p>
      </div>

      {/* SYSTEM STATUS ALERT */}
      <Alert className="py-2 px-3 border-emerald-500/30 bg-emerald-500/5 text-foreground">
        <Server className="h-4 w-4 text-emerald-500" />
        <AlertTitle className="text-xs font-semibold text-emerald-500">100% Local Hardware Processing Active</AlertTitle>
        <AlertDescription className="text-xs text-muted-foreground mt-0.5">
          Your pipeline is currently utilizing native local FFmpeg 9.0 binaries and Edge TTS. Video rendering requires 0 cloud API credits.
        </AlertDescription>
      </Alert>

      {/* PIPELINE FLOW CARDS */}
      <div className="grid gap-3 sm:grid-cols-3">
        {ARCHITECTURE_STEPS.map((item, i) => (
          <Card key={i} className="shadow-xs border-border/60">
            <CardHeader className="py-2.5 px-3">
              <span className="text-[10px] font-mono font-semibold text-primary">{item.step}</span>
              <CardTitle className="text-xs font-semibold">{item.title}</CardTitle>
            </CardHeader>
            <CardContent className="px-3 pb-3">
              <p className="text-[11px] text-muted-foreground leading-relaxed">{item.desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Separator />

      {/* FAQ ACCORDION SECTION */}
      <div className="flex-1 overflow-y-auto">
        <ArchitectureFAQ />
      </div>
    </div>
  );
}
