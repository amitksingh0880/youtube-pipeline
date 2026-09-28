"use client";

import React from "react";
import { Flame } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { NICHES_CONFIG } from "@/config/studio-config";

interface NicheSelectorProps {
  selectedNiche: string;
  onSelectNiche: (nicheId: string) => void;
}

export function NicheSelector({ selectedNiche, onSelectNiche }: NicheSelectorProps) {
  return (
    <Card className="shadow-sm border-border/60">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Flame className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">Target Niche Profile</CardTitle>
          </div>
          <Badge variant="outline" className="text-[11px] font-medium">
            {NICHES_CONFIG.length} Presets Available
          </Badge>
        </div>
        <CardDescription className="text-xs">
          Select a high-performing content profile tuned for maximum retention & RPM.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {NICHES_CONFIG.map((niche) => {
            const isSelected = selectedNiche === niche.id;
            return (
              <Button
                key={niche.id}
                variant={isSelected ? "default" : "outline"}
                size="sm"
                onClick={() => onSelectNiche(niche.id)}
                className={`h-9 px-3 text-xs rounded-full transition-all ${
                  isSelected
                    ? "shadow-sm font-medium"
                    : "hover:bg-muted text-muted-foreground hover:text-foreground"
                }`}
              >
                <span className="mr-1.5">{niche.icon}</span>
                {niche.name}
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
