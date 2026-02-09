import type { Metadata } from "next";
import { Geist, Geist_Mono, Playfair_Display, Cinzel } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { AuthWrapper } from "@/components/AuthWrapper";
import { SiteHeader } from "@/components/SiteHeader";

const GA_ID = "G-65HJEVF1M4";

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
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_ID}');
        `}
      </Script>
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
