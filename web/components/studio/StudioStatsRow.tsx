"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { STUDIO_STATS } from "@/config/studio-config";

export function StudioStatsRow() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {STUDIO_STATS.map((stat, i) => (
        <Card key={i} className="shadow-sm border-border/60 hover:border-border transition-all">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-2.5 rounded-lg bg-muted border border-border/50">
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </div>
            <div className="space-y-0.5">
              <p className="text-xs font-medium text-muted-foreground">{stat.label}</p>
              <h3 className="text-base font-semibold tracking-tight">{stat.value}</h3>
              <p className="text-[11px] text-muted-foreground/80">{stat.sub}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
