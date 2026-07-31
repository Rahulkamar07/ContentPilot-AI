# ADR-0005: Next.js 14 and Shadcn UI for Frontend Architecture

## Context & Problem Statement
The user interface requires an ultra-responsive, dark-mode, glassmorphic design system supporting real-time queue approval, drag-and-drop posting calendars, rich analytics charts, and seamless multi-tenant workspace switching.

## Decision Drivers
- React 18 / Next.js 14 App Router server components for initial fast page load performance.
- Copy-paste accessible primitive components via **Shadcn UI** (Radix UI primitives + TailwindCSS).
- Client state management via Zustand and TanStack Query for server caching.

## Considered Options
1. **Next.js 14 (App Router) + TailwindCSS + Shadcn UI**
2. **Vite + React SPA**
3. **Nuxt 3 (Vue.js)**

## Decision Outcome
**Chosen Option**: **Next.js 14 + Shadcn UI**.
Provides full control over component styling without being locked into rigid UI framework themes, paired with Next.js SSR/SSG capabilities.

### Positive Consequences
- Exceptional aesthetic customization (glassmorphism, dark themes, Framer Motion transitions).
- Zero design lock-in with fully accessible Radix primitives.
- Built-in API route proxies for CORS bypass during local development.
