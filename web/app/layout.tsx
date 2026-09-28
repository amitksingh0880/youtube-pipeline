import type { Metadata } from "next";
import "./globals.css";
import { Inter } from "next/font/google";
import { cn } from "@/lib/utils";
import { SidebarProvider, SidebarTrigger, SidebarInset } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { Separator } from "@/components/ui/separator";

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: "YouTube Shorts Studio",
  description: "Professional YouTube Shorts Studio Pipeline",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={cn("h-full", "font-sans", inter.variable)} suppressHydrationWarning>
      <body className="h-full bg-background text-foreground antialiased overflow-hidden selection:bg-primary/20 selection:text-primary">
        <SidebarProvider>
          <AppSidebar />
          <SidebarInset className="flex flex-col h-screen overflow-hidden bg-background">
            <header className="flex h-12 shrink-0 items-center justify-between border-b border-border/50 bg-background/95 px-4 backdrop-blur">
              <div className="flex items-center gap-2">
                <SidebarTrigger className="h-7 w-7" />
                <Separator orientation="vertical" className="h-4" />
                <span className="text-xs font-semibold tracking-tight text-muted-foreground">
                  YouTube Shorts Studio Dashboard
                </span>
              </div>
            </header>
            <main className="flex-1 overflow-hidden p-4">
              {children}
            </main>
          </SidebarInset>
        </SidebarProvider>
      </body>
    </html>
  );
}
