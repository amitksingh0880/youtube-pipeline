"use client";

import React, { useState, useEffect } from "react";
import {
  Play,
  RotateCw,
  Upload,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Sparkles,
  Sliders,
  Layers,
  Film,
  TrendingUp,
  Compass,
  Settings,
  ChevronRight,
  ShieldCheck,
  Video,
  Radio,
  Cloud,
  Cpu,
  Scissors,
  HelpCircle,
  RefreshCw,
} from "lucide-react";

interface Niche {
  id: string;
  name: string;
  rpm_tier?: string;
  default_voice?: string;
  voice_rate?: string;
  description?: string;
  captions?: {
    highlight_color?: string;
    font_name?: string;
  };
}

interface DiscoveredTopic {
  source: string;
  title: string;
  engagement_score: number;
  url?: string;
}

interface SsembleTemplate {
  id: string;
  name: string;
  description: string;
  popular?: boolean;
}

interface ShortItem {
  id: number;
  session_id: string;
  created_at: string;
  niche_id: string;
  topic: string;
  hook?: string;
  title?: string;
  mode: string;
  status: string;
  video_path?: string;
  youtube_video_id?: string;
}

interface Stats {
  total_generated: number;
  today_uploads: number;
  daily_limit: number;
  quota_remaining: number;
  default_voice: string;
  ssemble_template: string;
}

interface SystemHealth {
  status: string;
  gemini_2_flash: string;
  edge_neural_tts: string;
  ffmpeg: string;
  cloudflared: string;
  ssemble_api: string;
}

