// OneNexora customer dashboard
"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Activity, ArrowRight, BarChart3, Bot, CalendarClock, CheckCircle2, Clock3, Image as ImageIcon, Layers3, Send, Sparkles, Users, Video, WandSparkles, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { charactersApi, imagesApi, postsApi, videosApi, CharacterData, ImageData, PostData, VideoData } from "@/lib/api";

type DashboardState = { characters: CharacterData[]; images: ImageData[]; videos: VideoData[]; posts: PostData[] };
const emptyState: DashboardState = { characters: [], images: [], videos: [], posts: [] };

function statusLabel(status?: string) { return (status || "unknown").replace(/_/g, " "); }
function statusTone(status?: string) {
  if (["published","generated","active","completed","approved"].includes(status || "")) return "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300";
  if (["processing","pending","scheduled"].includes(status || "")) return "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300";
  if (["failed","rejected"].includes(status || "")) return "border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300";
  return "border-border bg-muted text-muted-foreground";
}

function StatCard({ label, value, detail, icon: Icon }: { label: string; value: number; detail: string; icon: typeof Users }) {
  return <Card><CardContent className="p-5"><div className="flex items-start justify-between"><div><p className="text-sm text-muted-foreground">{label}</p><p className="mt-2 text-3xl font-semibold">{value}</p><p className="mt-1 text-xs text-muted-foreground">{detail}</p></div><div className="rounded-xl bg-primary/10 p-2.5 text-primary"><Icon className="h-5 w-5" /></div></div></CardContent></Card>;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardState>(emptyState);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [characters, images, videos, posts] = await Promise.all([charactersApi.list(), imagesApi.list(), videosApi.list(), postsApi.list()]);
      setData({ characters: characters.items, images: images.items, videos: videos.items, posts: posts.items });
    } catch (error) {
      console.error("Dashboard load failed", error);
      setData(emptyState);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const metrics = useMemo(() => ({
    generatedImages: data.images.filter(x => x.status === "generated").length,
    generatedVideos: data.videos.filter(x => x.status === "generated").length,
    activeCharacters: data.characters.filter(x => x.status === "active").length,
    queued: data.images.filter(x => x.status === "processing").length + data.videos.filter(x => x.status === "processing").length,
    drafts: data.posts.filter(x => x.status === "draft").length,
    scheduled: data.posts.filter(x => x.status === "scheduled").length,
    published: data.posts.filter(x => x.status === "published").length,
    failed: data.images.filter(x => x.status === "failed").length + data.videos.filter(x => x.status === "failed").length + data.posts.filter(x => x.status === "failed").length,
  }), [data]);

  const recentPosts = data.posts.slice(0, 5);
  const recentImages = data.images.slice(0, 4);
  const recentVideos = data.videos.slice(0, 3);

  return <div className="space-y-8 pb-10">
    <section className="relative overflow-hidden rounded-3xl border border-border bg-card p-6 shadow-sm md:p-8">
      <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-2xl">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium text-primary"><Sparkles className="h-3.5 w-3.5" />OneNexora AI Workspace</div>
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">Your AI content command center</h1>
          <p className="mt-3 text-sm leading-6 text-muted-foreground md:text-base">Generate characters, images and videos, turn them into posts, and see the production pulse from one place.</p>
        </div>
        <div className="flex flex-wrap gap-3"><Button asChild><Link href="/images"><WandSparkles className="mr-2 h-4 w-4" />Create image</Link></Button><Button variant="outline" asChild><Link href="/posts"><Send className="mr-2 h-4 w-4" />New post</Link></Button></div>
      </div>
    </section>

    {loading ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{[1,2,3,4].map(i => <Card key={i}><CardContent className="h-32 animate-pulse p-5" /></Card>)}</div> : <>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Characters" value={data.characters.length} detail={String(metrics.activeCharacters) + " active"} icon={Users} />
        <StatCard label="Images" value={metrics.generatedImages} detail={String(data.images.length) + " total assets"} icon={ImageIcon} />
        <StatCard label="Videos" value={metrics.generatedVideos} detail={String(data.videos.length) + " total assets"} icon={Video} />
        <StatCard label="Posts" value={data.posts.length} detail={String(metrics.published) + " published"} icon={Send} />
      </div>

      <section className="grid gap-4 lg:grid-cols-[1.6fr_1fr]">
        <Card><CardHeader className="flex flex-row items-center justify-between"><div><CardTitle>Production pulse</CardTitle><p className="mt-1 text-sm text-muted-foreground">What needs attention right now.</p></div><Activity className="h-5 w-5 text-primary" /></CardHeader><CardContent className="grid gap-3 sm:grid-cols-2">
          {[{label:"In queue",value:metrics.queued,icon:Clock3,tone:"text-amber-600"},{label:"Draft posts",value:metrics.drafts,icon:Layers3,tone:"text-slate-600"},{label:"Scheduled",value:metrics.scheduled,icon:CalendarClock,tone:"text-blue-600"},{label:"Failed jobs",value:metrics.failed,icon:XCircle,tone:"text-red-600"}].map(item => <div key={item.label} className="flex items-center justify-between rounded-2xl border border-border p-4"><div className="flex items-center gap-3"><item.icon className={"h-4 w-4 " + item.tone} /><span className="text-sm font-medium">{item.label}</span></div><span className="text-xl font-semibold">{item.value}</span></div>)}
        </CardContent></Card>

        <Card><CardHeader><CardTitle>Workspace health</CardTitle><p className="mt-1 text-sm text-muted-foreground">Current content mix.</p></CardHeader><CardContent className="space-y-4">
          {[["Characters ready",metrics.activeCharacters,data.characters.length],["Images generated",metrics.generatedImages,data.images.length],["Videos generated",metrics.generatedVideos,data.videos.length],["Posts published",metrics.published,data.posts.length]].map(([label,value,total]) => { const ratio = total ? Math.round(Number(value)/Number(total)*100) : 0; return <div key={String(label)} className="space-y-2"><div className="flex justify-between text-xs"><span className="text-muted-foreground">{String(label)}</span><span className="font-medium">{value}/{total}</span></div><div className="h-2 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{width:String(ratio)+"%"}} /></div></div>; })}
        </CardContent></Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
        <Card><CardHeader className="flex flex-row items-center justify-between"><div><CardTitle>Recent posts</CardTitle><p className="mt-1 text-sm text-muted-foreground">Latest publishing workflow activity.</p></div><Button variant="ghost" size="sm" asChild><Link href="/posts">View all <ArrowRight className="ml-1 h-4 w-4" /></Link></Button></CardHeader><CardContent>
          {recentPosts.length === 0 ? <div className="rounded-2xl border border-dashed p-8 text-center"><Send className="mx-auto h-8 w-8 text-muted-foreground" /><p className="mt-3 font-medium">No posts yet</p><Button className="mt-4" asChild><Link href="/posts">Create post</Link></Button></div> : <div className="space-y-2">{recentPosts.map(post => <div key={post.id} className="flex items-center justify-between gap-4 rounded-2xl border p-4"><div className="min-w-0"><p className="truncate font-medium">{post.caption || "Untitled post"}</p><p className="mt-1 text-xs text-muted-foreground">{post.platform}{post.publish_date ? " • " + new Date(post.publish_date).toLocaleString() : ""}</p></div><span className={"shrink-0 rounded-full border px-2.5 py-1 text-xs capitalize " + statusTone(post.status)}>{statusLabel(post.status)}</span></div>)}</div>}
        </CardContent></Card>

        <Card><CardHeader><CardTitle>Quick actions</CardTitle><p className="mt-1 text-sm text-muted-foreground">Common production workflows.</p></CardHeader><CardContent className="space-y-3">
          {[{href:"/characters",icon:Bot,title:"Manage characters",text:"Build or activate influencer personas."},{href:"/images",icon:ImageIcon,title:"Generate images",text:"Run a new ComfyUI job."},{href:"/videos",icon:Video,title:"Generate video",text:"Create motion from an image."},{href:"/posts",icon:BarChart3,title:"Schedule content",text:"Prepare and publish a post."}].map(item => <Link key={item.href} href={item.href} className="group flex items-center gap-4 rounded-2xl border p-4 transition hover:border-primary/40 hover:bg-primary/5"><div className="rounded-xl bg-muted p-2.5 group-hover:bg-primary/10 group-hover:text-primary"><item.icon className="h-4 w-4" /></div><div className="min-w-0 flex-1"><p className="font-medium">{item.title}</p><p className="text-xs text-muted-foreground">{item.text}</p></div><ArrowRight className="h-4 w-4 text-muted-foreground" /></Link>)}
        </CardContent></Card>
      </section>

      <section><h2 className="text-xl font-semibold">Latest assets</h2><p className="mt-1 text-sm text-muted-foreground">Most recent generated media.</p><div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card><CardHeader className="flex flex-row items-center justify-between"><CardTitle>Images</CardTitle><Button variant="ghost" size="sm" asChild><Link href="/images">Open <ArrowRight className="ml-1 h-4 w-4" /></Link></Button></CardHeader><CardContent>{recentImages.length === 0 ? <div className="py-8 text-center text-sm text-muted-foreground">No generated images.</div> : <div className="grid grid-cols-2 gap-3 md:grid-cols-4">{recentImages.map(image => <div key={image.id} className="rounded-2xl border p-3"><div className="flex h-20 items-center justify-center rounded-xl bg-muted"><ImageIcon className="h-7 w-7 text-muted-foreground" /></div><p className="mt-2 truncate text-xs font-medium">{image.category || "general"}</p><span className={"mt-1 inline-flex rounded-full border px-2 py-0.5 text-[10px] capitalize " + statusTone(image.status)}>{statusLabel(image.status)}</span></div>)}</div>}</CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between"><CardTitle>Videos</CardTitle><Button variant="ghost" size="sm" asChild><Link href="/videos">Open <ArrowRight className="ml-1 h-4 w-4" /></Link></Button></CardHeader><CardContent>{recentVideos.length === 0 ? <div className="py-8 text-center text-sm text-muted-foreground">No generated videos.</div> : <div className="space-y-3">{recentVideos.map(video => <div key={video.id} className="flex items-center gap-3 rounded-2xl border p-3"><div className="flex h-12 w-16 items-center justify-center rounded-xl bg-muted"><Video className="h-5 w-5 text-muted-foreground" /></div><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium">{video.prompt || "Untitled video"}</p><p className="text-xs text-muted-foreground">{video.duration ? String(video.duration)+"s" : "Generated asset"}</p></div>{video.status==="generated" ? <CheckCircle2 className="h-4 w-4 text-emerald-600" /> : <Clock3 className="h-4 w-4 text-amber-600" />}</div>)}</div>}</CardContent></Card>
      </div></section>

      <section className="rounded-3xl border bg-muted/30 p-5"><div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"><div><p className="font-medium">SaaS hardening still required</p><p className="text-sm text-muted-foreground">Before public multi-customer rollout, add OneNexora auth, tenant isolation, usage metering, billing and audit logs.</p></div><span className="rounded-full border bg-background px-3 py-1.5 text-xs font-medium text-primary">Phase 2</span></div></section>
    </>}
  </div>;
}
