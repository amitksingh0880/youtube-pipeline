import {
  Upload,
  Volume2,
  Cpu,
  ShieldCheck,
  Globe,
  Radio,
  Server,
  Database,
  Layers,
  Zap,
} from "lucide-react";

export const PEXELS_CONFIG = {
  provider: "Pexels API",
  baseUrl: "https://api.pexels.com/v1",
  orientation: "portrait",
  queryDefault: "cinematic 4k background",
};

export const STUDIO_STATS = [
  { label: "Today's Uploads", value: "1 / 6", sub: "Spam Limit Aligned", icon: Upload, color: "text-blue-500" },
  { label: "Voice Engine", value: "Edge Neural TTS", sub: "$0 Unmetered", icon: Volume2, color: "text-emerald-500" },
  { label: "Render Acceleration", value: "FFmpeg NVENC", sub: "1080x1920 60FPS", icon: Cpu, color: "text-amber-500" },
  { label: "Safety Limits", value: "Compliant", sub: "#Shorts Altered Flag", icon: ShieldCheck, color: "text-violet-500" },
];

export const NICHES_CONFIG = [
  { id: "dark_history", name: "Dark History & Unsolved Paradoxes", rpm: "$4.00 - $8.50", volume: "High", voice: "ChristopherNeural", retention: "78%", icon: "📜", avgViews: "1.2M" },
  { id: "tech_ai", name: "Tech & AI Breakthroughs", rpm: "$4.50 - $9.00", volume: "Very High", voice: "GuyNeural", retention: "72%", icon: "🤖", avgViews: "890K" },
  { id: "hindi_mythology", name: "Hindu Mythology (Hindi)", rpm: "$2.00 - $5.50", volume: "Extreme", default_voice: "hi-IN-MadhurNeural", retention: "85%", icon: "🕉️", avgViews: "3.5M", language: "hi" },
  { id: "hindi_motivation", name: "Motivation & Life Rules (Hindi)", rpm: "$2.50 - $6.00", volume: "Extreme", default_voice: "hi-IN-SwaraNeural", retention: "82%", icon: "🔥", avgViews: "2.8M", language: "hi" },
  { id: "psychology", name: "Human Psychology & Mind Games", rpm: "$3.50 - $7.00", volume: "Extreme", voice: "ChristopherNeural", retention: "81%", icon: "🧠", avgViews: "1.5M" },
  { id: "space_science", name: "Cosmic Mysteries & Deep Space", rpm: "$3.00 - $6.50", volume: "Medium", voice: "ChristopherNeural", retention: "75%", icon: "🚀", avgViews: "720K" },
  { id: "wealth_finance", name: "Wealth Psychology & Money Rules", rpm: "$5.00 - $12.00", volume: "Extreme", voice: "GuyNeural", retention: "84%", icon: "📈", avgViews: "2.1M" },
  { id: "true_crime", name: "Unsolved Files & True Crime", rpm: "$4.20 - $8.00", volume: "Very High", voice: "AriaNeural", retention: "83%", icon: "🔍", avgViews: "1.8M" },
  { id: "fitness", name: "Fitness & Biohacking", rpm: "$3.20 - $6.80", volume: "High", voice: "GuyNeural", retention: "76%", icon: "💪", avgViews: "650K" },
  { id: "stoicism", name: "Stoic Philosophy & Daily Rules", rpm: "$3.80 - $7.50", volume: "High", voice: "GuyNeural", retention: "79%", icon: "🏛️", avgViews: "940K" },
  { id: "luxury_wealth", name: "Luxury & Wealth Rules", rpm: "$5.20 - $11.50", volume: "Very High", voice: "ChristopherNeural", retention: "82%", icon: "💎", avgViews: "1.1M" },
];

export const PIPELINE_MODES_CONFIG = [
  {
    id: "local",
    title: "Local Studio (FFmpeg)",
    badge: "100% Free",
    badgeVariant: "default" as const,
    desc: "$0 cost, unmetered rendering. FFmpeg native transcode + Edge-TTS audio stream + dynamic ASS kinetic typography.",
    icon: Cpu,
  },
  {
    id: "ssemble",
    title: "Ssemble Cloud AI",
    badge: "Cloud Bridge",
    badgeVariant: "secondary" as const,
    desc: "Rendered local assets tunnelled to aiclipping.ssemble.com. Includes cloud meme hooks & licensed sound layers.",
    icon: Globe,
  },
  {
    id: "clipper",
    title: "Trend Clipper",
    badge: "Auto Remix",
    badgeVariant: "outline" as const,
    desc: "Extract vertical highlight snippets from long-form YouTube URLs with auto facial framing & whisper transcription.",
    icon: Radio,
  },
];

