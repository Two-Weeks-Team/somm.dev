'use client';

import { useState } from 'react';
import { Wine, Trophy, Medal, Award, Star, AlertTriangle, Sparkles, ArrowRight, Zap, FileText, Share2, ChevronDown } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

const sommeliers = [
  { id: "marcel", name: "Marcel", role: "Cellar Master", desc: "Structure & Metrics", color: "#8B7355" },
  { id: "isabella", name: "Isabella", role: "Wine Critic", desc: "Code Quality", color: "#C41E3A" },
  { id: "heinrich", name: "Heinrich", role: "Quality Inspector", desc: "Security & Testing", color: "#2F4F4F" },
  { id: "sofia", name: "Sofia", role: "Vineyard Scout", desc: "Innovation & Tech", color: "#DAA520" },
  { id: "laurent", name: "Laurent", role: "Winemaker", desc: "Implementation", color: "#228B22" },
  { id: "jeanpierre", name: "Jean-Pierre", role: "Grand Sommelier", desc: "Final Synthesis", color: "#4169E1" },
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
            <a href="#how-it-works" className="hover:text-[#722F37] transition-colors relative group">
              How It Works
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-[#722F37] transition-all group-hover:w-full" />
            </a>
            <a href="#features" className="hover:text-[#722F37] transition-colors relative group">
              Features
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-[#722F37] transition-all group-hover:w-full" />
            </a>
            <a href="#sommeliers" className="hover:text-[#722F37] transition-colors relative group">
              Sommeliers
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-[#722F37] transition-all group-hover:w-full" />
            </a>
          </div>
          <Link
            href="/evaluate"
            className="px-4 py-2 bg-[#722F37] text-[#F7E7CE] rounded-full text-sm font-medium hover:bg-[#5A252C] transition-colors hover:shadow-lg hover:shadow-[#722F37]/25 hover:scale-105"
          >
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
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#722F37]/10 text-[#722F37] text-sm font-medium mb-6 animate-fadeIn">
                <Sparkles className="w-4 h-4 animate-pulse" />
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
                <Link
                  href="/evaluate"
                  className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-[#722F37] text-[#F7E7CE] rounded-full font-semibold transition-all hover:bg-[#5A252C] hover:shadow-xl hover:shadow-[#722F37]/20 hover:scale-105"
                >
                  Start Free Evaluation
                  <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                </Link>
                <Link
                  href="/evaluate/demo/result"
                  className="inline-flex items-center justify-center gap-2 px-8 py-4 border-2 border-[#722F37]/20 text-[#722F37] rounded-full font-semibold hover:border-[#722F37] hover:bg-[#722F37]/5 transition-all hover:scale-105"
                >
                  See Demo Result
                </Link>
              </div>

              <p className="mt-6 text-sm text-gray-500">
                Free for open source • No signup required
              </p>
            </div>

            {/* Right Content - Interactive Sommelier Collage */}
            <div className="relative">
              <div className="relative h-[500px] md:h-[600px]">
                {/* Central Image - Jean-Pierre */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 md:w-56 md:h-56 rounded-full overflow-hidden border-4 border-white shadow-2xl z-20 transition-transform hover:scale-105">
                  <Image
                    src="/sommeliers/jeanpierre.png"
                    alt="Jean-Pierre"
                    fill
                    className="object-cover object-top"
                    priority
                  />
                </div>

                {/* Surrounding Images with Hover Effects */}
                {sommeliers.slice(0, 5).map((s, i) => {
                  const positions = [
                    { top: '10%', left: '10%' },
                    { top: '5%', right: '20%' },
                    { top: '35%', right: '5%' },
                    { bottom: '20%', right: '15%' },
                    { bottom: '10%', left: '20%' },
                  ];
                  
                  return (
                    <div
                      key={s.id}
                      className="absolute cursor-pointer group"
                      style={{
                        ...positions[i],
                        zIndex: activeSommelier === s.id ? 30 : 20 - i,
                      }}
                      onMouseEnter={() => setActiveSommelier(s.id)}
                      onMouseLeave={() => setActiveSommelier(null)}
                    >
                      <div className={`relative w-20 h-20 md:w-24 md:h-24 rounded-full overflow-hidden border-4 border-white shadow-xl transition-all duration-500 ${
                        activeSommelier === s.id ? 'scale-125 shadow-2xl' : 'hover:scale-110'
                      }`}
                      style={{
                        boxShadow: activeSommelier === s.id ? `0 25px 50px -12px ${s.color}40` : undefined,
                      }}
                      >
                        <Image
                          src={`/sommeliers/${s.id}.png`}
                          alt={s.name}
                          fill
                          className="object-cover object-top"
                        />
                      </div>
                      
                      {/* Hover Tooltip */}
                      <div className={`absolute -bottom-16 left-1/2 -translate-x-1/2 whitespace-nowrap transition-all duration-300 ${
                        activeSommelier === s.id ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2 pointer-events-none'
                      }`}>
                        <div className="bg-white rounded-lg px-4 py-2 shadow-xl border border-gray-100">
                          <p className="font-semibold text-[#722F37]">{s.name}</p>
                          <p className="text-xs text-gray-500">{s.role}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-6 h-6 text-[#722F37]/40" />
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              How It Works
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Like a master sommelier orchestrates a tasting panel, our AI agents analyze your code in parallel.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: 1, title: "Submit Repository", desc: "Connect your GitHub repository or paste any public repo URL" },
              { step: 2, title: "Parallel Analysis", desc: "Six specialized sommeliers evaluate simultaneously" },
              { step: 3, title: "Get Verdict", desc: "Jean-Pierre synthesizes all findings into actionable insights" },
            ].map((item, i) => (
              <div key={item.step} className="relative group">
                <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/10 h-full transition-all hover:shadow-lg hover:border-[#722F37]/20 hover:-translate-y-1">
                  <div className="w-12 h-12 rounded-xl bg-[#722F37] text-[#F7E7CE] flex items-center justify-center text-xl font-bold mb-6 transition-transform group-hover:scale-110">
                    {item.step}
                  </div>
                  <h3 className="text-xl font-semibold text-[#722F37] mb-3">{item.title}</h3>
                  <p className="text-gray-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              Features
            </h2>
            <p className="text-gray-600">Everything you need for comprehensive code evaluation</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Zap, title: "Real-time Streaming", desc: "Watch evaluations unfold live with SSE streaming" },
              { icon: FileText, title: "PDF Reports", desc: "Export professional tasting notes as shareable PDF" },
              { icon: Share2, title: "One-Click Share", desc: "Share results with your team instantly" },
              { icon: Trophy, title: "4 Eval Modes", desc: "Basic, Hackathon, Academic, Custom" },
            ].map((feature, i) => (
              <div key={feature.title} className="group bg-white rounded-xl p-6 shadow-sm border border-[#722F37]/5 hover:shadow-md hover:border-[#722F37]/20 transition-all hover:-translate-y-1">
                <div className="w-12 h-12 rounded-lg bg-[#722F37]/10 flex items-center justify-center mb-4 transition-colors group-hover:bg-[#722F37]">
                  <feature.icon className="w-6 h-6 text-[#722F37] group-hover:text-[#F7E7CE] transition-colors" />
                </div>
                <h3 className="font-semibold text-[#722F37] mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Evaluation Modes */}
      <section className="py-24 px-6 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              Evaluation Modes
            </h2>
            <p className="text-gray-600">Choose the criteria that fits your needs</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {criteriaModes.map((mode) => (
              <div key={mode.name} className="bg-white rounded-xl p-6 border border-[#722F37]/10 hover:border-[#722F37]/30 transition-all group hover:shadow-lg hover:-translate-y-1">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-[#722F37] text-lg">{mode.name}</h3>
                  <span className="text-xs px-2 py-1 bg-[#722F37]/5 text-[#722F37] rounded-full">
                    {mode.weight}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{mode.desc}</p>
                <p className="text-xs text-[#722F37]/60">Best for: {mode.bestFor}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Meet Your Sommeliers */}
      <section id="sommeliers" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              Meet Your Sommeliers
            </h2>
            <p className="text-gray-600">Six AI experts, each with a unique perspective on code quality</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sommeliers.map((s) => (
              <div
                key={s.id}
                className="group bg-white rounded-xl overflow-hidden shadow-sm border border-[#722F37]/5 hover:shadow-xl transition-all cursor-pointer hover:-translate-y-1"
              >
                <div className="h-28 relative" style={{ backgroundColor: s.color }}>
                  <div className="absolute right-4 -bottom-6 w-20 h-20 rounded-full overflow-hidden border-4 border-white shadow-lg transition-transform group-hover:scale-110">
                    <Image
                      src={`/sommeliers/${s.id}.png`}
                      alt={s.name}
                      fill
                      className="object-cover object-top"
                    />
                  </div>
                </div>
                <div className="p-6 pt-10">
                  <h3 className="font-semibold text-[#722F37] text-lg">{s.name}</h3>
                  <p className="text-sm font-medium" style={{ color: s.color }}>{s.role}</p>
                  <p className="text-sm text-gray-600 mt-1">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Scoring System */}
      <section className="py-24 px-6 bg-white/50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
              Scoring System
            </h2>
            <p className="text-gray-600">From legendary cellars to house wines — every codebase has its place</p>
          </div>
          <div className="space-y-3">
            {scoringTiers.map((tier) => {
              const Icon = tier.icon;
              return (
                <div
                  key={tier.name}
                  className={`flex items-center gap-4 p-4 rounded-xl bg-gradient-to-r ${tier.bg} border ${tier.border} transition-all hover:shadow-md cursor-default group`}
                >
                  <div className={`w-10 h-10 rounded-lg bg-white/80 flex items-center justify-center ${tier.color} transition-transform group-hover:scale-110`}>
                    <Icon size={20} />
                  </div>
                  <div className="flex-1">
                    <div className={`font-semibold ${tier.color}`}>{tier.name}</div>
                  </div>
                  <div className={`font-bold text-lg ${tier.color}`}>{tier.range}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-[#722F37] rounded-3xl p-12 md:p-16 text-[#F7E7CE] relative overflow-hidden">
            <div className="absolute inset-0">
              <div className="absolute top-0 left-0 w-64 h-64 bg-white/5 rounded-full blur-3xl" />
              <div className="absolute bottom-0 right-0 w-64 h-64 bg-[#DAA520]/10 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10">
              <h2 className="font-serif-elegant text-4xl md:text-5xl font-bold mb-4">
                Ready to taste your code?
              </h2>
              <p className="text-lg opacity-80 mb-8 max-w-xl mx-auto">
                Join thousands of developers who trust Somm to evaluate their repositories.
              </p>
              <Link
                href="/evaluate"
                className="group inline-flex items-center gap-2 px-10 py-5 bg-[#F7E7CE] text-[#722F37] rounded-full font-semibold text-lg hover:bg-white transition-all hover:shadow-xl hover:scale-105"
              >
                Start Your Evaluation
                <ArrowRight className="w-6 h-6 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-[#722F37]/10 bg-white/30">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#722F37] flex items-center justify-center">
              <Wine className="w-4 h-4 text-[#F7E7CE]" />
            </div>
            <span className="font-serif-elegant text-lg font-bold text-[#722F37]">Somm</span>
          </div>

          <p className="text-sm text-gray-500">© 2025 Somm.dev — AI Code Sommelier</p>

          <div className="flex items-center gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-[#722F37] transition-colors">GitHub</a>
            <a href="#" className="hover:text-[#722F37] transition-colors">Twitter</a>
            <a href="#" className="hover:text-[#722F37] transition-colors">Discord</a>
          </div>
        </div>
      </footer>

      {/* CSS Animations */}
      <style jsx global>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out forwards;
        }
      `}</style>
    </div>
  );
}
