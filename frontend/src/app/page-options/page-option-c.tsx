'use client';

import { useEffect, useRef, useState } from 'react';
import { Wine, Trophy, Medal, Award, Star, AlertTriangle, Sparkles, ArrowRight, Zap, FileText, Share2, ChevronDown, Play, Pause } from "lucide-react";
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

const scoringTiers = [
  { range: "95-100", name: "Legendary", icon: Trophy, color: "text-yellow-600", bg: "from-yellow-100/80 to-amber-100/80" },
  { range: "90-94", name: "Grand Cru", icon: Trophy, color: "text-amber-600", bg: "from-amber-100/80 to-yellow-100/80" },
  { range: "85-89", name: "Premier Cru", icon: Medal, color: "text-orange-600", bg: "from-orange-100/80 to-amber-100/80" },
  { range: "80-84", name: "Village", icon: Award, color: "text-emerald-600", bg: "from-emerald-100/80 to-green-100/80" },
  { range: "70-79", name: "Table Wine", icon: Star, color: "text-blue-600", bg: "from-blue-100/80 to-sky-100/80" },
  { range: "60-69", name: "House Wine", icon: Wine, color: "text-purple-600", bg: "from-purple-100/80 to-violet-100/80" },
  { range: "<60", name: "Corked", icon: AlertTriangle, color: "text-red-600", bg: "from-red-100/80 to-rose-100/80" },
];

// Animated Counter Component
function AnimatedCounter({ target, duration = 2000 }: { target: number; duration?: number }) {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.5 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      // Easing function
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeOutQuart * target));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrame);
  }, [isVisible, target, duration]);

  return <span ref={ref}>{count}</span>;
}

