"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { api } from "@/core/api";
import { useAuthStore } from "@/store/useAuthStore";

export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((state) => state.setSession);

  const [mode, setMode] = useState<"login" | "register">("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const payload =
        mode === "login"
          ? { email, password }
          : { full_name: fullName.trim(), email, password };

      const response = await api.post(endpoint, payload);
      setSession(response.data.access_token, response.data.user);
      router.push("/workspaces");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 space-y-5">
        <div>
          <h1 className="text-2xl font-bold">{mode === "login" ? "Sign in" : "Create account"}</h1>
          <p className="text-sm text-muted-foreground">Connect to ContentPilot MVP workflow.</p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          {mode === "register" ? (
            <input
              className="w-full rounded-lg border border-border bg-background px-3 py-2"
              placeholder="Full name"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
            />
          ) : null}

          <input
            className="w-full rounded-lg border border-border bg-background px-3 py-2"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <input
            className="w-full rounded-lg border border-border bg-background px-3 py-2"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {error ? <p className="text-sm text-red-400">{error}</p> : null}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-primary px-3 py-2 text-primary-foreground disabled:opacity-60"
          >
            {loading ? "Please wait..." : mode === "login" ? "Sign in" : "Register"}
          </button>
        </form>

        <button
          type="button"
          className="text-sm text-primary"
          onClick={() => setMode((prev) => (prev === "login" ? "register" : "login"))}
        >
          {mode === "login" ? "Need an account? Register" : "Already have an account? Sign in"}
        </button>

        <Link href="/" className="text-xs text-muted-foreground block">
          ← Back to home
        </Link>
      </div>
    </div>
  );
}
