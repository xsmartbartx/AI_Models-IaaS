"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { charactersApi, imagesApi, videosApi, postsApi, CharacterData } from "@/lib/api";
import { Users, Image as ImageIcon, Video, Send, Sparkles } from "lucide-react";

export default function DashboardPage() {
  const [characters, setCharacters] = useState<CharacterData[]>([]);
  const [stats, setStats] = useState({ images: 0, videos: 0, posts: 0, characters: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [charsRes, imgsRes, vidsRes, postsRes] = await Promise.all([
          charactersApi.list().catch(() => ({ items: [], total: 0 })),
          imagesApi.list().catch(() => ({ items: [], total: 0 })),
          videosApi.list().catch(() => ({ items: [], total: 0 })),
          postsApi.list().catch(() => ({ items: [], total: 0 })),
        ]);
        setCharacters(charsRes.items);
        setStats({
          characters: charsRes.total,
          images: imgsRes.total,
          videos: vidsRes.total,
          posts: postsRes.total,
        });
      } catch {
        // API not available yet
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const statCards = [
    { label: "Characters", value: stats.characters, icon: Users, color: "text-purple-500" },
    { label: "Images", value: stats.images, icon: ImageIcon, color: "text-blue-500" },
    { label: "Videos", value: stats.videos, icon: Video, color: "text-pink-500" },
    { label: "Posts", value: stats.posts, icon: Send, color: "text-green-500" },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Overview of your AI influencer content factory</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Sparkles className="w-8 h-8 animate-pulse text-primary" />
        </div>
      ) : (
        <>
          <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
            {statCards.map((stat) => (
              <Card key={stat.label}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
                  <stat.icon className={`w-4 h-4 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div>
            <h2 className="text-xl font-bold mb-4">Active Characters</h2>
            {characters.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Users className="w-12 h-12 text-muted-foreground mb-3" />
                  <p className="text-muted-foreground">No characters created yet</p>
                  <p className="text-sm text-muted-foreground">Create your first AI influencer to get started</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                {characters.map((char) => (
                  <Card key={char.id}>
                    <CardContent className="pt-6">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                          <Users className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-semibold">{char.name}</p>
                          <p className="text-xs text-muted-foreground">{char.nationality} &bull; {char.style}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}