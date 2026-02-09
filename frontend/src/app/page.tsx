'use client';

import { useState, useEffect, useRef, useSyncExternalStore } from 'react';
import { Wine, Trophy, Medal, Award, Star, AlertTriangle, Sparkles, ArrowRight, Zap, FileText, Share2, ChevronDown, FolderGit, Code, Shield, Lightbulb, Wrench, ChevronRight, Users, Crown, Github } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { AnimatedSommeliers } from "@/components/ui/animated-sommeliers";

const sommeliers = [
  { id: "marcel", name: "Marcel", role: "Cellar Master", desc: "Structure & Metrics", color: "#8B7355", feature: "Analyzes repository architecture, file organization, and code metrics", icon: FolderGit },
  { id: "isabella", name: "Isabella", role: "Wine Critic", desc: "Code Quality", color: "#C41E3A", feature: "Evaluates readability, maintainability, and aesthetic code design", icon: Code },
  { id: "heinrich", name: "Heinrich", role: "Quality Inspector", desc: "Security & Testing", color: "#2F4F4F", feature: "Inspects test coverage, security vulnerabilities, and edge cases", icon: Shield },
  { id: "sofia", name: "Sofia", role: "Vineyard Scout", desc: "Innovation & Tech", color: "#DAA520", feature: "Discovers cutting-edge tech choices and architectural innovations", icon: Lightbulb },
  { id: "laurent", name: "Laurent", role: "Winemaker", desc: "Implementation", color: "#228B22", feature: "Reviews code craftsmanship, patterns, and implementation details", icon: Wrench },
  { id: "jeanpierre", name: "Jean-Pierre", role: "Grand Sommelier", desc: "Final Synthesis", color: "#4169E1", feature: "Synthesizes all evaluations into the final verdict and recommendations", icon: Trophy },
];

// Data for AnimatedSommeliers component
const sommelierTestimonials = [
  { name: "Marcel", role: "Cellar Master", focus: "Structure & Metrics", color: "#8B7355", src: "/sommeliers/marcel.png", quote: "A well-organized cellar reveals the soul of its maker. I examine the architecture, file organization, and code metrics to understand the structural integrity of your codebase." },
  { name: "Isabella", role: "Wine Critic", focus: "Code Quality", color: "#C41E3A", src: "/sommeliers/isabella.png", quote: "True elegance lies in readability and maintainability. I evaluate the aesthetic design of your code, seeking the perfect balance between complexity and clarity.", imagePosition: "center 20%" },
  { name: "Heinrich", role: "Quality Inspector", focus: "Security & Testing", color: "#2F4F4F", src: "/sommeliers/heinrich.png", quote: "Security is non-negotiable. I inspect test coverage, identify vulnerabilities, and ensure every edge case is handled with German precision." },
  { name: "Sofia", role: "Vineyard Scout", focus: "Innovation & Tech", color: "#DAA520", src: "/sommeliers/sofia.png", quote: "The best vineyards embrace innovation. I discover cutting-edge technologies and architectural patterns that set exceptional codebases apart." },
  { name: "Laurent", role: "Winemaker", focus: "Implementation", color: "#228B22", src: "/sommeliers/laurent.png", quote: "Craftsmanship is in the details. I review code patterns, implementation choices, and the artisanal care put into every function and module." },
  { name: "Jean-Pierre", role: "Grand Sommelier", focus: "Final Synthesis", color: "#4169E1", src: "/sommeliers/jeanpierre.png", quote: "After decades of tasting and evaluating, I synthesize all expert opinions into a single, authoritative verdict. The final score carries the weight of every sommelier's expertise combined." },
];

const criteriaModes = [
  { name: "Basic", desc: "General code review", bestFor: "Everyday projects", weight: "Balanced", featured: false, icon: "📋", features: ["Code structure", "Best practices", "Documentation"] },
  { name: "Hackathon", desc: "Gemini 3 judging criteria", bestFor: "Hackathon submissions", weight: "Tech 40%", featured: true, icon: "🏆", features: ["Technical impact", "Innovation", "Presentation", "Creativity"] },
  { name: "Academic", desc: "Research-focused evaluation", bestFor: "Research projects", weight: "Novelty", featured: false, icon: "🎓", features: ["Methodology", "Reproducibility", "Novelty"] },
  { name: "Custom", desc: "Define your own criteria", bestFor: "Special requirements", weight: "Flexible", featured: false, icon: "⚙️", features: ["Your criteria", "Custom weights", "Flexible scoring"] },
];

