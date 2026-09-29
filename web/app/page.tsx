"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Search, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { StudioStatsRow } from "@/components/studio/StudioStatsRow";
import { NicheSelector } from "@/components/studio/NicheSelector";
import { PipelineModeCards } from "@/components/studio/PipelineModeCards";
import { StudioPreviewPlayer } from "@/components/studio/StudioPreviewPlayer";
import { IntegrationsPanel } from "@/components/studio/IntegrationsPanel";
import { PipelineLogs } from "@/components/studio/PipelineLogs";

export default function StudioGeneratorPage() {
  const [selectedNiche, setSelectedNiche] = useState("dark_history");
  const [pipelineMode, setPipelineMode] = useState("local");
  const [topicHint, setTopicHint] = useState("");
  const [isDryRun, setIsDryRun] = useState(true);
  const [autoUpload, setAutoUpload] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stageText, setStageText] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [videoFilename, setVideoFilename] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isGenerating && jobId) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`/api/progress/${jobId}`);
          if (!res.ok) return;
          const data = await res.json();
          
          setProgress(data.percent || 0);
          setStageText(data.message || "");

          if (data.status === "completed") {
            setIsGenerating(false);
            clearInterval(interval);
            
            if (data.result) {
              if (data.result.session_id) {
                setSessionId(data.result.session_id);
              }
              if (data.result.video_path) {
                const fullPath = data.result.video_path;
                const filename = fullPath.split(/[/\\]/).pop();
                setVideoFilename(filename);
              }
            }
          } else if (data.status === "failed") {
            setIsGenerating(false);
            clearInterval(interval);
            setStageText(`Failed: ${data.error || data.message}`);
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isGenerating, jobId]);

  const handleSynthesize = async () => {
    setIsGenerating(true);
    setProgress(5);
    setStageText("Initializing pipeline...");
    setVideoFilename(null);
    setSessionId(null);
    setJobId(null);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          niche_id: selectedNiche,
          mode: pipelineMode === "local" ? "local-studio" : "ssemble-ai",
          topic_hint: topicHint || undefined,
          dry_run: isDryRun,
          privacy_status: "unlisted",
        }),
      });
      
      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      
      const data = await res.json();
      if (data.job_id) {
        setJobId(data.job_id);
      } else {
        throw new Error("No job_id returned");
      }
    } catch (err: any) {
      setIsGenerating(false);
      setStageText(`Error starting job: ${err.message}`);
    }
  };

  const handleUpload = async () => {
    if (!sessionId) return;
    setIsUploading(true);
    try {
      const res = await fetch(`/api/upload/${sessionId}`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      
      alert(`Successfully uploaded to YouTube!\nVideo ID: ${data.video_id}`);
    } catch (err: any) {
      alert(`Error uploading: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setProgress(0);
    setIsGenerating(false);
    setStageText("");
    setJobId(null);
    setVideoFilename(null);
    setSessionId(null);
  };

  return (
    <div className="flex flex-col gap-4">
      {/* STATS OVERVIEW */}
      <StudioStatsRow />

      {/* WORKSPACE GRID */}
      <div className="grid gap-4 lg:grid-cols-12 items-start">
        {/* CONFIG FORM (7 COLS) */}
        <div className="lg:col-span-7 space-y-4">
          <NicheSelector selectedNiche={selectedNiche} onSelectNiche={setSelectedNiche} />
          <PipelineModeCards selectedMode={pipelineMode} onSelectMode={setPipelineMode} />

          {/* TOPIC & ADVANCED SETTINGS */}
          <Card className="shadow-sm border-border/60">
            <CardHeader className="py-2.5 px-3.5">
              <CardTitle className="text-sm font-semibold">Hook & Topic Angle</CardTitle>
              <CardDescription className="text-xs">
                Provide a prompt hint or let the AI scout trending viral topics automatically.
              </CardDescription>
            </CardHeader>
            <CardContent className="px-3.5 pb-3 space-y-3">
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <Label className="text-xs font-medium">Topic or Headline Angle</Label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setTopicHint("Project Acoustic Kitty: $20M CIA Secret Spy Cat")}
                    className="h-5 text-[10px] px-1.5 text-muted-foreground hover:text-foreground"
                  >
                    <Search className="h-3 w-3 mr-1" />
                    Auto Trends
                  </Button>
                </div>
                <Input
                  placeholder="e.g. Project Acoustic Kitty: The $20M CIA Secret Spy Cat..."
                  value={topicHint}
                  onChange={(e) => setTopicHint(e.target.value)}
                  className="h-8 text-xs"
                />
              </div>

              <Separator />

              <div className="grid gap-2 sm:grid-cols-2">
                <div className="flex items-center justify-between rounded-lg border border-border/60 p-2.5 bg-muted/20">
                  <div className="space-y-0.5">
                    <Label className="text-xs font-medium">Dry Run Mode</Label>
                    <p className="text-[10px] text-muted-foreground">Local render preview</p>
                  </div>
                  <Switch checked={isDryRun} onCheckedChange={setIsDryRun} />
                </div>

                <div className="flex items-center justify-between rounded-lg border border-border/60 p-2.5 bg-muted/20">
                  <div className="space-y-0.5">
                    <Label className="text-xs font-medium">Auto YouTube Upload</Label>
                    <p className="text-[10px] text-muted-foreground">Post to channel</p>
                  </div>
                  <Switch checked={autoUpload} onCheckedChange={setAutoUpload} />
                </div>
              </div>
            </CardContent>
            <CardFooter className="py-2 px-3.5 border-t border-border/40">
              <Button
                onClick={handleSynthesize}
                disabled={isGenerating}
                className="w-full h-8 font-medium text-xs shadow-xs"
              >
                {isGenerating ? (
                  <>
                    <RotateCcw className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                    Synthesizing Video Stream... ({progress}%)
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-1.5 h-3.5 w-3.5" />
                    Synthesize Short Video
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
          
          <IntegrationsPanel />
        </div>

        {/* PREVIEW PLAYER (5 COLS) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <StudioPreviewPlayer
            isGenerating={isGenerating}
            progress={progress}
            stageText={stageText}
            topicTitle={topicHint}
            videoFilename={videoFilename}
            onReset={handleReset}
            onUpload={handleUpload}
            isUploading={isUploading}
          />
          {/* TERMINAL LOGS */}
          <PipelineLogs isGenerating={isGenerating} />
        </div>
      </div>
    </div>
  );
}
