"use client";

import React, { useState, useRef } from "react";
import { FileVideo, Zap, CheckCircle2, Play, Pause, Download, Upload, RotateCcw, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface StudioPreviewPlayerProps {
  isGenerating: boolean;
  progress: number;
  stageText: string;
  topicTitle: string;
  videoFilename?: string | null;
  onReset: () => void;
  onUpload?: () => void;
  isUploading?: boolean;
}

const SAMPLE_VIDEO_URL = "https://cdn.pixabay.com/video/2021/04/12/70860-536486121_tiny.mp4";

export function StudioPreviewPlayer({
  isGenerating,
  progress,
  stageText,
  topicTitle,
  videoFilename,
  onReset,
  onUpload,
  isUploading = false,
}: StudioPreviewPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(true);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const currentVideoUrl = videoFilename ? `/api/video/${videoFilename}` : SAMPLE_VIDEO_URL;

  return (
    <Card className="shadow-sm border-border/60 overflow-hidden h-full flex flex-col">
      <CardHeader className="py-2.5 px-3.5 border-b border-border/50">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xs font-semibold flex items-center gap-2">
            <FileVideo className="h-3.5 w-3.5 text-primary" />
            Interactive Video Preview
          </CardTitle>
          <div className="flex items-center gap-1.5">
            {progress === 100 && (
              <Badge variant="secondary" className="text-[9px] px-1.5 py-0 text-emerald-500 border-emerald-500/20 bg-emerald-500/10">
                Render Ready
              </Badge>
            )}
            <Badge variant="outline" className="text-[9px] px-1.5 py-0">
              1080x1920 (9:16)
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-3 flex-1 flex flex-col items-center justify-center bg-muted/20 relative min-h-[380px]">
        {isGenerating ? (
          /* GENERATING STATE WITH STEP-BY-STEP PROGRESS */
          <div className="w-full space-y-4 text-center p-4 max-w-sm">
            <div className="h-14 w-14 mx-auto rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center animate-pulse">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <div className="space-y-1">
              <h4 className="text-xs font-semibold">Synthesizing Short Video...</h4>
              <p className="text-[11px] text-muted-foreground font-mono transition-all">
                {stageText || "Processing video pipeline..."}
              </p>
            </div>
            <div className="space-y-1.5">
              <Progress value={progress} className="h-2 w-full" />
              <div className="flex items-center justify-between text-[10px] text-muted-foreground font-mono">
                <span>Stage Progress</span>
                <span className="font-semibold text-foreground">{progress}%</span>
              </div>
            </div>
          </div>
        ) : progress === 100 ? (
          /* GENERATION COMPLETE: REAL 9:16 PREVIEW PLAYER */
          <div className="w-full h-full flex flex-col items-center justify-between space-y-3">
            {/* 9:16 VERTICAL VIDEO CONTAINER */}
            <div className="relative aspect-[9/16] w-full max-w-[210px] rounded-xl overflow-hidden border border-border/70 shadow-lg bg-black group">
              <video
                ref={videoRef}
                src={currentVideoUrl}
                autoPlay
                loop
                muted
                playsInline
                className="w-full h-full object-cover"
              />
              
              {/* OVERLAY KINETIC SUBTITLE SIMULATION */}
              <div className="absolute inset-x-3 bottom-10 bg-black/60 backdrop-blur-xs p-2 rounded-lg text-center border border-white/10">
                <p className="text-[11px] font-bold text-yellow-300 drop-shadow-md leading-tight uppercase tracking-wide">
                  {topicTitle ? `"${topicTitle.slice(0, 45)}..."` : '"WAIT UNTIL YOU HEAR THIS SECRET..."'}
                </p>
                <span className="text-[9px] text-emerald-400 font-mono mt-0.5 block">
                  [Edge TTS + ASS Subtitles]
                </span>
              </div>

              {/* OVERLAY PLAY/PAUSE TRIGGER */}
              <button
                onClick={togglePlay}
                className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <div className="h-10 w-10 rounded-full bg-background/80 flex items-center justify-center shadow-md">
                  {isPlaying ? (
                    <Pause className="h-5 w-5 text-foreground" />
                  ) : (
                    <Play className="h-5 w-5 text-foreground ml-0.5" />
                  )}
                </div>
              </button>

              {/* TOP BADGE */}
              <div className="absolute top-2 left-2">
                <Badge variant="secondary" className="text-[8px] px-1 py-0 bg-black/60 text-white backdrop-blur-xs font-mono">
                  1080x1920 • 60FPS
                </Badge>
              </div>
            </div>

            {/* ACTION BUTTONS */}
            <div className="w-full max-w-[210px] space-y-1.5">
              <div className="grid grid-cols-2 gap-1.5">
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7 text-[10px] px-2"
                  render={<a href={currentVideoUrl} download />}
                >
                  <Download className="h-3 w-3 mr-1" /> Download
                </Button>
                <Button 
                  size="sm" 
                  variant="default" 
                  className="h-7 text-[10px] px-2"
                  onClick={onUpload}
                  disabled={isUploading || !onUpload}
                >
                  {isUploading ? (
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                  ) : (
                    <Upload className="h-3 w-3 mr-1" />
                  )}
                  {isUploading ? "Uploading..." : "Upload"}
                </Button>
              </div>
              <Button size="sm" variant="ghost" onClick={onReset} className="w-full h-6 text-[10px] text-muted-foreground" disabled={isUploading}>
                <RotateCcw className="h-2.5 w-2.5 mr-1" /> Re-synthesize
              </Button>
            </div>
          </div>
        ) : (
          /* INITIAL EMPTY STATE */
          <div className="text-center space-y-2 max-w-xs">
            <div className="h-12 w-12 mx-auto rounded-xl bg-background border shadow-xs flex items-center justify-center">
              <Play className="h-5 w-5 text-muted-foreground ml-0.5" />
            </div>
            <div className="space-y-0.5">
              <h4 className="text-xs font-semibold">Awaiting Generation</h4>
              <p className="text-[10px] text-muted-foreground leading-relaxed">
                Click <span className="font-semibold text-foreground">"Synthesize Short Video"</span> to begin AI generation & stream your 9:16 vertical video preview here.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

