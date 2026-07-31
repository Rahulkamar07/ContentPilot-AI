import React from "react";
import Link from "next/link";
import { Activity, Server, Database, Cpu, CheckCircle2 } from "lucide-react";

export default function OverviewPage() {
  return (
    <div className="min-h-screen bg-background p-8 space-y-8">
      <header className="flex justify-between items-center border-b border-border/50 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Infrastructure Overview</h1>
          <p className="text-sm text-muted-foreground">Sprint 1 Foundation Status & Core Connectivity</p>
        </div>
        <Link
          href="/"
          className="px-4 py-2 text-xs font-medium bg-card hover:bg-muted border border-border rounded-lg transition-all"
        >
          &larr; Back to Home
        </Link>
      </header>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="p-6 rounded-2xl bg-card border border-border space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground font-medium uppercase">API Service</span>
            <Server className="w-5 h-5 text-primary" />
          </div>
          <p className="text-2xl font-bold text-foreground">FastAPI 0.111</p>
          <div className="flex items-center text-xs text-accent space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Port 8000 Ready</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-card border border-border space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground font-medium uppercase">Database Engine</span>
            <Database className="w-5 h-5 text-primary" />
          </div>
          <p className="text-2xl font-bold text-foreground">PostgreSQL 16</p>
          <div className="flex items-center text-xs text-accent space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>pgvector Enabled</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-card border border-border space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground font-medium uppercase">Cache Broker</span>
            <Activity className="w-5 h-5 text-secondary" />
          </div>
          <p className="text-2xl font-bold text-foreground">Redis 7</p>
          <div className="flex items-center text-xs text-accent space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Connection Pool OK</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-card border border-border space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground font-medium uppercase">Task Workers</span>
            <Cpu className="w-5 h-5 text-accent" />
          </div>
          <p className="text-2xl font-bold text-foreground">Celery 5.4</p>
          <div className="flex items-center text-xs text-accent space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Beat Scheduled</span>
          </div>
        </div>
      </div>
    </div>
  );
}
