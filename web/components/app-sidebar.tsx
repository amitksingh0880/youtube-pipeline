"use client";

import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Film,
  Activity,
  Layers,
  LayoutDashboard,
  Database,
  PlayCircle,
  Cpu,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const navItems = [
  { id: "create", href: "/", label: "Studio Generator", icon: LayoutDashboard },
  { id: "ssemble_guide", href: "/architecture", label: "Architecture", icon: Layers },
  { id: "niches", href: "/niches", label: "Intelligence", icon: Database },
  { id: "diagnostics", href: "/diagnostics", label: "Diagnostics", icon: Activity },
  { id: "history", href: "/history", label: "Library", icon: Film },
];

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname();

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              render={<Link href="/" />}
            >
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                <PlayCircle className="size-4" />
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">Shorts Studio</span>
                <span className="truncate text-xs text-muted-foreground">Horizon SaaS Engine</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Studio Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <SidebarMenuItem key={item.id}>
                    <SidebarMenuButton
                      isActive={isActive}
                      tooltip={item.label}
                      render={<Link href={item.href} />}
                    >
                      <item.icon />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg">
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-500">
                <Cpu className="size-4" />
              </div>
              <div className="grid flex-1 text-left text-xs leading-tight">
                <span className="truncate font-medium">Local FFmpeg</span>
                <span className="truncate text-[10px] text-muted-foreground">0 API Credits</span>
              </div>
              <SidebarMenuBadge className="text-emerald-500">Active</SidebarMenuBadge>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
