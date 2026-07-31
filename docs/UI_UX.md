# ContentPilot AI - UI/UX & Design System Architecture

## 1. Design Philosophy & Aesthetic Identity

**ContentPilot AI** features a sleek, dark-first, premium SaaS design system built on **glassmorphism**, dynamic gradients, vibrant accent colors, and smooth micro-animations using **TailwindCSS**, **Shadcn UI**, **Lucide Icons**, and **Framer Motion**.

---

## 2. Design Tokens & Color Palette

### 2.1 HSL Color Palette Definitions

```css
:root {
  /* Surface & Background Tokens */
  --background: 224 71% 4%;           /* #020617 Slate 950 - Deepest Base */
  --card: 222 47% 8%;                 /* #0b1329 Glassmorphism Card Surface */
  --card-elevated: 217 33% 13%;       /* Elevated Card Surface */
  --border: 217 19% 18%;              /* Subtle Border Glow */

  /* Text & Foreground Tokens */
  --foreground: 210 40% 98%;          /* High-Contrast Crisp White Text */
  --muted-foreground: 215 20% 65%;    /* Secondary Muted Gray Text */

  /* Brand Accents */
  --primary: 217 91% 60%;             /* Electric Cyan-Blue (#3b82f6) */
  --primary-foreground: 0 0% 100%;
  --secondary: 263 70% 50%;           /* Royal Violet Gradient (#8b5cf6) */
  --accent: 160 84% 39%;              /* Emerald Success Accent (#10b981) */

  /* Status Tokens */
  --destructive: 0 84% 60%;           /* Crimson Error Red */
  --warning: 38 92% 50%;              /* Amber Warning */
  --radius: 0.75rem;                  /* 12px Rounded Corners */
}
```

---

## 3. Page Layouts & Component Wireframes

### 3.1 Global Dashboard Layout Blueprint

```
+-----------------------------------------------------------------------------------+
|  [Logo ContentPilot AI]  | Workspace Selector v | (Bell) (User Profile)           |
+-----------------------------------------------------------------------------------+
|  SIDEBAR                |  MAIN CONTENT AREA                                      |
|  ---------------------  |  -----------------------------------------------------  |
|  [x] Overview           |  Header: Welcome back, Alex 👋                           |
|  [ ] News Feed          |                                                         |
|  [ ] AI Queue (4)       |  +----------------+ +----------------+ +---------------+ |
|  [ ] Schedule Calendar  |  | Ingested Feeds | | Pending AI     | | Queued Posts  | |
|  [ ] Analytics          |  | 142 Active     | | 12 Processing  | | 8 Approved   | |
|  [ ] Social Accounts    |  +----------------+ +----------------+ +---------------+ |
|  [ ] Settings           |                                                         |
|                         |  +----------------------------------------------------+  |
|  ---------------------  |  | Quick Approval Kanban Board                        |  |
|  Plan: PRO (12k/mo)     |  | [Card 1: Tech AI Chip] [Card 2: SpaceX Launch]     |  |
|  [ Upgrade ]            |  +----------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

### 3.2 Content Queue & Approval Board (`/queue`)

```tsx
import React from "react";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, X, RefreshCw, Edit3 } from "lucide-react";