// Scroll Reveal Component
function ScrollReveal({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      }`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

export default function Home() {
  const [activeSommelier, setActiveSommelier] = useState<string | null>(null);
  const [demoScore, setDemoScore] = useState(87);

  return (
    <div className="min-h-screen bg-[#FAF4E8] overflow-x-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-[#722F37]/5 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-[#DAA520]/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#F7E7CE]/50 rounded-full blur-[150px]" />
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
            {['How It Works', 'Features', 'Sommeliers'].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase().replace(/\s+/g, '-')}`}
                className="hover:text-[#722F37] transition-colors relative group"
              >
                {item}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-[#722F37] transition-all group-hover:w-full" />
              </a>
            ))}
          </div>

          <Link
            href="/evaluate"
            className="px-5 py-2.5 bg-[#722F37] text-[#F7E7CE] rounded-full text-sm font-semibold hover:bg-[#5A252C] transition-all hover:shadow-lg hover:shadow-[#722F37]/25 hover:scale-105"
          >
            Start Evaluation
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen pt-32 pb-20 px-6 flex items-center">
        <div className="max-w-7xl mx-auto w-full">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Content */}
            <div className="relative z-10">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#722F37]/10 text-[#722F37] text-sm font-medium mb-6 animate-fadeIn"
              >
                <Sparkles className="w-4 h-4 animate-pulse" />
                <span>Now with Gemini 3</span>
              </div>

              <h1 className="font-serif-elegant text-5xl md:text-6xl lg:text-7xl font-bold text-[#722F37] leading-[1.05] mb-6"
              >
                <span className="inline-block animate-fadeIn" style={{ animationDelay: '100ms' }}>
                  AI Code
                </span>
                <br />
                <span className="inline-block italic font-normal animate-fadeIn" style={{ animationDelay: '200ms' }}>
                  Evaluation
                </span>
                <br />
                <span className="inline-block animate-fadeIn" style={{ animationDelay: '300ms' }}>
                  with
                </span>{' '}
                <span className="inline-block animate-fadeIn" style={{ animationDelay: '400ms' }}>
                  Sommelier
                </span>
                <br />
                <span className="inline-block text-[#722F37]/60 animate-fadeIn" style={{ animationDelay: '500ms' }}>
                  Sophistication
                </span>
              </h1>

              <p className="text-lg text-gray-600 mb-8 max-w-lg leading-relaxed animate-fadeIn" style={{ animationDelay: '600ms' }}>
                Six specialized AI agents analyze your repositories from every angle—
                structure, quality, security, and innovation.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 animate-fadeIn" style={{ animationDelay: '700ms' }}>
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
                  <Play className="w-4 h-4" />
                  See Demo
                </Link>
              </div>

              <p className="mt-6 text-sm text-gray-500 animate-fadeIn" style={{ animationDelay: '800ms' }}>
                Free for open source • No signup required
              </p>
            </div>

            {/* Right Content - Interactive Sommelier Grid */}
            <div className="relative">
              <div className="relative h-[550px] md:h-[600px]">
                {sommeliers.map((s, i) => {
                  const positions = [
                    { top: '10%', left: '10%' },
                    { top: '5%', right: '20%' },
                    { top: '35%', right: '5%' },
                    { bottom: '20%', right: '15%' },
                    { bottom: '10%', left: '20%' },
                    { top: '40%', left: '5%' },
                  ];
                  
                  return (
                    <div
                      key={s.id}
                      className="absolute cursor-pointer group"
                      style={{
                        ...positions[i],
                        zIndex: activeSommelier === s.id ? 30 : 20 - i,
                        animationDelay: `${i * 100}ms`,
                      }}
                      onMouseEnter={() => setActiveSommelier(s.id)}
                      onMouseLeave={() => setActiveSommelier(null)}
                    >
                      <div
                        className={`relative w-24 h-24 md:w-28 md:h-28 rounded-full overflow-hidden border-4 border-white shadow-xl transition-all duration-500 ${
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
                          priority={i < 3}
                        />
                      </div>

                      {/* Tooltip */}
                      <div
                        className={`absolute -bottom-16 left-1/2 -translate-x-1/2 whitespace-nowrap transition-all duration-300 ${
                          activeSommelier === s.id ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2 pointer-events-none'
                        }`}
                      >
                        <div className="bg-white rounded-lg px-4 py-2 shadow-xl border border-gray-100">
                          <p className="font-semibold text-[#722F37]">{s.name}</p>
                          <p className="text-xs text-gray-500">{s.role}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Center Badge */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
                  <div className="w-32 h-32 rounded-full bg-[#722F37] flex items-center justify-center shadow-2xl animate-pulse">
                    <Wine className="w-12 h-12 text-[#F7E7CE]" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-6 h-6 text-[#722F37]/40" />
        </div>
      </section>

      {/* Live Demo Score */}
      <section className="py-20 px-6">
        <ScrollReveal>
          <div className="max-w-4xl mx-auto">
            <div className="bg-gradient-to-br from-[#722F37] to-[#5A252C] rounded-3xl p-8 md:p-12 text-[#F7E7CE] text-center relative overflow-hidden">
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-0 left-0 w-full h-full" style={{
                  backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.15) 1px, transparent 0)',
                  backgroundSize: '40px 40px'
                }} />
              </div>

              <div className="relative z-10">
                <p className="text-sm uppercase tracking-widest opacity-70 mb-4">Sample Evaluation</p>
                <div className="text-7xl md:text-8xl font-bold mb-4">
                  <AnimatedCounter target={demoScore} />
                  <span className="text-3xl opacity-50">/100</span>
                </div>

                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur mb-6">
                  <Medal className="w-5 h-5 text-orange-300" />
                  <span className="font-semibold">Premier Cru</span>
                </div>

                <p className="text-lg opacity-80 max-w-xl mx-auto">
                  "Excellent code structure with strong testing practices. Minor improvements in documentation would elevate this to Grand Cru status."
                </p>
              </div>
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* How It Works - Animated Pipeline */}
      <section id="how-it-works" className="py-24 px-6 bg-white/30">
        <div className="max-w-6xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">
                How It Works
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Like a master sommelier tasting panel, our AI agents work in parallel
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: 1, title: "Submit Repository", desc: "Connect your GitHub repo or paste any public URL" },
              { step: 2, title: "Parallel Analysis", desc: "Six sommeliers evaluate simultaneously" },
              { step: 3, title: "Get Verdict", desc: "Receive detailed tasting notes and recommendations" },
            ].map((item, i) => (
              <ScrollReveal key={item.step} delay={i * 150}>
                <div className="relative group">
                  <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/5 h-full transition-all hover:shadow-lg hover:border-[#722F37]/20 hover:-translate-y-1">
                    <div className="w-14 h-14 rounded-2xl bg-[#722F37] text-[#F7E7CE] flex items-center justify-center text-2xl font-bold mb-6 transition-transform group-hover:scale-110">
                      {item.step}
                    </div>
                    <h3 className="text-xl font-semibold text-[#722F37] mb-3">{item.title}</h3>
                    <p className="text-gray-600">{item.desc}</p>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Features</h2>
              <p className="text-gray-600">Everything you need for comprehensive code evaluation</p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Zap, title: "Real-time Streaming", desc: "Watch evaluations unfold live" },
              { icon: FileText, title: "PDF Reports", desc: "Export professional tasting notes" },
              { icon: Share2, title: "One-Click Share", desc: "Share results instantly" },
              { icon: Trophy, title: "4 Eval Modes", desc: "Basic, Hackathon, Academic, Custom" },
            ].map((feature, i) => (
              <ScrollReveal key={feature.title} delay={i * 100}>
                <div className="group bg-white rounded-xl p-6 shadow-sm border border-[#722F37]/5 hover:shadow-md hover:border-[#722F37]/20 transition-all hover:-translate-y-1">
                  <div className="w-12 h-12 rounded-lg bg-[#722F37]/10 flex items-center justify-center mb-4 transition-colors group-hover:bg-[#722F37]">
                    <feature.icon className="w-6 h-6 text-[#722F37] group-hover:text-[#F7E7CE] transition-colors" />
                  </div>
                  <h3 className="font-semibold text-[#722F37] mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-600">{feature.desc}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Meet Your Sommeliers - Interactive */}
      <section id="sommeliers" className="py-24 px-6 bg-white/30">
        <div className="max-w-6xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Meet Your Sommeliers</h2>
              <p className="text-gray-600">Six AI experts, each with a unique perspective</p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sommeliers.map((s, i) => (
              <ScrollReveal key={s.id} delay={i * 100}>
                <div
                  className="group bg-white rounded-xl overflow-hidden shadow-sm border border-[#722F37]/5 hover:shadow-xl transition-all cursor-pointer"
                  onClick={() => setActiveSommelier(activeSommelier === s.id ? null : s.id)}
                >
                  <div className="h-28 relative overflow-hidden" style={{ backgroundColor: s.color }}>
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
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-[#722F37] text-lg">{s.name}</h3>
                      <div className={`transition-transform duration-300 ${activeSommelier === s.id ? 'rotate-180' : ''}`}>
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      </div>
                    </div>
                    <p className="text-sm font-medium" style={{ color: s.color }}>{s.role}</p>
                    <div
                      className={`overflow-hidden transition-all duration-300 ${
                        activeSommelier === s.id ? 'max-h-20 opacity-100 mt-3' : 'max-h-0 opacity-0'
                      }`}
                    >
                      <p className="text-sm text-gray-600">{s.desc}</p>
                    </div>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Scoring System */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Scoring System</h2>
              <p className="text-gray-600">From legendary cellars to house wines</p>
            </div>
          </ScrollReveal>

          <div className="space-y-3">
            {scoringTiers.map((tier, i) => {
              const Icon = tier.icon;
              return (
                <ScrollReveal key={tier.name} delay={i * 50}>
                  <div
                    className={`flex items-center gap-4 p-4 rounded-xl bg-gradient-to-r ${tier.bg} border border-transparent hover:border-[#722F37]/20 transition-all cursor-default group`}
                  >
                    <div className={`w-12 h-12 rounded-xl bg-white/80 flex items-center justify-center ${tier.color} transition-transform group-hover:scale-110`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <div className={"font-semibold text-lg " + tier.color}>{tier.name}</div>
                    </div>
                      <div className={"font-bold text-2xl " + tier.color}>{tier.range}</div>
                  </div>
                </ScrollReveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <ScrollReveal>
          <div className="max-w-4xl mx-auto">
            <div className="bg-gradient-to-br from-[#722F37] to-[#5A252C] rounded-3xl p-12 md:p-16 text-center text-[#F7E7CE] relative overflow-hidden">
              <div className="absolute inset-0">
                <div className="absolute top-0 left-0 w-64 h-64 bg-white/5 rounded-full blur-3xl" />
                <div className="absolute bottom-0 right-0 w-64 h-64 bg-[#DAA520]/10 rounded-full blur-3xl" />
              </div>

              <div className="relative z-10">
                <h2 className="font-serif-elegant text-4xl md:text-5xl font-bold mb-4">Ready to taste your code?</h2>
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
        </ScrollReveal>
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
            {['GitHub', 'Twitter', 'Discord'].map((link) => (
              <a key={link} href="#" className="hover:text-[#722F37] transition-colors">{link}</a>
            ))}
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
          opacity: 0;
        }
      `}</style>
    </div>
  );
}
