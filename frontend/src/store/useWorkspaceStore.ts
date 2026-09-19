"use client";

import { create } from "zustand";

interface WorkspaceState {
  activeWorkspaceId: string | null;
  activeWorkspaceSlug: string | null;
  hydrated: boolean;
  setActiveWorkspace: (id: string, slug: string) => void;
  hydrate: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeWorkspaceId: null,
  activeWorkspaceSlug: null,
  hydrated: false,
  setActiveWorkspace: (id, slug) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("contentpilot_workspace_id", id);
      localStorage.setItem("contentpilot_workspace_slug", slug);
    }
    set({ activeWorkspaceId: id, activeWorkspaceSlug: slug, hydrated: true });
  },
  hydrate: () => {
    if (typeof window === "undefined") {
      return;
    }
    set({
      activeWorkspaceId: localStorage.getItem("contentpilot_workspace_id"),
      activeWorkspaceSlug: localStorage.getItem("contentpilot_workspace_slug"),
      hydrated: true,
    });
  },
}));
