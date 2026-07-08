"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { videosApi, imagesApi, charactersApi, VideoData, CharacterData, ImageData } from "@/lib/api";
import { Sparkles, Plus, Trash2, Video } from "lucide-react";

export default function VideosPage() {
  const [videos, setVideos] = useState<VideoData[]>([]);
  const [characters, setCharacters] = useState<CharacterData[]>([]);
  const [images, setImages] = useState<ImageData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGenerate, setShowGenerate] = useState(false);
  const [selectedChar, setSelectedChar] = useState("");
  const [sourceImage, setSourceImage] = useState("");
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);

  const load = async () => {
    try {
      const [vidsRes, charsRes, imgsRes] = await Promise.all([
        videosApi.list().catch(() => ({ items: [], total: 0 })),
        charactersApi.list().catch(() => ({ items: [], total: 0 })),
        imagesApi.list().catch(() => ({ items: [], total: 0 })),
      ]);
      setVideos(vidsRes.items);
      setCharacters(charsRes.items);
      setImages(imgsRes.items);
      if (charsRes.items.length > 0) setSelectedChar(charsRes.items[0].id!);
    } catch {
      // API unavailable
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filteredImages = images.filter((i) => !selectedChar || i.character_id === selectedChar);

  const handleGenerate = async () => {
    if (!selectedChar) return;
    setGenerating(true);
    try {
      await videosApi.generate({
        character_id: selectedChar,
        prompt: prompt || "cinematic motion, slight smile, wind in hair",
        source_image_id: sourceImage || undefined,
      });
      setShowGenerate(false);
      setTimeout(() => load(), 2000);
    } catch (err) {
      console.error("Generation failed", err);
      setGenerating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this video?")) return;
    try {
      await videosApi.delete(id);
      await load();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Videos</h1>
          <p className="text-muted-foreground mt-1">AI-generated short video clips (5-10s)</p>
        </div>
        <Button onClick={() => setShowGenerate(!showGenerate)} disabled={characters.length === 0}>
          <Plus className="w-4 h-4 mr-2" /> Generate Video
        </Button>
      </div>

      {showGenerate && (
        <Card>
          <CardHeader><CardTitle>Generate New Video</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
              <div>
                <Label>Character</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={selectedChar}
                  onChange={(e) => { setSelectedChar(e.target.value); setSourceImage(""); }}
                >
                  {characters.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Source Image (optional)</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={sourceImage}
                  onChange={(e) => setSourceImage(e.target.value)}
                >
                  <option value="">None (auto-select)</option>
                  {filteredImages.map((img) => (
                    <option key={img.id} value={img.id}>
                      {img.category || "unknown"} - {img.prompt?.substring(0, 40)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <Label>Motion Prompt</Label>
              <Input value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="cinematic motion, slight smile, wind in hair" />
            </div>
            <div className="flex gap-3">
              <Button onClick={handleGenerate} disabled={generating || !selectedChar}>
                {generating ? <><Sparkles className="w-4 h-4 mr-2 animate-pulse" /> Generating...</> : "Generate"}
              </Button>
              <Button variant="outline" onClick={() => setShowGenerate(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><Sparkles className="w-8 h-8 animate-pulse text-primary" /></div>
      ) : videos.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Video className="w-12 h-12 text-muted-foreground mb-3" />
            <p className="text-lg text-muted-foreground">No videos yet</p>
            <p className="text-sm text-muted-foreground mb-4">Generate your first AI video clip</p>
            <Button onClick={() => setShowGenerate(true)} disabled={characters.length === 0}>
              <Plus className="w-4 h-4 mr-2" /> Generate
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {videos.map((vid) => (
            <Card key={vid.id} className="overflow-hidden group">
              <div className="aspect-video bg-muted flex items-center justify-center">
                {vid.file_path ? (
                  <video src={vid.file_path} controls className="w-full h-full object-cover" />
                ) : (
                  <Video className="w-8 h-8 text-muted-foreground" />
                )}
              </div>
              <CardContent className="p-3">
                <p className="text-xs text-muted-foreground truncate">{vid.prompt || "Generated video"}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs px-2 py-0.5 rounded bg-accent text-accent-foreground">
                    {vid.status || "processing"}
                  </span>
                  <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive" onClick={() => vid.id && handleDelete(vid.id)}>
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}