"use client";

import React from "react";
import { Activity, CheckCircle2, Terminal } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DIAGNOSTICS_SERVICES, DIAGNOSTICS_LOGS } from "@/config/studio-config";

export function DiagnosticsTerminal() {
  return (
    <div className="grid gap-4 md:grid-cols-12 items-start h-full">
      {/* SYSTEM STATUS CARDS (5 COLS) */}
      <Card className="md:col-span-5 shadow-sm border-border/60">
        <CardHeader className="py-2.5 px-3.5 border-b border-border/50">
          <CardTitle className="text-xs font-semibold flex items-center gap-2">
            <Activity className="h-3.5 w-3.5 text-emerald-500" />
            Component Health Status
          </CardTitle>
          <CardDescription className="text-[11px]">
            Engine background services & RPC response latencies.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-3 space-y-2.5">
          {DIAGNOSTICS_SERVICES.map((service, i) => (
            <div key={i} className="flex items-center justify-between p-2 rounded-md bg-muted/20 border border-border/40">
              <div className="flex items-center gap-2.5">
                <div className="p-1 rounded bg-emerald-500/10 text-emerald-500">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                </div>
                <span className="text-xs font-semibold">{service.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-muted-foreground">{service.ping}</span>
                <Badge variant="outline" className="text-[9px] px-1 py-0 text-emerald-500 border-emerald-500/30 bg-emerald-500/10">
                  {service.status}
                </Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* LIVE TERMINAL LOGS (7 COLS) */}
      <Card className="md:col-span-7 bg-[#0d0d0d] border-zinc-800 shadow-sm flex flex-col overflow-hidden h-full">
        <CardHeader className="py-2.5 px-3.5 border-b border-zinc-800 bg-zinc-950/60">
          <div className="flex items-center justify-between">
            <CardTitle className="text-xs font-mono text-zinc-200 flex items-center gap-2">
              <Terminal className="h-3.5 w-3.5 text-emerald-400" /> Pipeline Execution Logs
            </CardTitle>
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping" />
              <Badge variant="outline" className="text-[9px] px-1.5 py-0 text-zinc-400 border-zinc-700">
                Live Feed
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0 flex-1">
          <ScrollArea className="h-[280px] w-full p-3 font-mono text-[10px] leading-relaxed">
            <div className="space-y-1.5">
              {DIAGNOSTICS_LOGS.map((log, index) => (
                <div
                  key={index}
                  className={
                    log.includes("completed") || log.includes("successfully") || log.includes("located")
                      ? "text-emerald-400"
                      : log.includes("Notice:")
                      ? "text-amber-400"
                      : "text-zinc-400"
                  }
                >
                  {log}
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
