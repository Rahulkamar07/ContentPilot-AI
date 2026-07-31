import React from "react";
import Link from "next/link";
import { Sparkles, ArrowRight, ShieldCheck, Zap, Layers } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen items-center justify-center p-6 bg-gradient-to-b from-background via-card to-background text-foreground relative overflow-hidden">
      {/* Background Accent Blur */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/10 rounded-full blur-3xl pointer-events-none" />

      <main className="max-w-4xl w-full text-center space-y-8 z-10">
        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-card border border-border/60 text-primary text-xs font-semibold uppercase tracking-wider shadow-lg">
          <Sparkles className="w-4 h-4 text-primary" />
          <span>Sprint 1 Foundation Active</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground via-primary to-secondary">
          ContentPilot AI Platform
        </h1>

        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto font-light leading-relaxed">
          Autonomous multi-platform publishing engine powering copyrighted-safe visual synthesis, factual summarization, and human-in-the-loop workflow orchestration.
        </p>

        <div className="flex flex-wrap justify-center gap-4 pt-4">
          <Link
            href="/overview"
            className="inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-white bg-primary hover:bg-primary/90 rounded-xl transition-all shadow-lg hover:shadow-primary/25 space-x-2"
          >
            <span>Launch Dashboard Shell</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-foreground bg-card hover:bg-muted border border-border rounded-xl transition-all"
          >
            OpenAPI Specs (/docs)
          </a>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 text-left">
          <div className="p-6 rounded-2xl bg-card/60 backdrop-blur border border-border/50 hover:border-primary/40 transition-all space-y-3 shadow-xl">
            <ShieldCheck className="w-8 h-8 text-accent" />
            <h3 className="text-lg font-semibold">Clean Architecture</h3>
            <p className="text-sm text-muted-foreground">FastAPI modular monolith adhering strictly to domain repository interfaces.</p>
          </div>

          <div className="p-6 rounded-2xl bg-card/60 backdrop-blur border border-border/50 hover:border-primary/40 transition-all space-y-3 shadow-xl">
            <Zap className="w-8 h-8 text-primary" />
            <h3 className="text-lg font-semibold">Async PostgreSQL & Redis</h3>
            <p className="text-sm text-muted-foreground">SQLAlchemy 2.0 Async ORM with Alembic migrations and Redis connection pooling.</p>
          </div>

          <div className="p-6 rounded-2xl bg-card/60 backdrop-blur border border-border/50 hover:border-primary/40 transition-all space-y-3 shadow-xl">
            <Layers className="w-8 h-8 text-secondary" />
            <h3 className="text-lg font-semibold">Next.js 14 & HSL Theme</h3>
            <p className="text-sm text-muted-foreground">Tailwind CSS glassmorphism, Zustand store, and TanStack Query state cache.</p>
          </div>
        </div>
      </main>

      <footer className="mt-16 text-center text-xs text-muted-foreground z-10">
        ContentPilot AI &copy; 2026. Enterprise SaaS Architecture Baseline.
      </footer>
    </div>
  );
}
