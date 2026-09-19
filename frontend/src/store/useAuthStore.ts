"use client";

import { create } from "zustand";

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: "SUPER_ADMIN" | "USER";
}

interface AuthState {
  token: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
  hydrated: boolean;
  setSession: (token: string, user: UserProfile) => void;
  hydrate: () => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,
  hydrated: false,
  setSession: (token, user) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("contentpilot_token", token);
      localStorage.setItem("contentpilot_user", JSON.stringify(user));
    }
    set({ token, user, isAuthenticated: true, hydrated: true });
  },
  hydrate: () => {
    if (typeof window === "undefined") {
      return;
    }
    const token = localStorage.getItem("contentpilot_token");
    const userRaw = localStorage.getItem("contentpilot_user");
    const user = userRaw ? (JSON.parse(userRaw) as UserProfile) : null;
    set({ token, user, isAuthenticated: Boolean(token), hydrated: true });
  },
  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("contentpilot_token");
      localStorage.removeItem("contentpilot_user");
      localStorage.removeItem("contentpilot_workspace_id");
    }
    set({ token: null, user: null, isAuthenticated: false, hydrated: true });
  },
}));