const scoringTiers = [
  { range: "95-100", name: "Legendary", icon: Trophy, opacity: 100, barWidth: "100%" },
  { range: "90-94", name: "Grand Cru", icon: Trophy, opacity: 85, barWidth: "90%" },
  { range: "85-89", name: "Premier Cru", icon: Medal, opacity: 70, barWidth: "80%" },
  { range: "80-84", name: "Village", icon: Award, opacity: 55, barWidth: "70%" },
  { range: "70-79", name: "Table Wine", icon: Star, opacity: 40, barWidth: "55%" },
  { range: "60-69", name: "House Wine", icon: Wine, opacity: 25, barWidth: "40%" },
  { range: "<60", name: "Corked", icon: AlertTriangle, opacity: 15, barWidth: "20%", isCorked: true },
];

// Initial positions for sommeliers (relative to center, in pixels)
const initialPositions = [
  { x: -120, y: -100 },  // Marcel - top left
  { x: 100, y: -120 },   // Isabella - top right  
  { x: 140, y: 20 },     // Heinrich - right
  { x: 80, y: 120 },     // Sofia - bottom right
  { x: -100, y: 100 },   // Laurent - bottom left
  { x: -140, y: 0 },     // Jean-Pierre - left
];

const sizes = [56, 64, 48, 56, 52, 96]; // radius for collision detection

const emptySubscribe = () => () => {};
const getMounted = () => true;
const getServerMounted = () => false;

