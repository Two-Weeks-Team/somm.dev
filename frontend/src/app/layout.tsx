import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { AuthWrapper } from "@/components/AuthWrapper";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
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
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AuthProvider>
          <AuthWrapper>
            {children}
          </AuthWrapper>
        </AuthProvider>
      </body>
    </html>
  );
}
