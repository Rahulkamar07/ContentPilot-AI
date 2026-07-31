import { create } from "zustand";

interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  role: "SUPER_ADMIN" | "USER";
}

interface AuthState {
  token: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
  setSession: (token: string, user: UserProfile) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,
  setSession: (token, user) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("contentpilot_token", token);
    }
    set({ token, user, isAuthenticated: true });
  },
  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("contentpilot_token");
      localStorage.removeItem("contentpilot_workspace_id");
    }
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
