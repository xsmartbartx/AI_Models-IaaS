import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// ---- Types ----

export interface CharacterData {
  id?: string;
  name: string;
  age: number;
  nationality: string;
  hair: string;
  eyes: string;
  height: string;
  style: string;
  bio?: string;
  appearance?: Record<string, unknown>;
  hobbies?: string[];
  status?: string;
}

export interface ImageData {
  id?: string;
  character_id: string;
  file_path?: string;
  prompt: string;
  negative_prompt?: string;
  category?: string;
  status?: string;
  created_at?: string;
}

export interface VideoData {
  id?: string;
  character_id: string;
  file_path?: string;
  prompt: string;
  source_image_id?: string;
  status?: string;
  created_at?: string;
}

export interface PostData {
  id?: string;
  character_id: string;
  platform: string;
  caption: string;
  hashtags?: string[];
  media_ids?: string[];
  publish_date?: string;
  status?: string;
  created_at?: string;
}

export interface GenerateCaptionPayload {
  character_id: string;
  topic?: string;
  tone?: string;
  language?: string;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
}

// ---- Characters API ----

export const charactersApi = {
  list: () => api.get<ListResponse<CharacterData>>("/characters/").then((r) => r.data),
  get: (id: string) => api.get<CharacterData>(`/characters/${id}`).then((r) => r.data),
  create: (data: CharacterData) => api.post<CharacterData>("/characters/", data).then((r) => r.data),
  update: (id: string, data: Partial<CharacterData>) =>
    api.patch<CharacterData>(`/characters/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/characters/${id}`),
  activate: (id: string) => api.post<CharacterData>(`/characters/${id}/activate`).then((r) => r.data),
};

// ---- Images API ----

export const imagesApi = {
  list: (characterId?: string) =>
    api
      .get<ListResponse<ImageData>>("/images/", { params: characterId ? { character_id: characterId } : {} })
      .then((r) => r.data),
  get: (id: string) => api.get<ImageData>(`/images/${id}`).then((r) => r.data),
  generate: (data: { character_id: string; prompt?: string; negative_prompt?: string; category?: string }) =>
    api.post<{ status: string; task_id: string }>("/images/generate", data).then((r) => r.data),
  delete: (id: string) => api.delete(`/images/${id}`),
};

// ---- Videos API ----

export const videosApi = {
  list: (characterId?: string) =>
    api
      .get<ListResponse<VideoData>>("/videos/", { params: characterId ? { character_id: characterId } : {} })
      .then((r) => r.data),
  get: (id: string) => api.get<VideoData>(`/videos/${id}`).then((r) => r.data),
  generate: (data: { character_id: string; prompt?: string; source_image_id?: string }) =>
    api.post<{ status: string; task_id: string }>("/videos/generate", data).then((r) => r.data),
  delete: (id: string) => api.delete(`/videos/${id}`),
};

// ---- Posts API ----

export const postsApi = {
  list: (characterId?: string) =>
    api
      .get<ListResponse<PostData>>("/posts/", { params: characterId ? { character_id: characterId } : {} })
      .then((r) => r.data),
  get: (id: string) => api.get<PostData>(`/posts/${id}`).then((r) => r.data),
  create: (data: PostData) => api.post<PostData>("/posts/", data).then((r) => r.data),
  update: (id: string, data: Partial<PostData>) =>
    api.patch<PostData>(`/posts/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/posts/${id}`),
  generateCaption: (data: GenerateCaptionPayload) =>
    api.post<{ caption: string; hashtags: string[] }>("/posts/generate-caption", data).then((r) => r.data),
  approve: (id: string, data?: { approved_by?: string }) =>
    api.post<PostData>(`/posts/${id}/approve`, data || { approved_by: "admin" }).then((r) => r.data),
  reject: (id: string) =>
    api.post<PostData>(`/posts/${id}/reject`).then((r) => r.data),
  publish: (id: string) =>
    api.post<PostData>(`/posts/${id}/publish`).then((r) => r.data),
  schedule: (id: string, data: { publish_date: string }) =>
    api.post<PostData>(`/posts/${id}/schedule`, data).then((r) => r.data),
};

export default api;