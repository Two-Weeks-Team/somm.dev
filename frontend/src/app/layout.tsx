import type { Metadata } from "next";
import { Geist, Geist_Mono, Playfair_Display, Cinzel } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { AuthWrapper } from "@/components/AuthWrapper";
import { SiteHeader } from "@/components/SiteHeader";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  style: ["normal", "italic"],
});

const cinzel = Cinzel({
  variable: "--font-cinzel",
  subsets: ["latin"],
  weight: ["500", "700"],
});

export const metadata: Metadata = {
  title: "Somm - AI Code Evaluation",
  description: "AI-powered code evaluation with sommelier sophistication. Six specialized AI agents analyze your repositories and deliver comprehensive tasting notes.",
  keywords: ["code review", "AI", "code quality", "github", "evaluation", "sommelier"],
  authors: [{ name: "Somm Team" }],
  openGraph: {
    title: "Somm - AI Code Evaluation",
    description: "Every codebase has terroir. We're here to taste it.",
    type: "website",
    url: "https://somm.dev",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${playfair.variable} ${cinzel.variable} antialiased`}
      >
        <AuthProvider>
          <AuthWrapper>
            <SiteHeader />
            <main className="min-h-screen">
              {children}
            </main>
          </AuthWrapper>
        </AuthProvider>
      </body>
    </html>
  );
}