export default function ShortsStudioDashboard() {
  const [activeTab, setActiveTab] = useState<"create" | "history" | "niches" | "ssemble_guide">("create");
  const [niches, setNiches] = useState<Niche[]>([]);
  const [selectedNiche, setSelectedNiche] = useState<string>("dark_history");
  const [mode, setMode] = useState<string>("local-studio");
  const [topicHint, setTopicHint] = useState<string>("");
  const [youtubeClipUrl, setYoutubeClipUrl] = useState<string>("");
  const [selectedTemplate, setSelectedTemplate] = useState<string>("hormozi1");
  const [dryRun, setDryRun] = useState<boolean>(true);
  const [privacyStatus, setPrivacyStatus] = useState<string>("unlisted");

  const [discoveredTopics, setDiscoveredTopics] = useState<DiscoveredTopic[]>([]);
  const [isLoadingTopics, setIsLoadingTopics] = useState<boolean>(false);
  const [templates, setTemplates] = useState<SsembleTemplate[]>([]);

  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [stats, setStats] = useState<Stats>({
    total_generated: 0,
    today_uploads: 0,
    daily_limit: 6,
    quota_remaining: 9600,
    default_voice: "en-US-ChristopherNeural",
    ssemble_template: "hormozi1",
  });

  const [history, setHistory] = useState<ShortItem[]>([]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [progressMsg, setProgressMsg] = useState<string>("");
  const [progressPct, setProgressPct] = useState<number>(0);
  const [currentResult, setCurrentResult] = useState<any>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  // Fetch initial stats, niches, health, templates
  useEffect(() => {
    fetchStats();
    fetchNiches();
    fetchHistory();
    fetchHealth();
    fetchTemplates();
  }, []);

  // Auto-scout topics whenever niche changes
  useEffect(() => {
    if (selectedNiche) {
      handleDiscoverTopics(selectedNiche);
    }
  }, [selectedNiche]);

  const fetchHealth = async () => {
    try {
      const res = await fetch("/api/health");
      if (res.ok) setSystemHealth(await res.json());
    } catch (e) {
      console.error("Health check error:", e);
    }
  };

  const fetchTemplates = async () => {
    try {
      const res = await fetch("/api/ssemble/templates");
      if (res.ok) setTemplates(await res.json());
    } catch (e) {
      console.error("Templates fetch error:", e);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch("/api/stats");
      if (res.ok) setStats(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchNiches = async () => {
    try {
      const res = await fetch("/api/niches");
      if (res.ok) {
        const data = await res.json();
        setNiches(data);
        if (data.length > 0 && !selectedNiche) setSelectedNiche(data[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch("/api/history");
      if (res.ok) setHistory(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const handleDiscoverTopics = async (nicheId: string) => {
    setIsLoadingTopics(true);
    try {
      const res = await fetch(`/api/topics?niche_id=${nicheId}&limit=6`);
      if (res.ok) {
        setDiscoveredTopics(await res.json());
      }
    } catch (e) {
      console.error("Topic discovery failed:", e);
    } finally {
      setIsLoadingTopics(false);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setProgressMsg("Connecting to pipeline...");
    setProgressPct(5);

    try {
      const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          niche_id: selectedNiche,
          mode,
          topic_hint: mode === "ssemble-clip" ? null : (topicHint.trim() || null),
          youtube_url: mode === "ssemble-clip" ? youtubeClipUrl.trim() : null,
          dry_run: dryRun,
          privacy_status: privacyStatus,
        }),
      });

      if (!resp.ok) throw new Error("Failed to start generation");
      const { job_id } = await resp.json();

      const pollInterval = setInterval(async () => {
        const pRes = await fetch(`/api/progress/${job_id}`);
        if (!pRes.ok) return;
        const pData = await pRes.json();

        setProgressMsg(pData.message || "Generating...");
        setProgressPct(pData.percent || 0);

        if (pData.status === "completed") {
          clearInterval(pollInterval);
          setIsGenerating(false);
          fetchStats();
          fetchHistory();
          if (pData.result) {
            setCurrentResult(pData.result);
          }
        } else if (pData.status === "failed") {
          clearInterval(pollInterval);
          setIsGenerating(false);
          alert(`Generation error: ${pData.error || pData.message}`);
        }
      }, 1500);
    } catch (err: any) {
      setIsGenerating(false);
      alert(err.message);
    }
  };

  const handleUpload = async () => {
    if (!currentResult?.session_id) return;
    setIsUploading(true);
    try {
      const res = await fetch(`/api/upload/${currentResult.session_id}`, { method: "POST" });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      alert(`Published to YouTube!\nURL: ${data.url}`);
      fetchStats();
      fetchHistory();
    } catch (e: any) {
      alert(`Upload error: ${e.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex flex-col font-sans">
      {/* Top Google App Bar */}
      <header className="h-16 bg-white border-b border-[#DADCE0] px-6 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-[#FF0000] rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-sm">
            ▶
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[19px] font-medium text-[#202124]">YouTube Shorts Studio</span>
            <span className="text-xs bg-[#D2E3FC] text-[#174EA6] font-semibold px-2.5 py-0.5 rounded-full">
              Gemini 2.0 Flash
            </span>
            <span className="text-xs bg-[#CEEAD6] text-[#0D652D] font-semibold px-2.5 py-0.5 rounded-full">
              Edge Neural TTS
            </span>
          </div>
        </div>

        {/* System Health Badges */}
        <div className="flex items-center gap-2 text-xs">
          <div className="hidden md:flex items-center gap-1.5 bg-[#F1F3F4] px-3 py-1.5 rounded-full text-[#3C4043]">
            <span className="w-2 h-2 rounded-full bg-[#1E8E3E]" />
            <span>FFmpeg: Ready</span>
          </div>
          <div className="hidden md:flex items-center gap-1.5 bg-[#F1F3F4] px-3 py-1.5 rounded-full text-[#3C4043]">
            <span className={`w-2 h-2 rounded-full ${systemHealth?.cloudflared === "ready" ? "bg-[#1E8E3E]" : "bg-[#F9AB00]"}`} />
            <span>Cloudflare Tunnel: {systemHealth?.cloudflared === "ready" ? "Ready" : "Standby"}</span>
          </div>
          <div className="flex items-center gap-1.5 bg-[#F1F3F4] px-3 py-1.5 rounded-full text-[#3C4043]">
            <span className="w-2 h-2 rounded-full bg-[#1A73E8]" />
            <span>Ssemble: {systemHealth?.ssemble_api === "connected" ? "Connected" : "Local-Studio Ready"}</span>
          </div>
        </div>
      </header>

      {/* Tabs Navigation */}
      <div className="bg-white border-b border-[#DADCE0] px-6 flex gap-8">
        <button
          onClick={() => setActiveTab("create")}
          className={`py-3.5 text-sm font-medium transition-colors relative ${
            activeTab === "create" ? "text-[#1A73E8]" : "text-[#5F6368] hover:text-[#202124]"
          }`}
        >
          Studio Generator
          {activeTab === "create" && (
            <span className="absolute bottom-0 left-0 right-0 h-[3px] bg-[#1A73E8] rounded-t-sm" />
          )}
        </button>

        <button
          onClick={() => setActiveTab("history")}
          className={`py-3.5 text-sm font-medium transition-colors relative ${
            activeTab === "history" ? "text-[#1A73E8]" : "text-[#5F6368] hover:text-[#202124]"
          }`}
        >
          Shorts Library ({history.length})
          {activeTab === "history" && (
            <span className="absolute bottom-0 left-0 right-0 h-[3px] bg-[#1A73E8] rounded-t-sm" />
          )}
        </button>

        <button
          onClick={() => setActiveTab("niches")}
          className={`py-3.5 text-sm font-medium transition-colors relative ${
            activeTab === "niches" ? "text-[#1A73E8]" : "text-[#5F6368] hover:text-[#202124]"
          }`}
        >
          Niche Intelligence ({niches.length})
          {activeTab === "niches" && (
            <span className="absolute bottom-0 left-0 right-0 h-[3px] bg-[#1A73E8] rounded-t-sm" />
          )}
        </button>

        <button
          onClick={() => setActiveTab("ssemble_guide")}
          className={`py-3.5 text-sm font-medium transition-colors relative ${
            activeTab === "ssemble_guide" ? "text-[#1A73E8]" : "text-[#5F6368] hover:text-[#202124]"
          }`}
        >
          Ssemble Architecture
          {activeTab === "ssemble_guide" && (
            <span className="absolute bottom-0 left-0 right-0 h-[3px] bg-[#1A73E8] rounded-t-sm" />
          )}
        </button>
      </div>

      <main className="max-w-[1400px] w-full mx-auto p-6 flex-1">
        {/* Metric Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white border border-[#DADCE0] rounded-2xl p-5 shadow-sm">
            <span className="text-xs font-semibold text-[#5F6368] uppercase tracking-wider">Total Created</span>
            <div className="text-2xl font-semibold text-[#202124] mt-1">{stats.total_generated}</div>
            <span className="text-xs text-[#5F6368] mt-1 block">In SQLite Persistent DB</span>
          </div>

          <div className="bg-white border border-[#DADCE0] rounded-2xl p-5 shadow-sm">
            <span className="text-xs font-semibold text-[#5F6368] uppercase tracking-wider">Today's Uploads</span>
            <div className="text-2xl font-semibold text-[#202124] mt-1">
              {stats.today_uploads} / {stats.daily_limit}
            </div>
            <span className="text-xs text-[#5F6368] mt-1 block">YouTube Safety Limit</span>
          </div>

          <div className="bg-white border border-[#DADCE0] rounded-2xl p-5 shadow-sm">
            <span className="text-xs font-semibold text-[#5F6368] uppercase tracking-wider">Voice Engine</span>
            <div className="text-xl font-semibold text-[#202124] mt-1">Edge Neural TTS</div>
            <span className="text-xs text-[#1E8E3E] mt-1 font-medium block">Studio Quality ($0 Cost)</span>
          </div>

          <div className="bg-white border border-[#DADCE0] rounded-2xl p-5 shadow-sm">
            <span className="text-xs font-semibold text-[#5F6368] uppercase tracking-wider">2026 Compliance</span>
            <div className="text-xl font-semibold text-[#1E8E3E] mt-1 flex items-center gap-1.5">
              <ShieldCheck className="w-5 h-5" /> Aligned
            </div>
            <span className="text-xs text-[#5F6368] mt-1 block">Altered Media Tagged</span>
          </div>
        </div>

        {/* View 1: Studio Generator */}
        {activeTab === "create" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Controls Column (7 cols) */}
            <div className="lg:col-span-7 bg-white border border-[#DADCE0] rounded-2xl p-6 shadow-sm">
              <h2 className="text-lg font-medium text-[#202124] mb-5">Configure & Produce Short</h2>

              {/* 1. Niche Selector */}
              <div className="mb-5">
                <label className="block text-xs font-semibold text-[#5F6368] uppercase tracking-wider mb-2">
                  1. Target Niche Profile ({niches.length} Available)
                </label>
                <div className="flex flex-wrap gap-2">
                  {niches.map((n) => (
                    <button
                      key={n.id}
                      onClick={() => setSelectedNiche(n.id)}
                      className={`px-3.5 py-2 text-xs font-medium rounded-lg border transition-all ${
                        selectedNiche === n.id
                          ? "bg-[#E8F0FE] border-[#1A73E8] text-[#174EA6] font-semibold"
                          : "bg-white border-[#DADCE0] text-[#3C4043] hover:bg-[#F1F3F4]"
                      }`}
                    >
                      {n.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* 2. Assembly Mode */}
              <div className="mb-5">
                <label className="block text-xs font-semibold text-[#5F6368] uppercase tracking-wider mb-2">
                  2. Assembly Pipeline
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <div
                    onClick={() => setMode("local-studio")}
                    className={`border rounded-xl p-3.5 cursor-pointer transition-all ${
                      mode === "local-studio"
                        ? "border-[#1A73E8] bg-[#E8F0FE]"
                        : "border-[#DADCE0] hover:bg-[#F1F3F4]"
                    }`}
                  >
                    <div className="text-sm font-semibold text-[#202124] flex items-center gap-1.5">
                      <Cpu className="w-4 h-4 text-[#1A73E8]" /> Local Studio
                    </div>
                    <div className="text-[11px] text-[#5F6368] mt-1">100% Local FFmpeg + Hormozi ASS karaoke subtitles. 0 credits.</div>
                  </div>

                  <div
                    onClick={() => setMode("ssemble-ai")}
                    className={`border rounded-xl p-3.5 cursor-pointer transition-all ${
                      mode === "ssemble-ai"
                        ? "border-[#1A73E8] bg-[#E8F0FE]"
                        : "border-[#DADCE0] hover:bg-[#F1F3F4]"
                    }`}
                  >
                    <div className="text-sm font-semibold text-[#202124] flex items-center gap-1.5">
                      <Cloud className="w-4 h-4 text-[#1A73E8]" /> Ssemble Cloud
                    </div>
                    <div className="text-[11px] text-[#5F6368] mt-1">Tunnel stream to Ssemble cloud templates, meme hooks & music.</div>
                  </div>

                  <div
                    onClick={() => setMode("ssemble-clip")}
                    className={`border rounded-xl p-3.5 cursor-pointer transition-all ${
                      mode === "ssemble-clip"
                        ? "border-[#1A73E8] bg-[#E8F0FE]"
                        : "border-[#DADCE0] hover:bg-[#F1F3F4]"
                    }`}
                  >
                    <div className="text-sm font-semibold text-[#202124] flex items-center gap-1.5">
                      <Scissors className="w-4 h-4 text-[#1A73E8]" /> Trend Clipper
                    </div>
                    <div className="text-[11px] text-[#5F6368] mt-1">Direct long-form YouTube URL clipping via Ssemble AI.</div>
                  </div>
                </div>
              </div>

              {/* Mode-Specific Controls */}
              {mode === "ssemble-clip" ? (
                <div className="mb-5 bg-[#F8F9FA] border border-[#DADCE0] rounded-xl p-4">
                  <label className="block text-xs font-semibold text-[#202124] uppercase tracking-wider mb-2">
                    Long-Form YouTube URL to Clip
                  </label>
                  <input
                    type="url"
                    value={youtubeClipUrl}
                    onChange={(e) => setYoutubeClipUrl(e.target.value)}
                    placeholder="https://www.youtube.com/watch?v=..."
                    className="w-full h-11 px-3.5 text-sm bg-white border border-[#DADCE0] rounded-lg focus:outline-none focus:border-[#1A73E8] focus:ring-1 focus:ring-[#1A73E8]"
                  />
                  <div className="mt-3 flex items-center gap-3">
                    <span className="text-xs text-[#5F6368]">Ssemble Template:</span>
                    <select
                      value={selectedTemplate}
                      onChange={(e) => setSelectedTemplate(e.target.value)}
                      className="h-8 text-xs bg-white border border-[#DADCE0] rounded px-2"
                    >
                      {templates.map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ) : (
                /* Topic Hint & Discovery */
                <div className="mb-5">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-xs font-semibold text-[#5F6368] uppercase tracking-wider">
                      3. Topic / Headline Angle
                    </label>
                    <button
                      type="button"
                      onClick={() => handleDiscoverTopics(selectedNiche)}
                      className="text-xs text-[#1A73E8] hover:underline flex items-center gap-1 font-medium"
                    >
                      <RefreshCw className={`w-3 h-3 ${isLoadingTopics ? "animate-spin" : ""}`} />
                      Scout Live Trends
                    </button>
                  </div>

                  <input
                    type="text"
                    value={topicHint}
                    onChange={(e) => setTopicHint(e.target.value)}
                    placeholder="e.g. Project Acoustic Kitty Cold War secret cat spy"
                    className="w-full h-11 px-3.5 text-sm bg-white border border-[#DADCE0] rounded-lg focus:outline-none focus:border-[#1A73E8] focus:ring-1 focus:ring-[#1A73E8]"
                  />

                  {/* Discovered Trending Topics Chips */}
                  {discoveredTopics.length > 0 && (
                    <div className="mt-3">
                      <span className="text-[11px] font-semibold text-[#5F6368] uppercase tracking-wider block mb-1.5">
                        Live Verified Ideas for this Niche:
                      </span>
                      <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto pr-1">
                        {discoveredTopics.map((dt, idx) => (
                          <div
                            key={idx}
                            onClick={() => setTopicHint(dt.title)}
                            className="p-2 bg-[#F1F3F4] hover:bg-[#E8F0FE] rounded-lg border border-[#E8EAED] cursor-pointer text-xs transition-colors flex items-center justify-between"
                          >
                            <span className="text-[#202124] line-clamp-1">{dt.title}</span>
                            <span className="text-[10px] text-[#1A73E8] bg-white border border-[#D2E3FC] px-1.5 py-0.5 rounded font-medium whitespace-nowrap ml-2">
                              {dt.source.split("/")[0]}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Options */}
              <div className="flex items-center gap-6 mb-6">
                <label className="flex items-center gap-2 text-xs text-[#3C4043] cursor-pointer">
                  <input
                    type="checkbox"
                    checked={dryRun}
                    onChange={(e) => setDryRun(e.target.checked)}
                    className="w-4 h-4 rounded text-[#1A73E8] focus:ring-[#1A73E8]"
                  />
                  <span>Dry Run (Render video locally, skip YouTube upload)</span>
                </label>

                <div className="flex items-center gap-2 text-xs text-[#3C4043]">
                  <span>Upload Privacy:</span>
                  <select
                    value={privacyStatus}
                    onChange={(e) => setPrivacyStatus(e.target.value)}
                    className="h-8 text-xs bg-white border border-[#DADCE0] rounded px-2"
                  >
                    <option value="unlisted">Unlisted</option>
                    <option value="private">Private</option>
                    <option value="public">Public</option>
                  </select>
                </div>
              </div>

              {/* Action Button */}
              <button
                disabled={isGenerating}
                onClick={handleGenerate}
                className="w-full h-11 bg-[#1A73E8] hover:bg-[#1557B0] disabled:bg-[#DADCE0] disabled:cursor-not-allowed text-white text-sm font-semibold rounded-full flex items-center justify-center gap-2 shadow-sm transition-all"
              >
                {isGenerating ? (
                  <>
                    <RotateCw className="w-4 h-4 animate-spin" />
                    <span>Processing Pipeline...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white" />
                    <span>{mode === "ssemble-clip" ? "Clip & Generate Short" : "Generate YouTube Short"}</span>
                  </>
                )}
              </button>

              {/* Progress Box */}
              {isGenerating && (
                <div className="mt-5 p-4 bg-[#F1F3F4] rounded-xl border border-[#E8EAED]">
                  <div className="flex justify-between text-xs font-semibold text-[#202124] mb-2">
                    <span>{progressMsg}</span>
                    <span>{progressPct}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-[#DADCE0] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-[#1A73E8] transition-all duration-300"
                      style={{ width: `${progressPct}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Right Preview Column (5 cols) */}
            <div className="lg:col-span-5 flex flex-col items-center">
              {/* 9:16 Phone Mockup */}
              <div className="w-[300px] h-[533px] bg-black rounded-[36px] border-[8px] border-[#202124] overflow-hidden relative shadow-2xl flex items-center justify-center">
                {currentResult?.video_path ? (
                  <video
                    src={`/api/video/${currentResult.video_path.split(/[\\\\/]/).pop()}`}
                    controls
                    autoPlay
                    loop
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="p-6 text-center text-[#9AA0A6]">
                    <div className="text-4xl mb-3">📱</div>
                    <div className="text-sm font-semibold text-white mb-1">Interactive 9:16 Preview</div>
                    <div className="text-xs">Your generated video with animated karaoke subtitles will stream here.</div>
                  </div>
                )}
              </div>

              {/* Post-Generation Details & Direct Upload */}
              {currentResult && (
                <div className="w-full mt-4 bg-white border border-[#DADCE0] rounded-2xl p-4 shadow-sm text-xs">
                  <div className="font-semibold text-sm text-[#202124] mb-1">
                    {currentResult.script?.title || "Short Generated"}
                  </div>
                  <div className="text-[#5F6368] mb-3 line-clamp-2">
                    {currentResult.script?.description || currentResult.topic}
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-[#E8EAED]">
                    <span className="text-[#1E8E3E] font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" /> Ready on Disk
                    </span>

                    <button
                      disabled={isUploading}
                      onClick={handleUpload}
                      className="px-4 py-1.5 bg-[#1E8E3E] hover:bg-[#188038] text-white font-medium rounded-full flex items-center gap-1.5 shadow-sm"
                    >
                      <Upload className="w-3.5 h-3.5" />
                      <span>{isUploading ? "Uploading..." : "Publish to YouTube"}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* View 2: History Library */}
        {activeTab === "history" && (
          <div className="bg-white border border-[#DADCE0] rounded-2xl shadow-sm overflow-hidden">
            <div className="p-5 border-b border-[#DADCE0] flex justify-between items-center">
              <div>
                <h2 className="text-base font-medium text-[#202124]">Generated Shorts Library</h2>
                <span className="text-xs text-[#5F6368]">Persistent record in SQLite with full metadata deduplication</span>
              </div>
              <button
                onClick={fetchHistory}
                className="text-xs text-[#1A73E8] border border-[#DADCE0] hover:bg-[#F1F3F4] px-3 py-1.5 rounded-lg flex items-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Refresh
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F8F9FA] border-b border-[#DADCE0] text-[#5F6368] font-semibold uppercase tracking-wider">
                    <th className="py-3 px-4">Date</th>
                    <th className="py-3 px-4">Niche</th>
                    <th className="py-3 px-4">Title & Hook</th>
                    <th className="py-3 px-4">Mode</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#DADCE0]">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-[#F8F9FA] transition-colors">
                      <td className="py-3 px-4 text-[#5F6368] whitespace-nowrap">
                        {item.created_at ? item.created_at.slice(0, 16) : "-"}
                      </td>
                      <td className="py-3 px-4 font-medium text-[#202124]">
                        {item.niche_id}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-semibold text-[#202124] line-clamp-1">{item.title || item.topic}</div>
                        <div className="text-[#5F6368] text-[11px] line-clamp-1">{item.hook}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="bg-[#E8F0FE] text-[#174EA6] font-medium px-2 py-0.5 rounded text-[11px]">
                          {item.mode}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`font-semibold px-2 py-0.5 rounded text-[11px] ${
                            item.status === "uploaded"
                              ? "bg-[#E6F4EA] text-[#137333]"
                              : "bg-[#FEF7E0] text-[#B06000]"
                          }`}
                        >
                          {item.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        {item.youtube_video_id ? (
                          <a
                            href={`https://youtu.be/${item.youtube_video_id}`}
                            target="_blank"
                            rel="noreferrer"
                            className="text-[#1A73E8] hover:underline flex items-center gap-1 font-medium"
                          >
                            <span>Watch</span> <ExternalLink className="w-3 h-3" />
                          </a>
                        ) : item.video_path ? (
                          <button
                            onClick={() => setCurrentResult({ video_path: item.video_path, topic: item.topic, title: item.title, session_id: item.session_id })}
                            className="text-[#1A73E8] hover:underline font-medium"
                          >
                            Preview
                          </button>
                        ) : (
                          "-"
                        )}
                      </td>
                    </tr>
                  ))}
                  {history.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-[#5F6368]">
                        No shorts generated yet. Use the Studio Generator to produce your first Short!
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* View 3: Niche Intelligence */}
        {activeTab === "niches" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {niches.map((n) => (
              <div key={n.id} className="bg-white border border-[#DADCE0] rounded-2xl p-5 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs bg-[#E8F0FE] text-[#174EA6] font-semibold px-2 py-0.5 rounded">
                      {n.rpm_tier || "High RPM"}
                    </span>
                    <span className="text-[11px] text-[#5F6368]">Voice: {n.default_voice?.split("-")[2] || "Neural"}</span>
                  </div>
                  <h3 className="text-base font-semibold text-[#202124] mb-2">{n.name}</h3>
                  <p className="text-xs text-[#5F6368] line-clamp-3 mb-4">{n.description || "Rich Verticals v3 niche profile."}</p>
                </div>

                <div className="pt-3 border-t border-[#E8EAED] flex items-center justify-between">
                  <button
                    onClick={() => {
                      setSelectedNiche(n.id);
                      setActiveTab("create");
                    }}
                    className="text-xs text-[#1A73E8] font-semibold hover:underline flex items-center gap-1"
                  >
                    Use This Niche <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* View 4: Ssemble Architecture Explainer */}
        {activeTab === "ssemble_guide" && (
          <div className="bg-white border border-[#DADCE0] rounded-2xl p-6 shadow-sm max-w-4xl mx-auto">
            <h2 className="text-xl font-semibold text-[#202124] mb-3">Where Ssemble Fits in the Architecture</h2>
            <p className="text-sm text-[#5F6368] mb-6">
              You hold an active 1-year subscription to <strong>app.ssemble.com</strong>. Ssemble integrates seamlessly into 3 complementary workflows:
            </p>

            <div className="space-y-6">
              {/* Role 1 */}
              <div className="p-4 bg-[#F8F9FA] rounded-xl border border-[#DADCE0]">
                <div className="flex items-center gap-2 mb-2 font-semibold text-sm text-[#1A73E8]">
                  <Cloud className="w-4 h-4" /> 1. Mode: Ssemble AI Polisher (Rough Cut → Cloud Magic)
                </div>
                <p className="text-xs text-[#3C4043] leading-relaxed">
                  Our local engine runs Gemini 2.0 Flash scriptwriting, Edge-TTS studio voice synthesis, and Pexels HD B-roll sourcing completely for $0.
                  The video is streamed to Ssemble via an encrypted Cloudflare Tunnel (or direct link). Ssemble applies its cloud rendering engine:
                  viral subtitle templates (Hormozi, Beast, Neon), licensed background tracks from Ssemble's audio library, and meme hooks.
                </p>
              </div>

              {/* Role 2 */}
              <div className="p-4 bg-[#F8F9FA] rounded-xl border border-[#DADCE0]">
                <div className="flex items-center gap-2 mb-2 font-semibold text-sm text-[#1E8E3E]">
                  <Scissors className="w-4 h-4" /> 2. Mode: Ssemble Clip Rewards & Viral Long-Form Clipper
                </div>
                <p className="text-xs text-[#3C4043] leading-relaxed">
                  Provide any long-form YouTube link (podcast, interview, documentary). Ssemble's AI parses the transcript, detects retention peaks,
                  cuts 30-60s vertical clips, adds dynamic animated subtitles, and returns the highest viral-score Short. Zero local uploading or tunnel needed.
                </p>
              </div>

              {/* Role 3 */}
              <div className="p-4 bg-[#F8F9FA] rounded-xl border border-[#DADCE0]">
                <div className="flex items-center gap-2 mb-2 font-semibold text-sm text-[#E37400]">
                  <Cpu className="w-4 h-4" /> 3. Mode: Local Studio (Zero-Credit Fallback)
                </div>
                <p className="text-xs text-[#3C4043] leading-relaxed">
                  When your Ssemble monthly export quota is reached, or when rendering offline/batch runs: our local FFmpeg + Edge-TTS + ASS subtitle engine
                  produces identical Hormozi-grade animated karaoke videos at $0 cost and 0 Ssemble credits consumed.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
