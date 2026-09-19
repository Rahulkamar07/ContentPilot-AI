"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { api, Article, QueuePost, Source } from "@/core/api";
import { useAuthStore } from "@/store/useAuthStore";
import { useWorkspaceStore } from "@/store/useWorkspaceStore";

export default function QueuePage() {
  const { isAuthenticated, hydrate: hydrateAuth } = useAuthStore();
  const { activeWorkspaceId, hydrate: hydrateWorkspace } = useWorkspaceStore();

  const [sources, setSources] = useState<Source[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [posts, setPosts] = useState<QueuePost[]>([]);
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [category, setCategory] = useState("general");
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!activeWorkspaceId) return;
    try {
      const [sourcesRes, articlesRes, postsRes] = await Promise.all([
        api.get<Source[]>("/sources"),
        api.get<Article[]>("/articles"),
        api.get<QueuePost[]>("/queue/posts"),
      ]);
      setSources(sourcesRes.data);
      setArticles(articlesRes.data);
      setPosts(postsRes.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to load queue data");
    }
  }, [activeWorkspaceId]);

  useEffect(() => {
    hydrateAuth();
    hydrateWorkspace();
  }, [hydrateAuth, hydrateWorkspace]);

  useEffect(() => {
    if (!isAuthenticated || !activeWorkspaceId) {
      return;
    }
    void loadData();
  }, [isAuthenticated, activeWorkspaceId, loadData]);

  const createSource = async (event: FormEvent) => {
    event.preventDefault();
    if (!activeWorkspaceId) return;

    setError(null);
    try {
      await api.post("/sources", { name, url, category });
      setName("");
      setUrl("");
      await loadData();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to create source");
    }
  };

  const runIngestion = async (sourceId: string) => {
    try {
      await api.post(`/sources/${sourceId}/ingest`);
      await loadData();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to start ingestion");
    }
  };

  const generatePost = async (articleId: string) => {
    try {
      await api.post(`/articles/${articleId}/ai-process`, { platform: "instagram" });
      await loadData();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to process article");
    }
  };

  const approvePost = async (postId: string) => {
    try {
      await api.post(`/queue/posts/${postId}/approve`, {});
      await loadData();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to approve post");
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <Link href="/login" className="text-primary">
          Please sign in first
        </Link>
      </div>
    );
  }

  if (!activeWorkspaceId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <Link href="/workspaces" className="text-primary">
          Select a workspace first
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground p-6 max-w-7xl mx-auto space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Review Queue Board</h1>
        <Link href="/workspaces" className="text-sm text-primary">
          ← Workspaces
        </Link>
      </header>

      <form onSubmit={createSource} className="grid grid-cols-1 md:grid-cols-4 gap-3 rounded-xl border border-border p-4 bg-card">
        <input
          className="rounded-lg border border-border bg-background px-3 py-2"
          placeholder="Source name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />
        <input
          className="rounded-lg border border-border bg-background px-3 py-2"
          placeholder="https://feed-url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          required
        />
        <input
          className="rounded-lg border border-border bg-background px-3 py-2"
          placeholder="category"
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          required
        />
        <button type="submit" className="rounded-lg bg-primary text-primary-foreground px-3 py-2">
          Add source
        </button>
      </form>

      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <section className="rounded-xl border border-border bg-card p-4 space-y-3">
          <h2 className="font-semibold">Sources</h2>
          {sources.map((source) => (
            <div key={source.id} className="rounded-lg border border-border p-3 space-y-2">
              <p className="font-medium">{source.name}</p>
              <p className="text-xs text-muted-foreground truncate">{source.url}</p>
              <button
                type="button"
                className="text-xs rounded bg-secondary px-2 py-1"
                onClick={() => runIngestion(source.id)}
              >
                Run ingestion
              </button>
            </div>
          ))}
        </section>

        <section className="rounded-xl border border-border bg-card p-4 space-y-3">
          <h2 className="font-semibold">Articles</h2>
          {articles.map((article) => (
            <div key={article.id} className="rounded-lg border border-border p-3 space-y-2">
              <p className="font-medium text-sm">{article.title}</p>
              <button
                type="button"
                className="text-xs rounded bg-secondary px-2 py-1"
                onClick={() => generatePost(article.id)}
              >
                Generate post
              </button>
            </div>
          ))}
        </section>

        <section className="rounded-xl border border-border bg-card p-4 space-y-3">
          <h2 className="font-semibold">Queue</h2>
          {posts.map((post) => (
            <div key={post.id} className="rounded-lg border border-border p-3 space-y-2">
              <p className="text-xs uppercase text-muted-foreground">{post.status}</p>
              <p className="text-sm whitespace-pre-line">{post.caption}</p>
              {post.status !== "PUBLISHED" ? (
                <button
                  type="button"
                  className="text-xs rounded bg-primary text-primary-foreground px-2 py-1"
                  onClick={() => approvePost(post.id)}
                >
                  Approve & publish
                </button>
              ) : (
                <p className="text-xs text-accent">Published: {post.external_post_id}</p>
              )}
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}
