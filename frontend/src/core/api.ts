import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Attach JWT Bearer token & Tenant Workspace ID
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("contentpilot_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
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

// Response Interceptor: Standard Error Unwrapping
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      // Handle session expiration
    }
    return Promise.reject(error);
  }
);
