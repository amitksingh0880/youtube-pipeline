"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { KeyRound, Tv, Upload, CheckCircle2, Loader2, Play } from "lucide-react";

export function IntegrationsPanel() {
  const [hasSecret, setHasSecret] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isUploadingFile, setIsUploadingFile] = useState(false);
  const [isAuthorizing, setIsAuthorizing] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await fetch("/api/settings/youtube/status");
      if (res.ok) {
        const data = await res.json();
        setHasSecret(data.has_client_secret);
        setIsAuthenticated(data.is_authenticated);
      }
    } catch (err) {
      console.error("Failed to fetch auth status", err);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Poll status periodically in case auth happens
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      setIsAuthorizing(false);
    }
  }, [isAuthenticated]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    setIsUploadingFile(true);
    try {
      const arrayBuffer = await file.arrayBuffer();
      const res = await fetch("/api/settings/youtube/client-secret", {
        method: "POST",
        headers: {
          "Content-Type": "application/octet-stream",
        },
        body: arrayBuffer,
      });
      if (res.ok) {
        await fetchStatus();
      } else {
        alert("Failed to upload client secret.");
      }
    } catch (err) {
      alert("Error uploading file.");
    } finally {
      setIsUploadingFile(false);
    }
  };

  const handleAuthorize = async () => {
    setIsAuthorizing(true);
    try {
      const res = await fetch("/api/settings/youtube/authorize", {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        if (data.auth_url) {
          window.open(data.auth_url, "_blank", "width=500,height=600");
        }
      } else {
        const data = await res.json();
        alert("Failed to authorize: " + data.detail);
        setIsAuthorizing(false);
      }
    } catch (err) {
      alert("Error during authorization.");
      setIsAuthorizing(false);
    }
  };

  return (
    <Card className="shadow-sm border-border/60 mt-3">
      <CardHeader className="py-2.5 px-3.5 bg-muted/20 border-b border-border/50">
        <CardTitle className="text-sm font-semibold flex items-center gap-2">
          <Tv className="h-4 w-4 text-red-500" />
          YouTube Publishing Integration
        </CardTitle>
        <CardDescription className="text-xs">
          Connect your YouTube channel to enable 1-click video uploads directly from the studio.
        </CardDescription>
      </CardHeader>
      <CardContent className="px-3.5 py-4 space-y-4">
        
        {/* Step 1: Upload client_secret.json */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs font-semibold flex items-center gap-1.5">
              <span className={`flex h-4 w-4 items-center justify-center rounded-full text-[9px] font-bold ${hasSecret ? 'bg-emerald-500/20 text-emerald-500' : 'bg-primary/20 text-primary'}`}>
                {hasSecret ? <CheckCircle2 className="h-3 w-3" /> : '1'}
              </span>
              OAuth Client Secret File
            </Label>
            {hasSecret && (
              <span className="text-[10px] text-emerald-500 font-medium flex items-center">
                client_secret.json loaded
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="w-full relative h-8 text-xs font-medium bg-background"
              disabled={isUploadingFile}
            >
              {isUploadingFile ? (
                <Loader2 className="h-3.5 w-3.5 mr-2 animate-spin" />
              ) : (
                <Upload className="h-3.5 w-3.5 mr-2" />
              )}
              {hasSecret ? 'Replace client_secret.json' : 'Upload client_secret.json'}
              <input
                type="file"
                accept=".json,application/json,text/plain,*/*"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleFileUpload}
                disabled={isUploadingFile}
              />
            </Button>
          </div>
          {!hasSecret && (
            <p className="text-[10px] text-muted-foreground mt-1">
              Download this from Google Cloud Console (Desktop App type).
            </p>
          )}
        </div>

        {/* Step 2: Authorize */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs font-semibold flex items-center gap-1.5">
              <span className={`flex h-4 w-4 items-center justify-center rounded-full text-[9px] font-bold ${isAuthenticated ? 'bg-emerald-500/20 text-emerald-500' : 'bg-primary/20 text-primary'}`}>
                {isAuthenticated ? <CheckCircle2 className="h-3 w-3" /> : '2'}
              </span>
              Connect Channel
            </Label>
            {isAuthenticated && (
              <span className="text-[10px] text-emerald-500 font-medium flex items-center">
                Ready to upload
              </span>
            )}
          </div>
          <Button
            onClick={handleAuthorize}
            disabled={!hasSecret || isAuthenticated || isAuthorizing}
            className="w-full h-8 text-xs font-medium"
            variant={isAuthenticated ? "secondary" : "default"}
          >
            {isAuthorizing ? (
              <>
                <Loader2 className="h-3.5 w-3.5 mr-2 animate-spin" />
                Waiting for browser approval...
              </>
            ) : isAuthenticated ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5 mr-2 text-emerald-500" />
                Channel Connected
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 mr-2" />
                Login to YouTube
              </>
            )}
          </Button>
          {!isAuthenticated && hasSecret && !isAuthorizing && (
            <p className="text-[10px] text-muted-foreground text-center mt-1">
              This will securely open a new browser tab for you to click "Allow".
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
