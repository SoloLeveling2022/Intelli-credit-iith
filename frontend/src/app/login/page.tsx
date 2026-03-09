"use client";

import { useState } from "react";
import Link from "next/link";
import { Loader2, Sun, Moon, ArrowLeft, Eye, EyeOff } from "lucide-react";
import { login } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/hooks/useTheme";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { loginUser } = useAuth();
  const { isDark, toggleTheme } = useTheme();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await login(username, password);
      loginUser(res.token, res.user);
    } catch {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen c-bg-main flex items-center justify-center p-4 relative">
      <div className="fixed top-0 left-0 right-0 z-40 flex items-center justify-between px-4 sm:px-6 h-14">
        <Link href="/" className="flex items-center gap-1.5 text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
          <ArrowLeft className="w-3.5 h-3.5" />
          Back
        </Link>
        <button onClick={toggleTheme} className="p-2 rounded-lg" style={{ color: "var(--text-secondary)" }} aria-label="Toggle theme">
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>

      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2.5 mb-8">
          <img
            src="/intelli-credit-logo.png"
            alt="Intelli-Credit"
            className="w-10 h-10 rounded-xl shadow-md"
          />
          <div>
            <span className="text-lg font-bold tracking-tight c-text">
              Intelli-Credit
            </span>
            <span className="text-[11px] block -mt-0.5 c-text-3">
              AI Credit & GST Platform
            </span>
          </div>
        </div>

        <div
          className="c-bg-card rounded-xl border c-border p-6"
          style={{ boxShadow: "var(--shadow-md)" }}
        >
          <h1 className="text-lg font-semibold c-text mb-1">Sign in</h1>
          <p className="text-sm c-text-3 mb-6">
            Access your credit appraisal and GST compliance workspace
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs font-medium c-text-2 mb-1.5 block">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                required
                className="w-full rounded-lg px-3 py-2.5 text-sm outline-none"
              />
            </div>
            <div>
              <label className="text-xs font-medium c-text-2 mb-1.5 block">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  className="w-full rounded-lg px-3 py-2.5 pr-10 text-sm outline-none"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5"
                  style={{ color: "var(--text-tertiary)" }}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <p className="text-xs text-red-400 bg-red-500/10 px-3 py-2 rounded-lg">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 c-bg-accent hover:c-bg-accent-hover disabled:opacity-50 rounded-lg text-white text-sm font-medium transition-colors"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <p className="text-center text-xs c-text-3 mt-5">
            Need an account?{" "}
            <Link
              href="/register"
              className="c-text-accent hover:underline font-medium"
            >
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
