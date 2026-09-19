"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { api, Workspace } from "@/core/api";
import { useAuthStore } from "@/store/useAuthStore";
import { useWorkspaceStore } from "@/store/useWorkspaceStore";

export default function WorkspacesPage() {
  const router = useRouter();
  const { isAuthenticated, hydrate: hydrateAuth, logout } = useAuthStore();
  const { setActiveWorkspace, hydrate: hydrateWorkspace, activeWorkspaceId } = useWorkspaceStore();

  const [items, setItems] = useState<Workspace[]>([]);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadWorkspaces = async () => {
    try {
      const response = await api.get<Workspace[]>("/workspaces");
      setItems(response.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to load workspaces");
    }
  };

  useEffect(() => {
    hydrateAuth();
    hydrateWorkspace();
  }, [hydrateAuth, hydrateWorkspace]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    void loadWorkspaces();
  }, [isAuthenticated]);

  const onCreate = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.post("/workspaces", { name, slug });
      setName("");
      setSlug("");
      await loadWorkspaces();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to create workspace");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="space-y-3 text-center">
          <p>Please sign in first.</p>
          <Link href="/login" className="text-primary">
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground p-6 max-w-5xl mx-auto space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Workspaces</h1>
        <button
          type="button"
          className="text-sm text-red-400"
          onClick={() => {
            logout();
            router.push("/login");
          }}
        >
          Logout
        </button>
      </header>

      <form onSubmit={onCreate} className="grid grid-cols-1 md:grid-cols-4 gap-3 rounded-xl border border-border p-4 bg-card">
        <input
          className="rounded-lg border border-border bg-background px-3 py-2"
          placeholder="Workspace name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />
        <input
          className="rounded-lg border border-border bg-background px-3 py-2"
          placeholder="slug"
          value={slug}
          onChange={(event) => setSlug(event.target.value)}
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-primary text-primary-foreground px-3 py-2"
        >
          {loading ? "Creating..." : "Create"}
        </button>
        <Link href="/queue" className="rounded-lg border border-border px-3 py-2 text-center">
          Open Queue
        </Link>
      </form>

      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      <div className="grid gap-3">
        {items.map((workspace) => (
          <button
            type="button"
            key={workspace.id}
            onClick={() => setActiveWorkspace(workspace.id, workspace.slug)}
            className={`rounded-xl border p-4 text-left ${
              activeWorkspaceId === workspace.id ? "border-primary" : "border-border"
            }`}
          >
            <h2 className="font-semibold">{workspace.name}</h2>
            <p className="text-sm text-muted-foreground">slug: {workspace.slug}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
