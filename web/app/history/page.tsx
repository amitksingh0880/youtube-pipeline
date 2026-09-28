"use client";

import React from "react";
import { RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ShortsLibraryGrid } from "@/components/studio/ShortsLibraryGrid";

export default function HistoryPage() {
  return (
    <div className="h-full flex flex-col justify-between gap-3 overflow-hidden">
      {/* PAGE HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-[10px] px-1.5 py-0">
              Library Archive
            </Badge>
            <Badge variant="secondary" className="text-[10px] px-1.5 py-0 text-blue-500 border-blue-500/20 bg-blue-500/10">
              12 Total Rendered
            </Badge>
          </div>
          <h2 className="text-xl font-bold tracking-tight">Shorts Library & Archive</h2>
          <p className="text-xs text-muted-foreground">
            Review, download, and track stats for your synthesized short videos.
          </p>
        </div>
        <Button variant="outline" size="sm" className="h-8 text-xs">
          <RefreshCw className="mr-1 h-3.5 w-3.5" /> Sync Library
        </Button>
      </div>

      {/* SHORTS LIBRARY GRID */}
      <div className="flex-1 overflow-y-auto">
        <ShortsLibraryGrid />
      </div>
    </div>
  );
}
