"use client";

import React, { useState } from "react";
import { Play, Globe, Search, Filter, Download, ExternalLink } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { HISTORY_ITEMS } from "@/config/studio-config";

export function ShortsLibraryGrid() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const filteredItems = HISTORY_ITEMS.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.niche.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || item.status.toLowerCase() === statusFilter.toLowerCase();
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-3">
      {/* SEARCH AND FILTER BAR */}
      <div className="flex flex-col sm:flex-row items-center gap-2">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            placeholder="Search shorts by title or niche..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8 h-8 text-xs"
          />
        </div>
        <Select value={statusFilter} onValueChange={(val) => setStatusFilter(val || "all")}>
          <SelectTrigger className="w-full sm:w-40 h-8 text-xs">
            <Filter className="mr-1 h-3 w-3 text-muted-foreground" />
            <SelectValue placeholder="Status Filter" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="published">Published</SelectItem>
            <SelectItem value="rendered">Rendered</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* VIDEO GRID */}
      <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
        {filteredItems.map((item) => (
          <Card
            key={item.id}
            className="shadow-xs border-border/60 overflow-hidden flex flex-col group hover:border-border transition-all"
          >
            {/* PORTRAIT VIDEO THUMBNAIL */}
            <div className="aspect-[9/16] bg-muted/40 border-b border-border/50 flex flex-col items-center justify-center relative p-3 group-hover:bg-muted/60 transition-colors">
              <div className="h-9 w-9 rounded-full bg-background/90 border border-border/60 flex items-center justify-center shadow-xs group-hover:scale-105 transition-transform">
                <Play className="h-3.5 w-3.5 text-foreground fill-foreground/20 ml-0.5" />
              </div>
              
              <div className="absolute top-2 left-2">
                <Badge variant="secondary" className="text-[9px] px-1 py-0 bg-background/80 backdrop-blur-xs font-mono">
                  {item.duration}
                </Badge>
              </div>

              <div className="absolute top-2 right-2">
                <Badge
                  variant="outline"
                  className={`text-[9px] py-0 px-1 font-medium ${
                    item.status === "Published"
                      ? "text-emerald-500 border-emerald-500/30 bg-emerald-500/10"
                      : item.status === "Failed"
                      ? "text-red-500 border-red-500/30 bg-red-500/10"
                      : "text-blue-500 border-blue-500/30 bg-blue-500/10"
                  }`}
                >
                  {item.status}
                </Badge>
              </div>

              <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between text-[9px] text-muted-foreground font-mono bg-background/70 backdrop-blur-xs px-1.5 py-0.5 rounded">
                <span>{item.renderTime}</span>
                <span>{item.date}</span>
              </div>
            </div>

            {/* CONTENT INFO */}
            <CardContent className="p-2.5 flex-1 flex flex-col justify-between space-y-2">
              <div className="space-y-0.5">
                <h3 className="text-xs font-semibold leading-tight line-clamp-2">{item.title}</h3>
                <p className="text-[10px] text-muted-foreground font-medium">{item.niche}</p>
              </div>

              <div className="flex items-center justify-between pt-1.5 border-t border-border/40 text-[10px]">
                <span className="flex items-center gap-1 text-muted-foreground">
                  <Globe className="h-3 w-3" /> {item.views}
                </span>
                <div className="flex items-center gap-0.5">
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <Download className="h-3 w-3 text-muted-foreground" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-6 w-6">
                    <ExternalLink className="h-3 w-3 text-muted-foreground" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
