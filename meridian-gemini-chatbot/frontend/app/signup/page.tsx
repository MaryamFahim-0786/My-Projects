"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { storeTokens } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { access_token, refresh_token } = await api.signup(email, password, fullName);
      storeTokens(access_token, refresh_token);
      router.push("/chat");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <Link href="/" className="font-display italic text-lg text-muted">
          Meridian
        </Link>
        <h1 className="font-display text-3xl mt-6 mb-8">Create your account</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-muted block mb-1">Full name</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-surface border border-line rounded px-3 py-2 focus:border-signal outline-none"
              placeholder="Optional"
            />
          </div>
          <div>
            <label className="text-sm text-muted block mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface border border-line rounded px-3 py-2 focus:border-signal outline-none"
            />
          </div>
          <div>
            <label className="text-sm text-muted block mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-surface border border-line rounded px-3 py-2 focus:border-signal outline-none"
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-signal text-white py-2.5 rounded font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-sm text-muted mt-6">
          Already have an account?{" "}
          <Link href="/login" className="text-signal hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
