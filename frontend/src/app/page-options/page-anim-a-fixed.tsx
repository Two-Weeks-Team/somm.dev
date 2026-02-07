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

const criteriaModes = [
  { name: "Basic", desc: "General code review", bestFor: "Everyday projects", weight: "Balanced" },
  { name: "Hackathon", desc: "Gemini 3 judging criteria", bestFor: "Hackathon submissions", weight: "Tech 40%" },
  { name: "Academic", desc: "Research-focused evaluation", bestFor: "Research projects", weight: "Novelty" },
  { name: "Custom", desc: "Define your own criteria", bestFor: "Special requirements", weight: "Flexible" },
];

const scoringTiers = [
  { range: "95-100", name: "Legendary", icon: Trophy, color: "text-yellow-600", bg: "from-yellow-100/80 to-amber-100/80", border: "border-yellow-300" },
  { range: "90-94", name: "Grand Cru", icon: Trophy, color: "text-amber-600", bg: "from-amber-100/80 to-yellow-100/80", border: "border-amber-300" },
  { range: "85-89", name: "Premier Cru", icon: Medal, color: "text-orange-600", bg: "from-orange-100/80 to-amber-100/80", border: "border-orange-300" },
  { range: "80-84", name: "Village", icon: Award, color: "text-emerald-600", bg: "from-emerald-100/80 to-green-100/80", border: "border-emerald-300" },
  { range: "70-79", name: "Table Wine", icon: Star, color: "text-blue-600", bg: "from-blue-100/80 to-sky-100/80", border: "border-blue-300" },
  { range: "60-69", name: "House Wine", icon: Wine, color: "text-purple-600", bg: "from-purple-100/80 to-violet-100/80", border: "border-purple-300" },
  { range: "<60", name: "Corked", icon: AlertTriangle, color: "text-red-600", bg: "from-red-100/80 to-rose-100/80", border: "border-red-300" },
];