export default function Home() {
  const [activeSommelier, setActiveSommelier] = useState<string | null>(null);
  const mounted = useSyncExternalStore(emptySubscribe, getMounted, getServerMounted);
  const [positions, setPositions] = useState(initialPositions);
  const [velocities] = useState(() => initialPositions.map(() => ({
    x: (Math.random() - 0.5) * 2,
    y: (Math.random() - 0.5) * 2,
  })));
  const velocitiesRef = useRef(velocities);

  useEffect(() => {
    const animate = () => {
      setPositions(prev => {
        const newPositions = [...prev];
        const velocities = velocitiesRef.current!;
        const bounds = { x: 180, y: 150 };
        
        // Update positions
        for (let i = 0; i < newPositions.length; i++) {
          newPositions[i] = {
            x: prev[i].x + velocities[i].x,
            y: prev[i].y + velocities[i].y,
          };
          
          // Bounce off boundaries
          if (Math.abs(newPositions[i].x) > bounds.x) {
            velocities[i].x *= -0.9;
            newPositions[i].x = Math.sign(newPositions[i].x) * bounds.x;
          }
          if (Math.abs(newPositions[i].y) > bounds.y) {
            velocities[i].y *= -0.9;
            newPositions[i].y = Math.sign(newPositions[i].y) * bounds.y;
          }
        }
        
        // Collision with CENTER WINE ICON (keep sommeliers away from center)
        const wineRadius = 100; // Wine icon protected zone (increased)
        for (let i = 0; i < newPositions.length; i++) {
          const dx = newPositions[i].x;
          const dy = newPositions[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const minDist = wineRadius + sizes[i] / 2;
          
          if (dist < minDist && dist > 0) {
            // Push away from center
            const nx = dx / dist;
            const ny = dy / dist;
            
            // Bounce off center
            const dotProduct = velocities[i].x * nx + velocities[i].y * ny;
            if (dotProduct < 0) {
              velocities[i].x -= 2 * dotProduct * nx;
              velocities[i].y -= 2 * dotProduct * ny;
            }
            
            // Push out of center zone
            newPositions[i].x = nx * minDist;
            newPositions[i].y = ny * minDist;
          }
        }
        
        // Collision detection between sommeliers
        for (let i = 0; i < newPositions.length; i++) {
          for (let j = i + 1; j < newPositions.length; j++) {
            const dx = newPositions[j].x - newPositions[i].x;
            const dy = newPositions[j].y - newPositions[i].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            const minDist = (sizes[i] + sizes[j]) / 2 + 10;
            
            if (dist < minDist && dist > 0) {
              // Normalize collision vector
              const nx = dx / dist;
              const ny = dy / dist;
              
              // Relative velocity
              const dvx = velocities[i].x - velocities[j].x;
              const dvy = velocities[i].y - velocities[j].y;
              const dvn = dvx * nx + dvy * ny;
              
              // Only resolve if objects are approaching
              if (dvn > 0) {
                const restitution = 0.8;
                const impulse = dvn * restitution;
                
                velocities[i].x -= impulse * nx * 0.5;
                velocities[i].y -= impulse * ny * 0.5;
                velocities[j].x += impulse * nx * 0.5;
                velocities[j].y += impulse * ny * 0.5;
              }
              
              // Separate overlapping objects
              const overlap = minDist - dist;
              newPositions[i].x -= overlap * nx * 0.5;
              newPositions[i].y -= overlap * ny * 0.5;
              newPositions[j].x += overlap * nx * 0.5;
              newPositions[j].y += overlap * ny * 0.5;
            }
          }
        }
        
        // Add slight random movement to keep things interesting
        for (let i = 0; i < velocities.length; i++) {
          velocities[i].x += (Math.random() - 0.5) * 0.1;
          velocities[i].y += (Math.random() - 0.5) * 0.1;
          // Damping
          velocities[i].x *= 0.995;
          velocities[i].y *= 0.995;
          // Minimum velocity
          const speed = Math.sqrt(velocities[i].x ** 2 + velocities[i].y ** 2);
          if (speed < 0.3) {
            velocities[i].x += (Math.random() - 0.5) * 0.5;
            velocities[i].y += (Math.random() - 0.5) * 0.5;
          }
        }
        
        return newPositions;
      });
    };
    
    const interval = setInterval(animate, 1000 / 60); // 60fps
    return () => clearInterval(interval);
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
          <Link href="/evaluate" className="px-4 py-2 bg-[#722F37] text-[#F7E7CE] rounded-full text-sm font-medium hover:bg-[#5A252C] transition-all hover:scale-105">
            Start Evaluation
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="relative z-10">
              {/* Enhanced Gemini Badge */}
              <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-[#DAA520]/20 to-[#FFD700]/20 border border-[#DAA520]/30 text-[#8B6914] text-sm font-semibold mb-6 shadow-lg shadow-[#DAA520]/10">
                <Sparkles className="w-5 h-5 text-[#DAA520] animate-pulse" />
                <span>Powered by Gemini 3</span>
                <span className="px-2 py-0.5 bg-[#DAA520] text-white text-xs rounded-full">NEW</span>
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
                <Link href="/evaluate" className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-[#722F37] text-[#F7E7CE] rounded-full font-semibold transition-all hover:bg-[#5A252C] hover:shadow-xl hover:shadow-[#722F37]/20 hover:scale-105">
                  Start Free Evaluation
                  <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                </Link>
                <Link href="/evaluate/6986e6d6650de8503772babf/result" className="inline-flex items-center justify-center gap-2 px-8 py-4 border-2 border-[#722F37]/20 text-[#722F37] rounded-full font-semibold hover:border-[#722F37] hover:bg-[#722F37]/5 transition-all hover:scale-105">
                  See Demo Result
                </Link>
              </div>

              <p className="mt-6 text-sm text-gray-500 flex items-center gap-4">
                <span>✨ Free for open source</span>
                <span>🔒 No signup required</span>
              </p>
            </div>

            {/* Right Content - Bouncing Sommelier Physics */}
            <div className="relative">
              <div className="relative h-[500px] md:h-[600px] flex items-center justify-center">
                {/* Center Wine Icon with Label & Tooltip */}
                <div 
                  className="absolute cursor-pointer group"
                  style={{ zIndex: activeSommelier === 'wine' ? 50 : 10 }}
                  onMouseEnter={() => setActiveSommelier('wine')}
                  onMouseLeave={() => setActiveSommelier(null)}
                >
                  <div className="w-20 h-20 rounded-full bg-[#722F37] flex items-center justify-center shadow-2xl transition-transform group-hover:scale-110">
                    <Wine className="w-9 h-9 text-[#F7E7CE]" />
                  </div>
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-[#722F37] text-[#F7E7CE] text-[9px] font-bold rounded-full shadow-lg whitespace-nowrap">
                    YOUR CODE
                  </div>
                  
                  {/* Tooltip */}
                  {activeSommelier === 'wine' && (
                    <div className="absolute -bottom-24 left-1/2 -translate-x-1/2 w-64 bg-white rounded-xl px-4 py-3 shadow-2xl border border-[#722F37] z-50">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-8 h-8 rounded-full bg-[#722F37]/10 flex items-center justify-center">
                          <Wine className="w-4 h-4 text-[#722F37]" />
                        </div>
                        <div>
                          <p className="font-semibold text-[#722F37]">Your Code</p>
                          <p className="text-xs text-gray-500">The Tasting Subject</p>
                        </div>
                      </div>
                      <p className="text-xs text-gray-600">The repository our sommeliers will taste and evaluate</p>
                    </div>
                  )}
                </div>

                {/* All 6 Sommeliers with physics-based bouncing */}
                {mounted && sommeliers.map((s, i) => {
                  const sizeClasses = [
                    'w-24 h-24 md:w-28 md:h-28',              // Marcel
                    'w-28 h-28 md:w-32 md:h-32',              // Isabella - bigger
                    'w-20 h-20 md:w-24 md:h-24',              // Heinrich - smaller
                    'w-24 h-24 md:w-28 md:h-28',              // Sofia
                    'w-[88px] h-[88px] md:w-[104px] md:h-[104px]', // Laurent
                    'w-36 h-36 md:w-48 md:h-48',              // Jean-Pierre - LARGEST
                  ];
                  const IconComponent = s.icon;
                  const isJeanPierre = s.id === 'jeanpierre';
                  const pos = positions[i];
                  
                  return (
                    <div
                      key={s.id}
                      className="absolute cursor-pointer transition-shadow duration-200"
                      style={{
                        transform: `translate(${pos.x}px, ${pos.y}px)`,
                        zIndex: activeSommelier === s.id ? 30 : isJeanPierre ? 25 : 20,
                      }}
                      onMouseEnter={() => setActiveSommelier(s.id)}
                      onMouseLeave={() => setActiveSommelier(null)}
                    >
                      <div className={sizeClasses[i] + " rounded-full overflow-hidden border-4 border-white shadow-xl transition-all duration-200 relative " + (activeSommelier === s.id ? 'scale-110 shadow-2xl' : '') + (isJeanPierre ? ' ring-4 ring-[#DAA520] ring-offset-2' : '')}
                        style={{ 
                          boxShadow: activeSommelier === s.id ? '0 25px 50px -12px ' + s.color + '40' : isJeanPierre ? '0 20px 40px -10px rgba(65, 105, 225, 0.4)' : undefined,
                        }}
                      >
                        <Image src={"/sommeliers/" + s.id + ".png"} alt={s.name} fill className="object-cover object-top" priority={isJeanPierre} />
                      </div>
                      
                      {/* MASTER badge for Jean-Pierre */}
                      {isJeanPierre && (
                        <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 px-2.5 py-0.5 bg-[#DAA520] text-white text-[10px] font-bold rounded-full shadow-lg">
                          MASTER
                        </div>
                      )}
                      
                      {/* Hover Tooltip */}
                      {activeSommelier === s.id && (
                        <div className={"absolute -bottom-24 left-1/2 -translate-x-1/2 bg-white rounded-xl px-3 py-2 shadow-2xl border z-50 " + (isJeanPierre ? 'w-64 border-[#DAA520]' : 'w-56 border-gray-100')}>
                          <div className="flex items-center gap-2 mb-1">
                            <div className="w-7 h-7 rounded-full flex items-center justify-center" style={{ backgroundColor: s.color + '20' }}>
                              <IconComponent className="w-3.5 h-3.5" style={{ color: s.color }} />
                            </div>
                            <div>
                              <p className="font-semibold text-sm text-[#722F37]">{s.name}</p>
                              <p className="text-xs text-gray-500">{s.role}</p>
                            </div>
                            {isJeanPierre && (
                              <span className="text-[9px] px-1.5 py-0.5 bg-[#DAA520] text-white rounded-full">MASTER</span>
                            )}
                          </div>
                          <p className="text-xs text-gray-600">{s.desc}</p>
                        </div>
                      )}
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

      {/* Result Preview Section */}
      <section className="py-16 px-6 bg-gradient-to-b from-[#FAF4E8] to-white/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="font-serif-elegant text-3xl font-bold text-[#722F37] mb-3">
              See What You Get
            </h2>
            <p className="text-gray-600">A comprehensive evaluation report with actionable insights</p>
          </div>
          
          {/* Real Result Card - ai/nanoid evaluation */}
          <div className="bg-white rounded-2xl shadow-xl border border-[#722F37]/10 overflow-hidden">
            <div className="bg-gradient-to-r from-[#722F37] to-[#5A252C] p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-80">Repository Evaluation</p>
                  <p className="text-xl font-bold">ai/nanoid</p>
                </div>
                <div className="text-right">
                  <p className="text-sm opacity-80">Final Score</p>
                  <p className="text-4xl font-bold text-[#DAA520]">97<span className="text-lg text-[#DAA520]/60">/100</span></p>
                </div>
              </div>
            </div>
            <div className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <Trophy className="w-5 h-5 text-yellow-500" />
                <span className="font-semibold text-[#722F37]">Legendary</span>
                <span className="text-sm text-gray-500">— Exceptional quality codebase</span>
              </div>
              <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
                {sommeliers.map((s, i) => {
                  const scores = [96, 98, 96, 96, 98, 97];
                  const isTop = scores[i] === 98;
                  return (
                    <div key={s.id} className="text-center p-3 bg-gray-50 rounded-xl relative">
                      {isTop && <span className="absolute -top-1 -right-1 inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded-full font-semibold"><Crown size={10} />TOP</span>}
                      <div className="w-20 h-20 mx-auto mb-2 rounded-full overflow-hidden border-2 border-white shadow-md relative">
                        <Image src={"/sommeliers/" + s.id + ".png"} alt={s.name} fill className="object-cover object-top" />
                      </div>
                      <p className="text-sm text-gray-700 font-medium">{s.name.split(' ')[0]}</p>
                      <p className="text-xl font-bold text-[#722F37]">{scores[i]}</p>
                    </div>
                  );
                })}
              </div>
              <p className="text-center text-xs text-gray-400 mt-4">* Real evaluation of ai/nanoid repository</p>
              <div className="mt-4 flex justify-center">
                <Link href="/evaluate/6986e6d6650de8503772babf/result" className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#722F37]/5 text-[#722F37] font-semibold rounded-full hover:bg-[#722F37]/10 transition-colors">
                  View Full Demo Report <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - Enhanced */}
      <section id="how-it-works" className="py-24 px-6 bg-gradient-to-b from-white/50 to-[#FAF4E8]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">How It Works</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">Like a master sommelier orchestrates a tasting panel, our AI agents analyze your code in parallel.</p>
          </div>

          <div className="flex flex-col md:flex-row items-stretch gap-4 md:gap-0">
            {/* Step 1 */}
            <div className="flex items-center flex-1">
              <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/10 h-full transition-all hover:shadow-lg hover:border-[#722F37]/20 hover:-translate-y-1 flex-1 group">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-[#722F37] text-[#F7E7CE] flex items-center justify-center text-xl font-bold">
                    1
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-[#722F37]/10 flex items-center justify-center group-hover:bg-[#722F37]/20 transition-colors">
                    <FolderGit className="w-6 h-6 text-[#722F37]" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-[#722F37] mb-3">Submit Repository</h3>
                <p className="text-gray-600 mb-4">Connect your GitHub repository or paste any public repo URL</p>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Code className="w-4 h-4" />
                  <span>Public or private repos</span>
                </div>
              </div>
              <div className="hidden md:flex items-center justify-center w-12 flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-[#722F37]/10 flex items-center justify-center">
                  <ChevronRight className="w-5 h-5 text-[#722F37]" />
                </div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex items-center flex-1">
              <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/10 h-full transition-all hover:shadow-lg hover:border-[#722F37]/20 hover:-translate-y-1 flex-1 group">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-[#722F37] text-[#F7E7CE] flex items-center justify-center text-xl font-bold">
                    2
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-[#722F37]/10 flex items-center justify-center group-hover:bg-[#722F37]/20 transition-colors">
                    <Users className="w-6 h-6 text-[#722F37]" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-[#722F37] mb-3">Parallel Analysis</h3>
                <p className="text-gray-600 mb-4">Six specialized sommeliers evaluate simultaneously</p>
                {/* Sommelier Avatars */}
                <div className="flex -space-x-2">
                  {['marcel', 'isabella', 'heinrich', 'sofia', 'laurent'].map((id) => (
                    <div key={id} className="w-10 h-10 rounded-full overflow-hidden border-2 border-white shadow-sm">
                      <Image src={"/sommeliers/" + id + ".png"} alt={id} width={40} height={40} className="object-cover object-top" />
                    </div>
                  ))}
                  <div className="w-10 h-10 rounded-full bg-[#DAA520] border-2 border-white shadow-sm flex items-center justify-center">
                    <span className="text-white text-xs font-bold">+1</span>
                  </div>
                </div>
              </div>
              <div className="hidden md:flex items-center justify-center w-12 flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-[#722F37]/10 flex items-center justify-center">
                  <ChevronRight className="w-5 h-5 text-[#722F37]" />
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex items-center flex-1">
              <div className="bg-gradient-to-br from-[#722F37] to-[#5A252C] rounded-2xl p-8 shadow-lg h-full transition-all hover:shadow-xl hover:-translate-y-1 flex-1 group text-white">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center text-xl font-bold">
                    3
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center group-hover:bg-white/20 transition-colors">
                    <Trophy className="w-6 h-6 text-[#DAA520]" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold mb-3">Get Verdict</h3>
                <p className="text-white/80 mb-4">Jean-Pierre synthesizes all findings into actionable insights</p>
                {/* Jean-Pierre Avatar */}
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-[#DAA520] shadow-lg">
                    <Image src="/sommeliers/jeanpierre.png" alt="Jean-Pierre" width={40} height={40} className="object-cover object-top" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">Jean-Pierre</p>
                    <p className="text-xs text-white/60">Grand Sommelier</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features - Bento Style */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Features</h2>
            <p className="text-gray-600">Everything you need for comprehensive code evaluation</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Featured - Real-time Streaming */}
            <div className="group lg:col-span-2 bg-gradient-to-br from-[#722F37] to-[#5A252C] rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 text-white relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Zap className="w-7 h-7 text-[#F7E7CE]" />
                  </div>
                  <span className="px-3 py-1 bg-[#DAA520] text-white text-xs font-bold rounded-full">LIVE</span>
                </div>
                <h3 className="text-2xl font-bold mb-3">Real-time Streaming</h3>
                <p className="text-white/80 text-lg mb-4">Watch evaluations unfold live with Server-Sent Events streaming. See each sommelier&apos;s analysis as it happens.</p>
                <div className="flex items-center gap-4 text-sm text-white/60">
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" /> Live updates</span>
                  <span>• No page refresh</span>
                </div>
              </div>
            </div>

            {/* PDF Reports */}
            <div className="group bg-white rounded-2xl p-6 shadow-sm border border-[#722F37]/10 hover:shadow-lg hover:border-[#722F37]/20 transition-all hover:-translate-y-1">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-100 to-orange-100 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <FileText className="w-6 h-6 text-red-500" />
              </div>
              <h3 className="font-bold text-[#722F37] mb-2 text-lg">PDF Reports</h3>
              <p className="text-gray-600 text-sm">Export professional tasting notes as beautifully formatted PDF reports.</p>
            </div>

            {/* One-Click Share */}
            <div className="group bg-white rounded-2xl p-6 shadow-sm border border-[#722F37]/10 hover:shadow-lg hover:border-[#722F37]/20 transition-all hover:-translate-y-1">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-100 to-cyan-100 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Share2 className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="font-bold text-[#722F37] mb-2 text-lg">One-Click Share</h3>
              <p className="text-gray-600 text-sm">Share results with your team instantly via link or social media.</p>
            </div>

            {/* 4 Eval Modes */}
            <div className="group lg:col-span-2 bg-gradient-to-br from-[#FAF4E8] to-white rounded-2xl p-6 shadow-sm border border-[#DAA520]/20 hover:shadow-lg hover:border-[#DAA520]/40 transition-all hover:-translate-y-1">
              <div className="flex items-start gap-6">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-[#DAA520]/20 to-[#FFD700]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                  <Sparkles className="w-7 h-7 text-[#DAA520]" />
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-[#722F37] mb-2 text-lg">4 Evaluation Modes</h3>
                  <p className="text-gray-600 text-sm mb-4">Choose the perfect evaluation style for your needs.</p>
                  <div className="flex flex-wrap gap-2">
                    {['Basic', 'Hackathon', 'Academic', 'Custom'].map((mode, i) => (
                      <span key={mode} className={"px-3 py-1.5 rounded-full text-xs font-medium " + (i === 1 ? 'bg-[#DAA520] text-white' : 'bg-white border border-gray-200 text-gray-600')}>
                        {i === 1 && '🏆 '}{mode}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mid-page CTA */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="bg-gradient-to-br from-[#722F37] to-[#5A252C] rounded-3xl p-10 md:p-12 relative overflow-hidden">
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-72 h-72 bg-[#DAA520]/10 rounded-full -translate-y-1/2 translate-x-1/3" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/4" />
            <div className="absolute top-1/2 right-1/4 w-24 h-24 bg-[#DAA520]/5 rounded-full" />
            
            <div className="relative flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="text-center md:text-left">
                <h3 className="text-3xl md:text-4xl font-serif-elegant font-bold text-white mb-3">Ready to evaluate your code?</h3>
                <p className="text-white/80 text-lg mb-4">Get detailed insights from six AI sommelier agents in minutes.</p>
                <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm text-white/60">
                  <span className="flex items-center gap-2"><span className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center"><span className="w-2 h-2 rounded-full bg-green-400" /></span> Free for open source</span>
                  <span className="flex items-center gap-2"><span className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center"><span className="w-2 h-2 rounded-full bg-blue-400" /></span> No signup required</span>
                </div>
              </div>
              <div className="flex flex-col items-center gap-3">
                <Link href="/evaluate" className="inline-flex items-center gap-2 px-8 py-4 bg-[#DAA520] text-white rounded-full font-bold text-lg hover:bg-[#C9A227] transition-all hover:scale-105 shadow-lg shadow-black/20 whitespace-nowrap">
                  Try It Now <ArrowRight className="w-5 h-5" />
                </Link>
                <span className="text-white/40 text-sm">Takes less than 2 minutes</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Evaluation Modes - Hackathon Highlighted */}
      <section className="py-24 px-6 bg-gradient-to-b from-white/50 to-[#FAF4E8]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Evaluation Modes</h2>
            <p className="text-gray-600">Choose the criteria that fits your needs</p>
          </div>
          
          {/* Hackathon Featured - Large Card */}
          <div className="mb-8">
            <div className="bg-gradient-to-br from-[#DAA520]/20 via-[#FFD700]/10 to-[#DAA520]/5 rounded-2xl p-8 border-2 border-[#DAA520]/40 relative overflow-hidden group hover:shadow-xl transition-all">
              <div className="absolute top-0 right-0 w-64 h-64 bg-[#DAA520]/10 rounded-full -translate-y-1/2 translate-x-1/2" />
              <div className="relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                <div className="flex-1">
                  <div className="flex items-center gap-4 mb-4">
                    <span className="text-4xl">🏆</span>
                    <div>
                      <div className="flex items-center gap-3">
                        <h3 className="text-2xl font-bold text-[#722F37]">Hackathon Mode</h3>
                        <span className="px-3 py-1 bg-[#DAA520] text-white text-xs font-bold rounded-full flex items-center gap-1 animate-pulse">
                          <Sparkles className="w-3 h-3" /> RECOMMENDED
                        </span>
                      </div>
                      <p className="text-[#722F37]/70">Gemini 3 judging criteria • Best for hackathon submissions</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {['Gemini judging focus', 'Innovation & Impact', 'Technical creativity', 'Demo-ready polish'].map((item) => (
                      <span key={item} className="px-3 py-1.5 bg-white/80 border border-[#DAA520]/30 rounded-full text-sm text-[#722F37] font-medium">
                        ✓ {item}
                      </span>
                    ))}
                  </div>
                </div>
                <Link href="/evaluate" className="inline-flex items-center gap-2 px-6 py-3 bg-[#DAA520] text-white rounded-full font-bold hover:bg-[#C9A227] transition-all hover:scale-105 shadow-lg whitespace-nowrap">
                  Use This Mode <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>

          {/* Other Modes - 3 Column Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            {criteriaModes.filter(m => !m.featured).map((mode) => (
              <div key={mode.name} className="bg-white rounded-xl p-6 border border-[#722F37]/10 transition-all group hover:shadow-lg hover:-translate-y-1 hover:border-[#722F37]/30">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">{mode.icon}</span>
                  <div>
                    <h3 className="font-bold text-[#722F37] text-lg">{mode.name}</h3>
                    <span className="text-xs text-[#722F37]/50">{mode.weight}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-4">{mode.desc}</p>
                <div className="space-y-2">
                  {mode.features.map((feature) => (
                    <div key={feature} className="flex items-center gap-2 text-sm text-gray-500">
                      <span className="w-4 h-4 rounded-full bg-[#722F37]/10 flex items-center justify-center text-[10px] text-[#722F37]">✓</span>
                      {feature}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-[#722F37]/40 mt-4 pt-4 border-t border-gray-100">Best for: {mode.bestFor}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Meet Your Sommeliers */}
      <section id="sommeliers" className="py-24 px-6 bg-gradient-to-b from-[#FAF4E8] to-white">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Meet Your Sommeliers</h2>
            <p className="text-gray-600">Six AI experts, each with a unique perspective on code quality</p>
          </div>

          {/* Animated Sommeliers Carousel - All 6 */}
          <AnimatedSommeliers sommeliers={sommelierTestimonials} autoplay={true} />
        </div>
      </section>

      {/* Scoring System */}
      <section className="py-24 px-6 bg-white/50">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="font-serif-elegant text-4xl font-bold text-[#722F37] mb-4">Scoring System</h2>
            <p className="text-gray-600">From legendary cellars to house wines — every codebase has its place</p>
          </div>
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#722F37]/10">
            <div className="space-y-4">
              {scoringTiers.map((tier) => {
                const Icon = tier.icon;
                const isCorked = (tier as { isCorked?: boolean }).isCorked;
                return (
                  <div key={tier.name} className="group">
                    <div className="flex items-center gap-4 mb-2">
                      <div 
                        className="w-8 h-8 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110"
                        style={{ 
                          backgroundColor: isCorked ? '#fee2e2' : `rgba(114, 47, 55, ${tier.opacity / 100})`,
                          color: isCorked ? '#dc2626' : tier.opacity > 50 ? '#F7E7CE' : '#722F37'
                        }}
                      >
                        <Icon size={16} />
                      </div>
                      <span 
                        className="font-semibold w-28"
                        style={{ color: isCorked ? '#dc2626' : '#722F37' }}
                      >
                        {tier.name}
                      </span>
                      <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full transition-all duration-500"
                          style={{ 
                            width: tier.barWidth,
                            backgroundColor: isCorked ? '#fca5a5' : `rgba(114, 47, 55, ${tier.opacity / 100 + 0.2})`
                          }}
                        />
                      </div>
                      <span 
                        className="font-bold text-sm w-16 text-right"
                        style={{ color: isCorked ? '#dc2626' : '#722F37' }}
                      >
                        {tier.range}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-8 pt-6 border-t border-gray-100 flex items-center justify-center gap-8 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-[#722F37]" />
                <span>Exceptional</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-[#722F37]/50" />
                <span>Good</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-[#722F37]/20" />
                <span>Basic</span>
              </div>
            </div>
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
              <h2 className="font-serif-elegant text-4xl md:text-5xl font-bold mb-4">Ready to taste your code?</h2>
              <p className="text-lg opacity-80 mb-8 max-w-xl mx-auto">Get comprehensive insights from six AI sommeliers in minutes.</p>
              <Link href="/evaluate" className="group inline-flex items-center gap-2 px-10 py-5 bg-[#F7E7CE] text-[#722F37] rounded-full font-semibold text-lg hover:bg-white transition-all hover:shadow-xl hover:scale-105">
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

          <p className="text-sm text-gray-500">© 2026 Somm.dev — AI Code Sommelier</p>

          <a 
            href="https://github.com/sgwannabe/somm.dev" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#722F37] transition-colors"
          >
            <Github className="w-5 h-5" />
            <span>GitHub</span>
          </a>
        </div>
      </footer>

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
