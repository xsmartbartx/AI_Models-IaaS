"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { BarChart3, Image as ImageIcon, LayoutDashboard, Menu, Send, Settings2, Sparkles, Users, Video, X } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/characters", label: "Characters", icon: Users },
  { href: "/images", label: "Images", icon: ImageIcon },
  { href: "/videos", label: "Videos", icon: Video },
  { href: "/posts", label: "Publishing", icon: Send },
];
const secondaryItems = [
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Workspace", icon: Settings2 },
];

export function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const renderItems = (items: typeof navItems) => items.map((item) => {
    const Icon = item.icon;
    const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
    return <Link key={item.href} href={item.href} onClick={() => setMobileOpen(false)} className={cn("flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition", active ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:bg-muted hover:text-foreground")}><Icon className="h-4 w-4" />{item.label}</Link>;
  });
  return <>
    <button onClick={() => setMobileOpen((open) => !open)} className="fixed left-4 top-4 z-50 rounded-xl border bg-card p-2 shadow-sm lg:hidden" aria-label="Toggle navigation">{mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}</button>
    <aside className={cn("fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r bg-card transition-transform duration-200","lg:translate-x-0",mobileOpen ? "translate-x-0" : "-translate-x-full")}>
      <div className="flex items-center gap-3 border-b px-5 py-5"><div className="rounded-xl bg-primary/10 p-2 text-primary"><Sparkles className="h-5 w-5" /></div><div><p className="text-sm font-semibold">OneNexora AI</p><p className="text-xs text-muted-foreground">Content Workspace</p></div></div>
      <div className="flex-1 overflow-y-auto p-4"><p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">Workspace</p><nav className="space-y-1">{renderItems(navItems)}</nav><p className="mb-2 mt-7 px-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">Insights</p><nav className="space-y-1">{renderItems(secondaryItems)}</nav></div>
      <div className="border-t p-4"><div className="rounded-2xl bg-muted/60 p-3"><p className="text-xs font-medium">AI Influencer Factory</p><p className="mt-1 text-[11px] leading-4 text-muted-foreground">FastAPI · Celery · ComfyUI · Ollama</p></div></div>
    </aside>
    {mobileOpen && <button className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={() => setMobileOpen(false)} aria-label="Close navigation" />}
  </>;
}