"use client";

import React, { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setError("Missing token. Please try logging in again.");
      return;
    }

    let cancelled = false;

    const handleLogin = async () => {
      try {
        await login(token);
        if (!cancelled) {
          router.replace("/evaluate");
        }
      } catch (err) {
        if (!cancelled) {
          setError("Login failed. Please try again.");
        }
      }
    };

    handleLogin();

    return () => {
      cancelled = true;
    };
  }, [login, router, searchParams]);

  return (
    <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-xl border border-gray-100 bg-white p-6 text-center shadow-sm">
        <h1 className="text-2xl font-bold text-[#722F37] font-serif">
          Signing you in
        </h1>
        <p className="mt-3 text-gray-600">
          {error
            ? "We could not complete the sign-in."
            : "Please wait while we connect your GitHub account."}
        </p>
        {error && (
          <div className="mt-4 text-sm text-red-600">{error}</div>
        )}
        {error && (
          <button
            type="button"
            onClick={() => router.replace("/evaluate")}
            className="mt-6 inline-flex items-center justify-center rounded-lg bg-[#722F37] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#5a252c]"
          >
            Back to evaluation
          </button>
        )}
      </div>
    </div>
  );
}
