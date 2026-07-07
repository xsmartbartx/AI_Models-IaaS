"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { charactersApi, CharacterData } from "@/lib/api";
import { Plus, Pencil, Trash2, Sparkles, X } from "lucide-react";

const defaultForm: CharacterData = {
  name: "",
  age: 24,
  nationality: "Polish",
  hair: "brown",
  eyes: "green",
  height: "170",
  style: "fashion",
  bio: "",
  hobbies: [],
};

export default function CharactersPage() {
  const [characters, setCharacters] = useState<CharacterData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<CharacterData | null>(null);
  const [form, setForm] = useState<CharacterData>({ ...defaultForm });
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      const res = await charactersApi.list();
      setCharacters(res.items);
    } catch {
      // API unavailable
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openNew = () => {
    setEditing(null);
    setForm({ ...defaultForm });
    setShowForm(true);
  };

  const openEdit = (char: CharacterData) => {
    setEditing(char);
    setForm({ ...defaultForm, ...char });
    setShowForm(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editing?.id) {
        await charactersApi.update(editing.id, form);
      } else {
        await charactersApi.create(form);
      }
      setShowForm(false);
      await load();
    } catch (err) {
      console.error("Save failed", err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this character?")) return;
    try {
      await charactersApi.delete(id);
      await load();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleActivate = async (id: string) => {
    try {
      await charactersApi.activate(id);
      await load();
    } catch (err) {
      console.error("Activate failed", err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Characters</h1>
          <p className="text-muted-foreground mt-1">Manage your AI influencer personas</p>
        </div>
        <Button onClick={openNew}>
          <Plus className="w-4 h-4 mr-2" />
          New Character
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>{editing ? "Edit Character" : "New Character"}</CardTitle>
              <CardDescription>Define your AI influencer persona</CardDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setShowForm(false)}>
              <X className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
              <div>
                <Label>Name *</Label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Sophia" />
              </div>
              <div>
                <Label>Age *</Label>
                <Input type="number" value={form.age} onChange={(e) => setForm({ ...form, age: Number(e.target.value) })} />
              </div>
              <div>
                <Label>Nationality *</Label>
                <Input value={form.nationality} onChange={(e) => setForm({ ...form, nationality: e.target.value })} />
              </div>
              <div>
                <Label>Hair</Label>
                <Input value={form.hair} onChange={(e) => setForm({ ...form, hair: e.target.value })} />
              </div>
              <div>
                <Label>Eyes</Label>
                <Input value={form.eyes} onChange={(e) => setForm({ ...form, eyes: e.target.value })} />
              </div>
              <div>
                <Label>Height</Label>
                <Input value={form.height} onChange={(e) => setForm({ ...form, height: e.target.value })} />
              </div>
              <div>
                <Label>Style *</Label>
                <Input value={form.style} onChange={(e) => setForm({ ...form, style: e.target.value })} placeholder="fashion, fitness, luxury" />
              </div>
              <div>
                <Label>Bio</Label>
                <Textarea value={form.bio || ""} onChange={(e) => setForm({ ...form, bio: e.target.value })} placeholder="Short biography..." />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <Button onClick={handleSave} disabled={saving || !form.name}>
                {saving ? "Saving..." : "Save Character"}
              </Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <Sparkles className="w-8 h-8 animate-pulse text-primary" />
        </div>
      ) : characters.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Sparkles className="w-12 h-12 text-muted-foreground mb-3" />
            <p className="text-muted-foreground text-lg">No characters yet</p>
            <p className="text-sm text-muted-foreground mb-4">Create your first AI influencer to begin</p>
            <Button onClick={openNew}>
              <Plus className="w-4 h-4 mr-2" />
              Create Character
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {characters.map((char) => (
            <Card key={char.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-lg font-bold text-primary">
                      {char.name[0]}
                    </div>
                    <div>
                      <p className="font-semibold">{char.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {char.age} &bull; {char.nationality}
                      </p>
                      <p className="text-xs text-muted-foreground">{char.style}</p>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button size="sm" variant="outline" onClick={() => openEdit(char)}>
                    <Pencil className="w-3 h-3 mr-1" /> Edit
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => char.id && handleActivate(char.id)}>
                    <Sparkles className="w-3 h-3 mr-1" /> Activate
                  </Button>
                  <Button size="sm" variant="outline" className="text-destructive" onClick={() => char.id && handleDelete(char.id)}>
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