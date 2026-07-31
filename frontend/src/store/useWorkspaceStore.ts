import { create } from "zustand";

interface WorkspaceState {
  activeWorkspaceId: string | null;
  activeWorkspaceSlug: string | null;
  setActiveWorkspace: (id: string, slug: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeWorkspaceId: null,
  activeWorkspaceSlug: null,
  setActiveWorkspace: (id, slug) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("contentpilot_workspace_id", id);
    }
    set({ activeWorkspaceId: id, activeWorkspaceSlug: slug });
  },
}));
