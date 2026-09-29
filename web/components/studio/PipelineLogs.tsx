"use client";

import React, { useEffect, useState, useRef } from "react";
import { Terminal } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function PipelineLogs({ isGenerating }: { isGenerating: boolean }) {
  const [logs, setLogs] = useState<{ timestamp: string; level: string; message: string }[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchLogs = async () => {
      try {
        const res = await fetch("/api/logs");
        if (res.ok) {
          const data = await res.json();
          if (data.logs) {
            setLogs(data.logs);
          }
        }
      } catch (err) {
        console.error("Failed to fetch logs", err);
      }
    };

    if (isGenerating) {
      fetchLogs();
      interval = setInterval(fetchLogs, 2000);
    } else {
      // Fetch one last time when generation stops
      fetchLogs();
    }

    return () => clearInterval(interval);
  }, [isGenerating]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <Card className="shadow-sm border-border/60 bg-slate-950 text-slate-300">
      <CardHeader className="py-2.5 px-3.5 border-b border-slate-800 bg-slate-900/50">
        <CardTitle className="text-xs font-mono flex items-center gap-2 text-slate-200">
          <Terminal className="h-3.5 w-3.5 text-emerald-400" />
          Pipeline Execution Logs
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div 
          ref={scrollRef}
          className="h-64 overflow-y-auto p-3 text-[10px] font-mono leading-relaxed space-y-1"
        >
          {logs.length === 0 ? (
            <div className="text-slate-600 italic">No logs generated yet...</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="flex gap-2 break-all">
                <span className="text-slate-500 shrink-0">[{log.timestamp}]</span>
                <span className={
                  log.level === 'ERROR' || log.level === 'CRITICAL' ? 'text-red-400 font-bold' : 
                  log.level === 'WARNING' ? 'text-yellow-400' : 'text-slate-300'
                }>
                  {log.message}
                </span>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
