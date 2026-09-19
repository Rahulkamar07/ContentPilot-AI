import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("contentpilot_token");
      if (token) {
        config.headers.Authorization = "Bearer ".concat(token);
      }

      const workspaceId = localStorage.getItem("contentpilot_workspace_id");
      if (workspaceId) {
        config.headers["X-Workspace-ID"] = workspaceId;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("contentpilot_token");
    }
    return Promise.reject(error);
  }
);

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: "SUPER_ADMIN" | "USER";
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  plan_tier: string;
}

export interface Source {
  id: string;
  name: string;
  url: string;
  category: string;
  workspace_id: string;
  is_active: boolean;
  last_fetched_at: string | null;
}

export interface Article {
  id: string;
  source_id: string;
  workspace_id: string;
  title: string;
  url: string;
  summary: string | null;
  category: string;
  image_url: string | null;
  published_at: string | null;
}

export interface QueuePost {
  id: string;
  article_id: string;
  workspace_id: string;
  platform: string;
  status: string;
  caption: string;
  image_prompt: string | null;
  image_url: string | null;
  scheduled_for: string | null;
  published_at: string | null;
  external_post_id: string | null;
}
