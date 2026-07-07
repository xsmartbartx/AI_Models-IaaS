"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { imagesApi, charactersApi, ImageData, CharacterData } from "@/lib/api";
import { Sparkles, Plus, Trash2, ImageIcon } from "lucide-react";

const categories = ["lifestyle", "gym", "travel", "fashion", "portrait", "other"];
const promptTemplates: Record<string, string> = {
  lifestyle: "walking in old town, summer evening, DSLR photo, realistic skin",
  gym: "fitness club, workout session, sportswear, natural lighting",
  travel: "airport terminal, vacation outfit, cinematic photo",
  fashion: "street fashion, urban background, editorial photography",
  portrait: "professional portrait, studio lighting, bokeh background",
};

export default function ImagesPage() {
  const [images, setImages] = useState<ImageData[]>([]);
  const [characters, setCharacters] = useState<CharacterData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGenerate, setShowGenerate] = useState(false);
  const [selectedChar, setSelectedChar] = useState("");
  const [prompt, setPrompt] = useState("");
  const [negativePrompt, setNegativePrompt] = useState("");
  const [category, setCategory] = useState("lifestyle");
  const [generating, setGenerating] = useState(false);

  const load = async () => {
    try {
      const [imgsRes, charsRes] = await Promise.all([
        imagesApi.list().catch(() => ({ items: [], total: 0 })),
        charactersApi.list().catch(() => ({ items: [], total: 0 })),
      ]);
      setImages(imgsRes.items);
      setCharacters(charsRes.items);
      if (charsRes.items.length > 0) setSelectedChar(charsRes.items[0].id!);
    } catch {
      // API unavailable
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleGenerate = async () => {
    if (!selectedChar) return;
    setGenerating(true);
    try {
      await imagesApi.generate({
        character_id: selectedChar,
        prompt: prompt || promptTemplates[category],
        negative_prompt: negativePrompt || "blurry, deformed, bad anatomy, ugly",
        category,
      });
      setShowGenerate(false);
      setTimeout(() => load(), 2000);
    } catch (err) {
      console.error("Generation failed", err);
      setGenerating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this image?")) return;
    try {
      await imagesApi.delete(id);
      await load();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Images</h1>
          <p className="text-muted-foreground mt-1">AI-generated photo sessions</p>
        </div>
        <Button onClick={() => setShowGenerate(!showGenerate)} disabled={characters.length === 0}>
          <Plus className="w-4 h-4 mr-2" /> Generate Image
        </Button>
      </div>

      {showGenerate && (
        <Card>
          <CardHeader><CardTitle>Generate New Image</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
              <div>
                <Label>Character</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={selectedChar}
                  onChange={(e) => setSelectedChar(e.target.value)}
                >
                  {characters.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Category</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={category}
                  onChange={(e) => { setCategory(e.target.value); setPrompt(promptTemplates[e.target.value] || ""); }}
                >
                  {categories.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <Label>Prompt</Label>
              <Input value={prompt || promptTemplates[category]} onChange={(e) => setPrompt(e.target.value)} />
            </div>
            <div>
              <Label>Negative Prompt</Label>
              <Input value={negativePrompt} onChange={(e) => setNegativePrompt(e.target.value)} placeholder="blurry, deformed, bad anatomy" />
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
      ) : images.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <ImageIcon className="w-12 h-12 text-muted-foreground mb-3" />
            <p className="text-lg text-muted-foreground">No images yet</p>
            <p className="text-sm text-muted-foreground mb-4">Generate your first AI photo</p>
            <Button onClick={() => setShowGenerate(true)} disabled={characters.length === 0}>
              <Plus className="w-4 h-4 mr-2" /> Generate
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {images.map((img) => (
            <Card key={img.id} className="overflow-hidden group">
              <div className="aspect-square bg-muted flex items-center justify-center">
                {img.file_path ? (
                  <img src={img.file_path} alt={img.prompt} className="w-full h-full object-cover" />
                ) : (
                  <ImageIcon className="w-8 h-8 text-muted-foreground" />
                )}
              </div>
              <CardContent className="p-3">
                <p className="text-xs text-muted-foreground truncate">{img.prompt}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs px-2 py-0.5 rounded bg-accent text-accent-foreground">{img.category || "unknown"}</span>
                  <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive" onClick={() => img.id && handleDelete(img.id)}>
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