export const DIAGNOSTICS_SERVICES = [
  { name: "FastAPI Engine", status: "Online", ping: "12ms", icon: Server },
  { name: "Gemini 2.0 Flash API", status: "Synced", ping: "45ms", icon: Cpu },
  { name: "Microsoft Edge TTS", status: "Ready", ping: "22ms", icon: Radio },
  { name: "FFmpeg 9.0 Binary", status: "v9.0 Found", ping: "2ms", icon: Cpu },
  { name: "SQLite Telemetry DB", status: "Connected", ping: "1ms", icon: Database },
];

export const DIAGNOSTICS_LOGS = [
  "[21:45:01] System initialization starting...",
  "[21:45:02] FFmpeg 9.0 located at C:\\ffmpeg\\bin\\ffmpeg.exe",
  "[21:45:02] Gemini API authenticated successfully (gemini-2.0-flash).",
  "[21:46:15] Synthesizing narration via Edge TTS (en-US-ChristopherNeural)...",
  "[21:46:18] Notice: Audio loudness normalized to -14 LUFS target.",
  "[21:46:20] Generated ASS subtitle file with Hormozi kinetic typography.",
  "[21:46:22] Hardware acceleration NVENC engaged for 1080x1920 60FPS encode.",
  "[21:46:25] Render completed in 3.82 seconds. Output saved to data/renders/short_01.mp4",
  "[21:46:26] Awaiting next studio dispatch instruction...",
];

export const HISTORY_ITEMS = [
  {
    id: "1",
    title: "Project Acoustic Kitty: $20M CIA Secret Spy Cat",
    status: "Published",
    date: "2 hours ago",
    niche: "Dark History",
    views: "1.2K",
    duration: "0:52",
    renderTime: "3.4s",
  },
  {
    id: "2",
    title: "The Bystander Effect & Mind Games",
    status: "Rendered",
    date: "5 hours ago",
    niche: "Psychology",
    views: "-",
    duration: "0:48",
    renderTime: "4.1s",
  },
  {
    id: "3",
    title: "Billionaire Wealth Mindset Rules",
    status: "Failed",
    date: "Yesterday",
    niche: "Wealth Finance",
    views: "-",
    duration: "0:58",
    renderTime: "Failed",
  },
  {
    id: "4",
    title: "The Voyager 1 Cosmic Mystery",
    status: "Published",
    date: "2 days ago",
    niche: "Space Science",
    views: "5.8K",
    duration: "0:55",
    renderTime: "3.9s",
  },
  {
    id: "5",
    title: "Marcus Aurelius Stoic Life Lessons",
    status: "Rendered",
    date: "3 days ago",
    niche: "Stoicism",
    views: "-",
    duration: "0:45",
    renderTime: "3.2s",
  },
  {
    id: "6",
    title: "AI Singularity 2026 Prediction",
    status: "Published",
    date: "4 days ago",
    niche: "Tech & AI",
    views: "12.4K",
    duration: "0:59",
    renderTime: "4.5s",
  },
];

export const ARCHITECTURE_STEPS = [
  {
    step: "01. Narration",
    title: "Edge TTS Synthesis",
    desc: "Streams unmetered neural speech via Microsoft Edge TTS with pitch/rate shaping.",
    icon: Cpu,
  },
  {
    step: "02. Subtitle Parsing",
    title: "Kinetic ASS Overlay",
    desc: "Generates ASS subtitle files with word-by-word highlight colors & Hormozi pop effects.",
    icon: Layers,
  },
  {
    step: "03. Composite Render",
    title: "FFmpeg NVENC Transcode",
    desc: "Composites 1080x1920 60FPS vertical footage with GPU hardware acceleration.",
    icon: Zap,
  },
];

export const ARCHITECTURE_FAQS = [
  {
    id: "item-1",
    question: "How does Local Studio rendering achieve $0 cost?",
    answer: "Local Studio uses FFmpeg installed on your machine. Speech synthesis uses free unmetered Edge TTS streams, subtitle alignment is generated via ASS text templates, and video compositing runs locally on your GPU/CPU without invoking paid APIs.",
  },
  {
    id: "item-2",
    question: "When is the Ssemble Cloud API fallback triggered?",
    answer: "If local FFmpeg rendering experiences hardware memory pressure or missing codec dependencies, the pipeline seamlessly tunnels the payload to aiclipping.ssemble.com using your configured API key.",
  },
  {
    id: "item-3",
    question: "How is YouTube Shorts compliance enforced?",
    answer: "All uploaded videos automatically include the mandatory #Shorts tag in the title and description, as well as the YouTube Data API v3 compliance flag for AI-generated synthetic media.",
  },
];
