"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { postsApi, charactersApi, PostData, CharacterData, GenerateCaptionPayload } from "@/lib/api";
import { Sparkles, Plus, Trash2, Send, Clock, MessageSquare, CheckCircle, XCircle, Pencil } from "lucide-react";

const platforms = ["instagram", "tiktok", "twitter", "facebook"];

export default function PostsPage() {
  const [posts, setPosts] = useState<PostData[]>([]);
  const [characters, setCharacters] = useState<CharacterData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showCaptionGen, setShowCaptionGen] = useState(false);
  const [editing, setEditing] = useState<PostData | null>(null);
  const [generating, setGenerating] = useState(false);
  const [genCaption, setGenCaption] = useState("");

  // Form state
  const [selectedChar, setSelectedChar] = useState("");
  const [platform, setPlatform] = useState("instagram");
  const [caption, setCaption] = useState("");
  const [hashtags, setHashtags] = useState("");
  const [mediaIds, setMediaIds] = useState("");

  // Caption generation state
  const [aiTopic, setAiTopic] = useState("");
  const [aiTone, setAiTone] = useState("casual");
  const [aiLanguage, setAiLanguage] = useState("english");

  const load = async () => {
    try {
      const [postsRes, charsRes] = await Promise.all([
        postsApi.list().catch(() => ({ items: [], total: 0 })),
        charactersApi.list().catch(() => ({ items: [], total: 0 })),
      ]);
      setPosts(postsRes.items);
      setCharacters(charsRes.items);
      if (charsRes.items.length > 0) setSelectedChar(charsRes.items[0].id!);
    } catch {
      // API unavailable
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const resetForm = () => {
    setCaption("");
    setHashtags("");
    setMediaIds("");
    setPlatform("instagram");
  };

  const handleCreate = async () => {
    if (!selectedChar) return;
    setGenerating(true);
    try {
      await postsApi.create({
        character_id: selectedChar,
        platform,
        caption,
        hashtags: hashtags ? hashtags.split(",").map((h) => h.trim()) : [],
        media_ids: mediaIds ? mediaIds.split(",").map((m) => m.trim()) : [],
      });
      setShowCreate(false);
      resetForm();
      await load();
    } catch (err) {
      console.error("Create post failed", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleUpdate = async () => {
    if (!editing?.id) return;
    setGenerating(true);
    try {
      await postsApi.update(editing.id, {
        platform,
        caption,
        hashtags: hashtags ? hashtags.split(",").map((h) => h.trim()) : [],
        media_ids: mediaIds ? mediaIds.split(",").map((m) => m.trim()) : [],
      });
      setEditing(null);
      setShowCreate(false);
      resetForm();
      await load();
    } catch (err) {
      console.error("Update post failed", err);
    } finally {
      setGenerating(false);
    }
  };

  const openEdit = (post: PostData) => {
    setEditing(post);
    setSelectedChar(post.character_id);
    setPlatform(post.platform);
    setCaption(post.caption);
    setHashtags((post.hashtags || []).join(", "));
    setMediaIds((post.media_ids || []).join(", "));
    setShowCreate(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this post?")) return;
    try {
      await postsApi.delete(id);
      await load();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleGenerateCaption = async () => {
    if (!selectedChar) return;
    setGenCaption("Generating...");
    try {
      const payload: GenerateCaptionPayload = {
        character_id: selectedChar,
        topic: aiTopic || undefined,
        tone: aiTone,
        language: aiLanguage,
      };
      const res = await postsApi.generateCaption(payload);
      setCaption(res.caption);
      setHashtags(res.hashtags.join(", "));
      setGenCaption("Generated!");
      setTimeout(() => setGenCaption(""), 2000);
      setShowCaptionGen(false);
    } catch (err) {
      console.error("Caption generation failed", err);
      setGenCaption("Failed. Is Ollama running?");
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await api.post(`/posts/${id}/approve`, { approved_by: "admin" });
      await load();
    } catch (err) {
      console.error("Approve failed", err);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await api.post(`/posts/${id}/reject`);
      await load();
    } catch (err) {
      console.error("Reject failed", err);
    }
  };

  const handlePublish = async (id: string) => {
    try {
      await api.post(`/posts/${id}/publish`);
      alert("Post queued for publishing");
      await load();
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Publish failed");
    }
  };

  const statusBadge = (status?: string) => {
    const colors: Record<string, string> = {
      draft: "bg-gray-500/10 text-gray-400",
      approved: "bg-green-500/10 text-green-400",
      rejected: "bg-red-500/10 text-red-400",
      scheduled: "bg-blue-500/10 text-blue-400",
      published: "bg-purple-500/10 text-purple-400",
    };
    return (
      <span className={`text-xs px-2 py-0.5 rounded ${colors[status || "draft"] || colors.draft}`}>
        {status || "draft"}
      </span>
    );
  };

  const charName = (id: string) => characters.find((c) => c.id === id)?.name || id.substring(0, 8);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Posts</h1>
          <p className="text-muted-foreground mt-1">Manage social media posts and captions</p>
        </div>
        <Button onClick={() => { setEditing(null); resetForm(); setShowCreate(!showCreate); }} disabled={characters.length === 0}>
          <Plus className="w-4 h-4 mr-2" /> New Post
        </Button>
      </div>

      {showCreate && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>{editing ? "Edit Post" : "New Post"}</CardTitle>
              <CardDescription>Create a post for your AI influencer</CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={() => { setShowCreate(false); setEditing(null); }}>
              <XCircle className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 grid-cols-1 md:grid-cols-3">
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
                <Label>Platform</Label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                >
                  {platforms.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Media IDs (comma-separated UUIDs)</Label>
                <Input value={mediaIds} onChange={(e) => setMediaIds(e.target.value)} placeholder="uuid1, uuid2" />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Label>Caption</Label>
              <Button variant="outline" size="sm" onClick={() => setShowCaptionGen(!showCaptionGen)} disabled={!selectedChar}>
                <Sparkles className="w-3 h-3 mr-1" /> AI Generate
              </Button>
            </div>
            <Textarea value={caption} onChange={(e) => setCaption(e.target.value)} rows={4} placeholder="Write your post caption..." />

            {showCaptionGen && (
              <Card className="border-dashed">
                <CardContent className="pt-4 space-y-3">
                  <div className="grid gap-3 grid-cols-1 md:grid-cols-3">
                    <div>
                      <Label>Topic</Label>
                      <Input value={aiTopic} onChange={(e) => setAiTopic(e.target.value)} placeholder="weekend vibes, gym, travel..." />
                    </div>
                    <div>
                      <Label>Tone</Label>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={aiTone}
                        onChange={(e) => setAiTone(e.target.value)}
                      >
                        <option value="casual">Casual</option>
                        <option value="professional">Professional</option>
                        <option value="funny">Funny</option>
                        <option value="inspirational">Inspirational</option>
                        <option value="flirty">Flirty</option>
                      </select>
                    </div>
                    <div>
                      <Label>Language</Label>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={aiLanguage}
                        onChange={(e) => setAiLanguage(e.target.value)}
                      >
                        <option value="english">English</option>
                        <option value="polish">Polish</option>
                        <option value="spanish">Spanish</option>
                        <option value="french">French</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex gap-2 items-center">
                    <Button size="sm" onClick={handleGenerateCaption} disabled={genCaption.startsWith("Generating")}>
                      <Sparkles className="w-3 h-3 mr-1" /> Generate Caption
                    </Button>
                    {genCaption && <span className="text-xs text-muted-foreground">{genCaption}</span>}
                  </div>
                </CardContent>
              </Card>
            )}

            <div>
              <Label>Hashtags (comma-separated)</Label>
              <Input value={hashtags} onChange={(e) => setHashtags(e.target.value)} placeholder="#ai #lifestyle #fashion" />
            </div>

            <div className="flex gap-3">
              <Button onClick={editing ? handleUpdate : handleCreate} disabled={generating || !selectedChar || !caption}>
                {generating ? "Saving..." : editing ? "Update Post" : "Create Post"}
              </Button>
              <Button variant="outline" onClick={() => { setShowCreate(false); setEditing(null); }}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><Sparkles className="w-8 h-8 animate-pulse text-primary" /></div>
      ) : posts.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Send className="w-12 h-12 text-muted-foreground mb-3" />
            <p className="text-lg text-muted-foreground">No posts yet</p>
            <p className="text-sm text-muted-foreground mb-4">Create your first social media post</p>
            <Button onClick={() => setShowCreate(true)} disabled={characters.length === 0}>
              <Plus className="w-4 h-4 mr-2" /> Create Post
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {posts.map((post) => (
            <Card key={post.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">{charName(post.character_id)}</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-accent text-accent-foreground">{post.platform}</span>
                      {statusBadge(post.status)}
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{post.caption}</p>
                    {post.hashtags && post.hashtags.length > 0 && (
                      <p className="text-xs text-blue-400">
                        {post.hashtags.map((h) => h.startsWith("#") ? h : `#${h}`).join(" ")}
                      </p>
                    )}
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      {post.publish_date && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {new Date(post.publish_date).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-1 ml-4 flex-shrink-0">
                    {post.status === "draft" && (
                      <>
                        <Button size="sm" variant="outline" onClick={() => post.id && handleApprove(post.id)} title="Approve">
                          <CheckCircle className="w-3 h-3 text-green-400" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => post.id && handleReject(post.id)} title="Reject">
                          <XCircle className="w-3 h-3 text-red-400" />
                        </Button>
                      </>
                    )}
                    {post.status === "approved" && (
                      <Button size="sm" variant="outline" onClick={() => post.id && handlePublish(post.id)} title="Publish now">
                        <Send className="w-3 h-3 text-purple-400" />
                      </Button>
                    )}
                    <Button size="sm" variant="outline" onClick={() => openEdit(post)}>
                      <Pencil className="w-3 h-3" />
                    </Button>
                    <Button size="sm" variant="outline" className="text-destructive" onClick={() => post.id && handleDelete(post.id)}>
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}