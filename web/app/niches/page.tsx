"use client";

import React from "react";
import { Flame, TrendingUp, DollarSign, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { NicheTable } from "@/components/studio/NicheTable";

export default function NichesPage() {
  return (
    <div className="h-full flex flex-col justify-between gap-3 overflow-hidden">
      {/* PAGE HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-[10px] px-1.5 py-0">
              Intelligence Presets
            </Badge>
            <Badge variant="secondary" className="text-[10px] px-1.5 py-0 text-amber-500 border-amber-500/20 bg-amber-500/10">
              High RPM Verified
            </Badge>
          </div>
          <h2 className="text-xl font-bold tracking-tight">Niche Intelligence & Presets</h2>
          <p className="text-xs text-muted-foreground">
            Explore verified high-retention content niches optimized for monetization.
          </p>
        </div>
        <Button size="sm" className="h-8 text-xs">
          <Plus className="mr-1 h-3.5 w-3.5" /> Add Custom Niche
        </Button>
      </div>

      {/* METRICS ROW */}
      <div className="grid gap-3 sm:grid-cols-3">
        <Card className="shadow-xs border-border/60">
          <CardContent className="p-3 flex items-center gap-3">
            <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-500">
              <DollarSign className="h-4 w-4" />
            </div>
            <div>
              <p className="text-[10px] text-muted-foreground">Top RPM Niche</p>
              <h4 className="text-xs font-semibold">Wealth & Finance ($12 RPM)</h4>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-xs border-border/60">
          <CardContent className="p-3 flex items-center gap-3">
            <div className="p-2 rounded bg-blue-500/10 border border-blue-500/20 text-blue-500">
              <TrendingUp className="h-4 w-4" />
            </div>
            <div>
              <p className="text-[10px] text-muted-foreground">Highest Search Volume</p>
              <h4 className="text-xs font-semibold">Psychology & Mind Games</h4>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-xs border-border/60">
          <CardContent className="p-3 flex items-center gap-3">
            <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-500">
              <Flame className="h-4 w-4" />
            </div>
            <div>
              <p className="text-[10px] text-muted-foreground">Avg. Retention Rate</p>
              <h4 className="text-xs font-semibold">81% Completion</h4>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* SEARCH AND TABLE COMPONENT */}
      <div className="flex-1 overflow-hidden">
        <NicheTable />
      </div>
    </div>
  );
}
