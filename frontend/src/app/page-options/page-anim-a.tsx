'use client';

import { useState, useEffect } from 'react';
import { Wine, Trophy, Medal, Award, Star, AlertTriangle, Sparkles, ArrowRight, Zap, FileText, Share2, ChevronDown, FolderGit, Code, Shield, Lightbulb, Wrench } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

const sommeliers = [
  { id: "marcel", name: "Marcel", role: "Cellar Master", desc: "Structure & Metrics", color: "#8B7355", feature: "Analyzes repository architecture", icon: FolderGit },
  { id: "isabella", name: "Isabella", role: "Wine Critic", desc: "Code Quality", color: "#C41E3A", feature: "Evaluates readability & design", icon: Code },
  { id: "heinrich", name: "Heinrich", role: "Quality Inspector", desc: "Security & Testing", color: "#2F4F4F", feature: "Inspects test coverage", icon: Shield },
  { id: "sofia", name: "Sofia", role: "Vineyard Scout", desc: "Innovation & Tech", color: "#DAA520", feature: "Discovers cutting-edge tech", icon: Lightbulb },
  { id: "laurent", name: "Laurent", role: "Winemaker", desc: "Implementation", color: "#228B22", feature: "Reviews code craftsmanship", icon: Wrench },
  { id: "jeanpierre", name: "Jean-Pierre", role: "Grand Sommelier", desc: "Final Synthesis", color: "#4169E1", feature: "Synthesizes final verdict", icon: Trophy },
];

export default function Home() {
  const [activeSommelier, setActiveSommelier] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const rect = document.getElementById('sommelier-container')?.getBoundingClientRect();
      if (rect) {
        setMousePos({
          x: (e.clientX - rect.left - rect.width / 2) / rect.width,
          y: (e.clientY - rect.top - rect.height / 2) / rect.height,
        });
      }
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="min-h-screen bg-[#FAF4E8] overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#FAF4E8]/80 backdrop-blur-md border-b border-[#722F37]/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#722F37] flex items-center justify-center">
              <Wine className="w-4 h-4 text-[#F7E7CE]" />
            </div>
            <span className="font-serif-elegant text-xl font-bold text-[#722F37]">Somm</span>
          </Link>
          <Link href="/evaluate" className="px-4 py-2 bg-[#722F37] text-[#F7E7CE] rounded-full text-sm font-medium">
            Start Evaluation
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative min-h-screen pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="font-serif-elegant text-5xl md:text-6xl lg:text-7xl font-bold text-[#722F37] leading-[1.1] mb-6">
                AI Code<br /><span className="italic font-normal">Evaluation</span>
              </h1>
              <Link href="/evaluate" className="inline-flex items-center gap-2 px-8 py-4 bg-[#722F37] text-[#F7E7CE] rounded-full font-semibold">
                Start Free Evaluation
              </Link>
            </div>

            {/* Orbital Animation Container */}
            <div id="sommelier-container" className="relative h-[600px]">
              {/* Jean-Pierre Center */}
              <div 
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-36 h-36 z-20"
                style={{
                  transform: `translate(calc(-50% + ${mousePos.x * -20}px), calc(-50% + ${mousePos.y * -20}px))`,
                }}
              >
                <div className="w-full h-full rounded-full overflow-hidden border-4 border-white shadow-2xl ring-4 ring-[#DAA520]">
                  <Image src="/sommeliers/jeanpierre.png" alt="Jean-Pierre" fill className="object-cover object-top" />
                </div>
              </div>

              {/* Orbiting Sommeliers */}
              {sommeliers.slice(0, 5).map((s, i) => {
                const angle = (i * 72) + (Date.now() / 100); // 60초에 한 바퀴
                const radius = 180;
                const parallaxX = mousePos.x * (30 + i * 5);
                const parallaxY = mousePos.y * (30 + i * 5);
                
                return (
                  <div
                    key={s.id}
                    className="absolute top-1/2 left-1/2 w-20 h-20 -translate-x-1/2 -translate-y-1/2"
                    style={{
                      transform: `rotate(${angle}deg) translateX(${radius}px) rotate(${-angle}deg) translate(${parallaxX}px, ${parallaxY}px)`,
                      animation: `orbit${i} 60s linear infinite`,
                    }}
                  >
                    <div 
                      className="w-full h-full rounded-full overflow-hidden border-4 border-white shadow-xl"
                      style={{ borderColor: s.color }}
                    >
                      <Image src={`/sommeliers/${s.id}.png`} alt={s.name} fill className="object-cover object-top" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <style jsx global>{`
        @keyframes orbit0 { from { transform: rotate(0deg) translateX(180px) rotate(0deg); } to { transform: rotate(360deg) translateX(180px) rotate(-360deg); } }
        @keyframes orbit1 { from { transform: rotate(72deg) translateX(180px) rotate(-72deg); } to { transform: rotate(432deg) translateX(180px) rotate(-432deg); } }
        @keyframes orbit2 { from { transform: rotate(144deg) translateX(180px) rotate(-144deg); } to { transform: rotate(504deg) translateX(180px) rotate(-504deg); } }
        @keyframes orbit3 { from { transform: rotate(216deg) translateX(180px) rotate(-216deg); } to { transform: rotate(576deg) translateX(180px) rotate(-576deg); } }
        @keyframes orbit4 { from { transform: rotate(288deg) translateX(180px) rotate(-288deg); } to { transform: rotate(648deg) translateX(180px) rotate(-648deg); } }
      `}</style>
    </div>
  );
}
