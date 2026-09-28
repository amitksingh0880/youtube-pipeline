"use client";

import React, { useState } from "react";
import { Search, Volume2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { NICHES_CONFIG } from "@/config/studio-config";

export function NicheTable() {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredNiches = NICHES_CONFIG.filter((n) =>
    n.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Card className="shadow-sm border-border/60 overflow-hidden flex flex-col h-full">
      <CardHeader className="py-2.5 px-4 border-b border-border/50">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <CardTitle className="text-sm font-semibold">Verified Niche Profiles</CardTitle>
          <div className="relative w-full sm:w-56">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Search niches..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 h-8 text-xs"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0 overflow-auto flex-1">
        <Table>
          <TableHeader className="bg-muted/50 sticky top-0 z-10">
            <TableRow>
              <TableHead className="text-xs font-semibold py-2">Niche Profile</TableHead>
              <TableHead className="text-xs font-semibold py-2">Est. RPM</TableHead>
              <TableHead className="text-xs font-semibold py-2">Volume</TableHead>
              <TableHead className="text-xs font-semibold py-2">Retention</TableHead>
              <TableHead className="text-xs font-semibold py-2">TTS Engine</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredNiches.map((niche) => (
              <TableRow key={niche.id} className="hover:bg-muted/30">
                <TableCell className="font-medium text-xs py-2 flex items-center gap-1.5">
                  <span>{niche.icon}</span>
                  {niche.name}
                </TableCell>
                <TableCell className="py-2">
                  <Badge variant="outline" className="text-[10px] py-0 font-medium text-emerald-500 border-emerald-500/30 bg-emerald-500/10">
                    {niche.rpm}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs py-2">{niche.volume}</TableCell>
                <TableCell className="text-xs font-mono font-medium text-primary py-2">{niche.retention}</TableCell>
                <TableCell className="text-xs text-muted-foreground py-2">
                  <div className="flex items-center gap-1">
                    <Volume2 className="h-3 w-3" />
                    {niche.voice}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
