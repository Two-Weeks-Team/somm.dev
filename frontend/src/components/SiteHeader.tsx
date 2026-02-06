"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Wine, Menu, X } from "lucide-react";
import { UserMenu } from "./UserMenu";

const NAV_LINKS = [
  { href: "/evaluate", label: "Evaluate" },
  { href: "/history", label: "History" },
];

export function SiteHeader() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[#722F37]/10 bg-[#FAF4E8]/95 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="rounded-full bg-[#722F37] p-2 transition-transform group-hover:scale-110">
            <Wine className="h-5 w-5 text-[#F7E7CE]" />
          </div>
          <span className="text-xl font-bold text-[#722F37]">Somm</span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm font-medium transition-colors ${
                pathname === link.href
                  ? "text-[#722F37]"
                  : "text-[#722F37]/60 hover:text-[#722F37]"
              }`}
            >
              {link.label}
            </Link>
          ))}
          <UserMenu />
        </nav>

        <div className="flex items-center gap-2 md:hidden">
          <UserMenu />
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="rounded-lg p-2 text-[#722F37]/60 transition-colors hover:bg-[#722F37]/5 hover:text-[#722F37]"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="border-t border-[#722F37]/10 bg-[#FAF4E8] md:hidden">
          <nav className="mx-auto max-w-7xl px-4 py-4">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`block rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                  pathname === link.href
                    ? "bg-[#722F37]/10 text-[#722F37]"
                    : "text-[#722F37]/60 hover:bg-[#722F37]/5 hover:text-[#722F37]"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