export function QueueCard({ post, onApprove, onReject, onRegenerate }) {
  return (
    <Card className="bg-card/60 backdrop-blur-md border-border/50 hover:border-primary/50 transition-all duration-300 shadow-xl rounded-xl overflow-hidden">
      <div className="relative aspect-square w-full bg-slate-900">
        <img
          src={post.imageUrl}
          alt="Generated Editorial Art"
          className="object-cover w-full h-full hover:scale-105 transition-transform duration-500"
        />
        <Badge className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur text-primary border-primary/30">
          {post.category}
        </Badge>
      </div>

      <CardContent className="p-4 space-y-3">
        <p className="text-sm text-foreground/90 font-normal line-clamp-3">
          {post.caption}
        </p>
        <div className="flex flex-wrap gap-1">
          {post.hashtags.map((tag) => (
            <span key={tag} className="text-xs text-primary/80 font-medium">
              {tag}
            </span>
          ))}
        </div>
      </CardContent>

      <CardFooter className="p-4 pt-0 flex justify-between items-center border-t border-border/30 mt-2">
        <Button size="sm" variant="ghost" onClick={() => onRegenerate(post.id)}>
          <RefreshCw className="w-4 h-4 mr-1 text-muted-foreground" /> Regenerate
        </Button>
        <div className="flex space-x-2">
          <Button size="sm" variant="destructive" onClick={() => onReject(post.id)}>
            <X className="w-4 h-4 mr-1" /> Reject
          </Button>
          <Button size="sm" className="bg-primary hover:bg-primary/90" onClick={() => onApprove(post.id)}>
            <Check className="w-4 h-4 mr-1" /> Approve
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
```

---

## 4. Frontend Component Hierarchy & State Architecture

### Component Hierarchy Tree

```
src/
├── app/
│   ├── (auth)/login/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx                # Shell: Sidebar, Topbar, WorkspaceContext
│   │   ├── overview/page.tsx         # Dashboard Stats & Recent Activity
│   │   ├── news-feed/page.tsx        # RSS Feeds & Article Ingestion Cards
│   │   ├── queue/page.tsx            # Approval Queue Kanban
│   │   ├── schedule/page.tsx         # Drag-and-Drop Timezone Calendar
│   │   ├── analytics/page.tsx        # Recharts Metrics Suite
│   │   └── settings/page.tsx         # Brand Tone & Social Accounts
├── components/
│   ├── ui/                           # Primitive Shadcn Components (Button, Dialog, Select)
│   ├── queue/
│   │   ├── QueueCard.tsx
│   │   ├── CaptionEditModal.tsx
│   │   └── ImageRegenerateDialog.tsx
│   ├── analytics/
│   │   ├── ImpressionsChart.tsx
│   │   └── CategoryPerformancePie.tsx
│   └── shared/
│       ├── SidebarNav.tsx
│       ├── HeaderUserMenu.tsx
│       └── WorkspaceSwitcher.tsx
```

---

## 5. Client-Side State Management (Zustand + TanStack Query)

### 5.1 Server State Isolation via TanStack Query

Server state (articles, queued posts, analytics) is fetched and cached using query key factories:

```typescript
// src/hooks/useQueuePosts.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/core/api";

export const queueKeys = {
  all: ["queue-posts"] as const,
  byWorkspace: (workspaceId: string) => [...queueKeys.all, workspaceId] as const,
};

export function useQueuePosts(workspaceId: string) {
  return useQuery({
    queryKey: queueKeys.byWorkspace(workspaceId),
    queryFn: async () => {
      const response = await api.get(`/posts/queue`, {
        headers: { "X-Workspace-ID": workspaceId },
      });
      return response.data.data;
    },
    staleTime: 1000 * 30, // 30 seconds
  });
}
```

### 5.2 UI Transient State via Zustand Store

Active workspace selection and UI theme/modal states are managed in Zustand:

```typescript
// src/store/useWorkspaceStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface WorkspaceState {
  activeWorkspaceId: string | null;
  activeWorkspaceSlug: string | null;
  setActiveWorkspace: (id: string, slug: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set) => ({
      activeWorkspaceId: null,
      activeWorkspaceSlug: null,
      setActiveWorkspace: (id, slug) => set({ activeWorkspaceId: id, activeWorkspaceSlug: slug }),
    }),
    { name: "contentpilot-active-workspace" }
  )
);
```

---

## 6. Accessibility & Responsive Design Standards

1. **WCAG 2.1 AA Compliance**: All text elements meet a minimum contrast ratio of 4.5:1 against glassmorphic backgrounds.
2. **Keyboard Navigation**: Full `Tab`, `Shift+Tab`, `Space`, and `Enter` keyboard focus support across all dialogs and approve buttons.
3. **Mobile Responsiveness**: Dynamic layout scaling from mobile viewports (375px) to ultra-wide displays (2560px), with collapsible mobile navigation sheets.

---

## 7. Super-Admin Panel Dashboard Architecture (`/admin`)

System administrators (`SUPER_ADMIN` role) access a centralized telemetry and management dashboard for monitoring tenant activity, background workers, AI token costs, and API usage quotas.

### Admin Dashboard Wireframe Blueprint

```
+------------------------------------------------------------------------------------+
|  [Logo ContentPilot Admin] | System Status: HEALTHY | (Live Logs) (Admin Profile)  |
+------------------------------------------------------------------------------------+
|  ADMIN NAV               |  SYSTEM TELEMETRY OVERVIEW                              |
|  ----------------------  |  -----------------------------------------------------  |
|  [x] System Health       |  +----------------+ +----------------+ +----------------+ |
|  [ ] Tenant Workspaces   |  | Total Users    | | Active Workers | | Monthly AI Cost| |
|  [ ] Worker Queues (3)   |  | 4,281 Users    | | 16 Celery / GPU| | $1,248.50 USD  | |
|  [ ] AI Usage & Costs    |  +----------------+ +----------------+ +----------------+ |
|  [ ] API Quotas & Keys   |                                                         |
|  [ ] Audit System Logs   |  +----------------------------------------------------+ |
|                          |  | Real-Time Celery Queue Lag & GPU VRAM Load         | |
|                          |  | [Chart: ai_queue lag] [Chart: NVIDIA VRAM 64%]    | |
|                          |  +----------------------------------------------------+ |
+------------------------------------------------------------------------------------+
```

### Key Admin Functionalities:
1. **Tenant & Workspace Management**: View all workspace subscriptions, override plan tier limits, or suspend abusive accounts.
2. **Worker Queue Inspector**: Live view of Celery task backlogs (`scraper_queue`, `ai_queue`, `publisher_queue`) with manual purge/retry buttons.
3. **AI Cost & API Quota Telemetry**: Breakdown of token consumption by model provider (OpenAI, Gemini, Local FLUX) and active SaaS tenant.

