"use client";

import React from "react";
import { Layers } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PIPELINE_MODES_CONFIG } from "@/config/studio-config";

interface PipelineModeCardsProps {
  selectedMode: string;
  onSelectMode: (modeId: string) => void;
}

export function PipelineModeCards({ selectedMode, onSelectMode }: PipelineModeCardsProps) {
  return (
    <Card className="shadow-sm border-border/60">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-emerald-500" />
            <CardTitle className="text-lg">Assembly Pipeline Mode</CardTitle>
          </div>
          <Badge variant="secondary" className="text-[11px]">
            NVENC Active
          </Badge>
        </div>
        <CardDescription className="text-xs">
          Choose local hardware rendering or cloud API synthesis.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3 sm:grid-cols-3">
        {PIPELINE_MODES_CONFIG.map((mode) => {
          const isSelected = selectedMode === mode.id;
          return (
            <div
              key={mode.id}
              onClick={() => onSelectMode(mode.id)}
              className={`cursor-pointer rounded-lg p-3.5 border transition-all flex flex-col justify-between space-y-3 ${
                isSelected
                  ? "border-primary bg-primary/5 ring-1 ring-primary/20"
                  : "border-border/60 bg-card hover:border-border hover:bg-muted/40"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className={`p-1.5 rounded-md ${isSelected ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                  <mode.icon className="h-4 w-4" />
                </div>
                <Badge variant={mode.badgeVariant} className="text-[10px] px-1.5 py-0">
                  {mode.badge}
                </Badge>
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-semibold">{mode.title}</h4>
                <p className="text-[11px] text-muted-foreground leading-relaxed line-clamp-3">
                  {mode.desc}
                </p>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
