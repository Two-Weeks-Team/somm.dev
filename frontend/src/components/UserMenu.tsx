"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { LogOut, History, ChevronDown } from "lucide-react";
import Link from "next/link";

export function UserMenu() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (isLoading) {
    return (
      <div className="h-8 w-8 animate-pulse rounded-full bg-[#722F37]/20" />
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <Link
        href={`${process.env.NEXT_PUBLIC_API_URL || "https://api.somm.dev"}/auth/github`}
        className="rounded-lg bg-[#722F37] px-4 py-2 text-sm font-medium text-[#F7E7CE] transition-colors hover:bg-[#5A252C]"
      >
        Login with GitHub
      </Link>
    );
  }

  const initials = user.username
    ? user.username.slice(0, 2).toUpperCase()
    : "U";

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-lg px-3 py-2 transition-colors hover:bg-[#722F37]/10"
      >
        {user.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.username}
            className="h-8 w-8 rounded-full border-2 border-[#722F37]/20"
          />
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#722F37] text-xs font-medium text-[#F7E7CE]">
            {initials}
          </div>
        )}
        <span className="hidden text-sm font-medium text-[#722F37] md:block">
          {user.username}
        </span>
        <ChevronDown
          className={`h-4 w-4 text-[#722F37]/60 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-xl border border-[#722F37]/10 bg-white py-2 shadow-lg">
          <div className="border-b border-[#722F37]/10 px-4 py-3">
            <p className="text-sm font-medium text-[#722F37]">{user.username}</p>
            {user.email && (
              <p className="text-xs text-[#722F37]/60">{user.email}</p>
            )}
          </div>

          <div className="py-1">
            <Link
              href="/history"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 transition-colors hover:bg-[#722F37]/5"
            >
              <History className="h-4 w-4" />
              Evaluation History
            </Link>
          </div>

          <div className="border-t border-[#722F37]/10 py-1">
            <button
              onClick={() => {
                logout();
                setIsOpen(false);
              }}
              className="flex w-full items-center gap-3 px-4 py-2 text-sm text-red-600 transition-colors hover:bg-red-50"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