export default function Home() {
  const [activeSommelier, setActiveSommelier] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
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
      {/* Animated Background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-[#722F37]/5 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-[#DAA520]/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#FAF4E8]/80 backdrop-blur-md border-b border-[#722F37]/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-full bg-[#722F37] flex items-center justify-center transition-transform group-hover:scale-110">
              <Wine className="w-4 h-4 text-[#F7E7CE]" />
            </div>
            <span className="font-serif-elegant text-xl font-bold text-[#722F37]">Somm</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-[#722F37]/70">
            <a href="#how-it-works" className="hover:text-[#722F37] transition-colors">How It Works</a>
            <a href="#features" className="hover:text-[#722F37] transition-colors">Features</a>
            <a href="#sommeliers" className="hover:text-[#722F37] transition-colors">Sommeliers</a>
          </div>
          <Link href="/evaluate" className="px-4 py-2 bg-[#722F37] text-[#F7E7CE] rounded-full text-sm font-medium hover:bg-[#5A252C] transition-all">
            Start Evaluation
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="relative z-10">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#722F37]/10 text-[#722F37] text-sm font-medium mb-6">
                <Sparkles className="w-4 h-4" />
                <span>Now with Gemini 3</span>
              </div>

              <h1 className="font-serif-elegant text-5xl md:text-6xl lg:text-7xl font-bold text-[#722F37] leading-[1.1] mb-6">
                AI Code
                <br />
                <span className="italic font-normal">Evaluation</span>
                <br />
                with Sommelier
                <br />
                Sophistication
              </h1>

              <p className="text-lg text-gray-600 mb-8 max-w-lg leading-relaxed">
                Six specialized AI agents analyze your repositories from every angle—
                structure, quality, security, and innovation.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/evaluate" className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-[#722F37] text-[#F7E7CE] rounded-full font-semibold hover:bg-[#5A252C] transition-all">
                  Start Free Evaluation
                  <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                </Link>
                <Link href="/evaluate/demo/result" className="inline-flex items-center justify-center gap-2 px-8 py-4 border-2 border-[#722F37]/20 text-[#722F37] rounded-full font-semibold hover:border-[#722F37] transition-all">
                  See Demo Result
                </Link>
              </div>
            </div>

            {/* Right Content - Orbital Sommeliers */}
            <div id="sommelier-container" className="relative h-[600px]">
              {mounted && (
                <>
                  {/* Jean-Pierre Center with Parallax */}
                  <div 
                    className="absolute top-1/2 left-1/2 z-30 transition-transform duration-300 ease-out"
                    style={{
                      transform: `translate(calc(-50% + ${mousePos.x * -30}px), calc(-50% + ${mousePos.y * -30}px))`,
                    }}
                  >
                    <div 
                      className="w-36 h-36 rounded-full overflow-hidden border-4 border-white shadow-2xl ring-4 ring-[#DAA520] ring-offset-4 transition-transform hover:scale-110"
                      onMouseEnter={() => setActiveSommelier('jeanpierre')}
                      onMouseLeave={() => setActiveSommelier(null)}
                    >
                      <Image src="/sommeliers/jeanpierre.png" alt="Jean-Pierre" fill className="object-cover object-top" priority />
                    </div>
                    
                    {activeSommelier === 'jeanpierre' && (
                      <div className="absolute -bottom-24 left-1/2 -translate-x-1/2 w-64 bg-white rounded-xl px-4 py-3 shadow-2xl border border-[#DAA520]"
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <Trophy className="w-5 h-5 text-[#DAA520]" />
                          <div className="flex-1">
                            <div className="flex items-center gap-1">
                              <p className="font-semibold text-[#722F37]">Jean-Pierre</p>
                              <span className="text-[10px] px-1.5 py-0.5 bg-[#DAA520] text-white rounded-full">MASTER</span>
                            </div>
                            <p className="text-xs text-gray-500">Grand Sommelier</p>
                          </div>
                        </div>
                        <p className="text-xs text-gray-600">Synthesizes all evaluations into final verdict</p>
                      </div>
                    )}
                  </div>

                  {/* Orbiting Sommeliers - CSS Only */}
                  {sommeliers.slice(0, 5).map((s, i) => {
                    const orbitClass = `orbit-sommelier-${i}`;
                    const IconComponent = s.icon;
                    
                    return (
                      <div
                        key={s.id}
                        className={`absolute top-1/2 left-1/2 w-20 h-20 -translate-x-1/2 -translate-y-1/2 ${orbitClass}`}
                        style={{ zIndex: 20 - i }}
                        onMouseEnter={() => setActiveSommelier(s.id)}
                        onMouseLeave={() => setActiveSommelier(null)}
                      >
                        <div 
                          className="w-full h-full rounded-full overflow-hidden border-4 border-white shadow-xl transition-all duration-300 hover:scale-125 hover:shadow-2xl"
                          style={{ borderColor: s.color }}
                        >
                          <Image src={`/sommeliers/${s.id}.png`} alt={s.name} fill className="object-cover object-top" />
                        </div>
                        
                        {activeSommelier === s.id && (
                          <div className="absolute -bottom-24 left-1/2 -translate-x-1/2 w-56 bg-white rounded-xl px-3 py-2 shadow-2xl border border-gray-100 z-50"
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: `${s.color}20` }}>
                                <IconComponent className="w-4 h-4" style={{ color: s.color }} />
                              </div>
                              <div>
                                <p className="font-semibold text-sm text-[#722F37]">{s.name}</p>
                                <p className="text-xs text-gray-500">{s.role}</p>
                              </div>
                            </div>
                            <p className="text-xs text-gray-600">{s.feature}</p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">How It Works</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">Like a master sommelier orchestrates a tasting panel, our AI agents analyze your code in parallel.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: 1, title: "Submit Repository", desc: "Connect your GitHub repository or paste any public repo URL" },
              { step: 2, title: "Parallel Analysis", desc: "Six specialized sommeliers evaluate simultaneously" },
              { step: 3, title: "Get Verdict", desc: "Jean-Pierre synthesizes all findings into actionable insights" },
            ].map((item) => (
              <div key={item.step} className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/10">
                <div className="w-12 h-12 rounded-xl bg-[#722F37] text-[#F7E7CE] flex items-center justify-center text-xl font-bold mb-6">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold text-[#722F37] mb-3">{item.title}</h3>
                <p className="text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Features</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Zap, title: "Real-time Streaming", desc: "Watch evaluations unfold live" },
              { icon: FileText, title: "PDF Reports", desc: "Export professional tasting notes" },
              { icon: Share2, title: "One-Click Share", desc: "Share results with your team" },
              { icon: Trophy, title: "4 Eval Modes", desc: "Basic, Hackathon, Academic, Custom" },
            ].map((feature) => (
              <div key={feature.title} className="bg-white rounded-xl p-6 shadow-sm border border-[#722F37]/5">
                <div className="w-12 h-12 rounded-lg bg-[#722F37]/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-[#722F37]" />
                </div>
                <h3 className="font-semibold text-[#722F37] mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Meet Your Sommeliers */}
      <section id="sommeliers" className="py-24 px-6 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Meet Your Sommeliers</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sommeliers.map((s) => {
              const IconComponent = s.icon;
              return (
                <div key={s.id} className="bg-white rounded-xl overflow-hidden shadow-sm border border-[#722F37]/5">
                  <div className="h-28 relative" style={{ backgroundColor: s.color }}>
                    <div className="absolute right-4 -bottom-6 w-20 h-20 rounded-full overflow-hidden border-4 border-white">
                      <Image src={`/sommeliers/${s.id}.png`} alt={s.name} fill className="object-cover object-top" />
                    </div>
                  </div>
                  <div className="p-6 pt-10">
                    <div className="flex items-center gap-2 mb-1">
                      <IconComponent className="w-4 h-4" style={{ color: s.color }} />
                      <h3 className="font-semibold text-[#722F37]">{s.name}</h3>
                    </div>
                    <p className="text-sm font-medium" style={{ color: s.color }}>{s.role}</p>
                    <p className="text-sm text-gray-600 mt-2">{s.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#722F37] rounded-3xl p-12 text-[#F7E7CE] relative overflow-hidden">
            <div className="absolute inset-0">
              <div className="absolute top-0 left-0 w-64 h-64 bg-white/5 rounded-full blur-3xl" />
            </div>
            <div className="relative z-10">
              <h2 className="font-serif-elegant text-4xl font-bold mb-4">Ready to taste your code?</h2>
              <Link href="/evaluate" className="inline-flex items-center gap-2 px-10 py-5 bg-[#F7E7CE] text-[#722F37] rounded-full font-semibold">
                Start Your Evaluation <ArrowRight className="w-6 h-6" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-[#722F37]/10">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#722F37] flex items-center justify-center">
              <Wine className="w-4 h-4 text-[#F7E7CE]" />
            </div>
            <span className="font-serif-elegant text-lg font-bold text-[#722F37]">Somm</span>
          </div>
          <p className="text-sm text-gray-500">© 2025 Somm.dev</p>
        </div>
      </footer>

      <style jsx global>{`
        @keyframes orbit0 {
          from { transform: rotate(0deg) translateX(180px) rotate(0deg); }
          to { transform: rotate(360deg) translateX(180px) rotate(-360deg); }
        }
        @keyframes orbit1 {
          from { transform: rotate(72deg) translateX(170px) rotate(-72deg); }
          to { transform: rotate(432deg) translateX(170px) rotate(-432deg); }
        }
        @keyframes orbit2 {
          from { transform: rotate(144deg) translateX(190px) rotate(-144deg); }
          to { transform: rotate(504deg) translateX(190px) rotate(-504deg); }
        }
        @keyframes orbit3 {
          from { transform: rotate(216deg) translateX(175px) rotate(-216deg); }
          to { transform: rotate(576deg) translateX(175px) rotate(-576deg); }
        }
        @keyframes orbit4 {
          from { transform: rotate(288deg) translateX(185px) rotate(-288deg); }
          to { transform: rotate(648deg) translateX(185px) rotate(-648deg); }
        }
        
        .orbit-sommelier-0 { animation: orbit0 60s linear infinite; }
        .orbit-sommelier-1 { animation: orbit1 50s linear infinite; }
        .orbit-sommelier-2 { animation: orbit2 70s linear infinite; }
        .orbit-sommelier-3 { animation: orbit3 55s linear infinite; }
        .orbit-sommelier-4 { animation: orbit4 65s linear infinite; }
      `}</style>
    </div>
  );
}
