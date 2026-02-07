'use client';

import { useState, useEffect, useRef } from 'react';
import { Wine, ArrowRight, FolderGit, Code, Shield, Lightbulb, Wrench, Trophy } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

const sommeliers = [
  { id: "marcel", name: "Marcel", color: "#8B7355", icon: FolderGit, orbit: { radius: 160, speed: 60, offset: 0 } },
  { id: "isabella", name: "Isabella", color: "#C41E3A", icon: Code, orbit: { radius: 170, speed: 55, offset: 72 } },
  { id: "heinrich", name: "Heinrich", color: "#2F4F4F", icon: Shield, orbit: { radius: 150, speed: 70, offset: 144 } },
  { id: "sofia", name: "Sofia", color: "#DAA520", icon: Lightbulb, orbit: { radius: 180, speed: 50, offset: 216 } },
  { id: "laurent", name: "Laurent", color: "#228B22", icon: Wrench, orbit: { radius: 155, speed: 65, offset: 288 } },
  { id: "jeanpierre", name: "Jean-Pierre", color: "#4169E1", icon: Trophy, orbit: null },
];

export default function Home() {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [time, setTime] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let animationId: number;
    const animate = () => {
      setTime(t => t + 0.016);
      animationId = requestAnimationFrame(animate);
    };
    animate();
    return () => cancelAnimationFrame(animationId);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        setMousePos({
          x: (e.clientX - rect.left - rect.width / 2) / (rect.width / 2),
          y: (e.clientY - rect.top - rect.height / 2) / (rect.height / 2),
        });
      }
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const getPosition = (s: typeof sommeliers[0], index: number) => {
    if (s.id === 'jeanpierre') {
      // Center with parallax
      return {
        x: mousePos.x * -30,
        y: mousePos.y * -30,
        scale: 1 + Math.sin(time * 2) * 0.03, // Breathing
      };
    }

    const orbit = s.orbit!;
    const angle = (time * (360 / orbit.speed)) + orbit.offset;
    const rad = (angle * Math.PI) / 180;
    
    // Orbital position
    let x = Math.cos(rad) * orbit.radius;
    let y = Math.sin(rad) * orbit.radius;
    
    // Add drift
    x += Math.sin(time * 3 + index) * 8;
    y += Math.cos(time * 2.5 + index) * 6;
    
    // Mouse parallax
    x += mousePos.x * (20 + index * 3);
    y += mousePos.y * (20 + index * 3);
    
    // Magnetic to hovered
    if (hoveredId && hoveredId !== s.id) {
      const hovered = sommeliers.findIndex(so => so.id === hoveredId);
      if (hovered !== -1 && hovered !== 5) {
        const hoveredAngle = (time * (360 / sommeliers[hovered].orbit!.speed)) + sommeliers[hovered].orbit!.offset;
        const hoveredRad = (hoveredAngle * Math.PI) / 180;
        const hx = Math.cos(hoveredRad) * sommeliers[hovered].orbit!.radius;
        const hy = Math.sin(hoveredRad) * sommeliers[hovered].orbit!.radius;
        x += (hx - x) * 0.15;
        y += (hy - y) * 0.15;
      }
    }
    
    return { x, y, scale: 1 };
  };

  return (
    <div className="min-h-screen bg-[#FAF4E8] overflow-x-hidden">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#FAF4E8]/80 backdrop-blur-md border-b border-[#722F37]/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#722F37]"><Wine className="w-4 h-4 text-[#F7E7CE] m-2" /></div>
            <span className="font-serif-elegant text-xl font-bold text-[#722F37]">Somm</span>
          </Link>
          <Link href="/evaluate" className="px-4 py-2 bg-[#722F37] text-[#F7E7CE] rounded-full">Start</Link>
        </div>
      </nav>

      <section className="relative min-h-screen pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="font-serif-elegant text-5xl md:text-7xl font-bold text-[#722F37] mb-6">
                AI Code<br /><span className="italic">Evaluation</span>
              </h1>
              <p className="text-lg text-gray-600 mb-8">Six AI sommeliers analyze your code</p>
              <Link href="/evaluate" className="inline-flex items-center gap-2 px-8 py-4 bg-[#722F37] text-[#F7E7CE] rounded-full font-semibold hover:scale-105 transition-transform">
                Start Free Evaluation <ArrowRight className="w-5 h-5" />
              </Link>
            </div>

            {/* FULL ANIMATION: Orbital + Parallax + Breathing + Magnetic */}
            <div ref={containerRef} className="relative h-[600px] flex items-center justify-center">
              {/* Breathing container */}
              <div 
                className="absolute w-full h-full flex items-center justify-center"
                style={{
                  animation: 'breathe 6s ease-in-out infinite',
                }}
              >
                {sommeliers.map((s, i) => {
                  const pos = getPosition(s, i);
                  const isJeanPierre = s.id === 'jeanpierre';
                  const size = isJeanPierre ? 'w-36 h-36' : 'w-20 h-20';
                  const Icon = s.icon;
                  
                  return (
                    <div
                      key={s.id}
                      className={`absolute ${size} transition-all duration-200 ${isJeanPierre ? 'z-30' : 'z-20'}`}
                      style={{
                        transform: `translate(${pos.x}px, ${pos.y}px) scale(${hoveredId === s.id ? 1.2 : pos.scale})`,
                        left: '50%',
                        top: '50%',
                        marginLeft: isJeanPierre ? '-72px' : '-40px',
                        marginTop: isJeanPierre ? '-72px' : '-40px',
                      }}
                      onMouseEnter={() => setHoveredId(s.id)}
                      onMouseLeave={() => setHoveredId(null)}
                    >
                      <div 
                        className={`w-full h-full rounded-full overflow-hidden border-4 border-white shadow-2xl transition-all duration-300 ${isJeanPierre ? 'ring-4 ring-[#DAA520] ring-offset-4' : ''}`}
                        style={{ 
                          borderColor: isJeanPierre ? undefined : s.color,
                          boxShadow: hoveredId === s.id 
                            ? `0 0 50px ${s.color}80, 0 0 100px ${s.color}40`
                            : isJeanPierre 
                              ? `0 0 60px ${s.color}60, 0 0 0 4px white, 0 0 0 8px #DAA52040`
                              : `0 0 20px ${s.color}30`,
                        }}
                      >
                        <Image src={`/sommeliers/${s.id}.png`} alt={s.name} fill className="object-cover object-top" />
                      </div>
                      
                      {hoveredId === s.id && (
                        <div className="absolute -bottom-20 left-1/2 -translate-x-1/2 bg-white px-4 py-3 rounded-xl shadow-2xl border border-gray-100 whitespace-nowrap z-50"
                        >
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: `${s.color}20` }}>
                              <Icon className="w-4 h-4" style={{ color: s.color }} />
                            </div>
                            <div>
                              <p className="font-semibold text-sm text-[#722F37]">{s.name}</p>
                              <p className="text-xs text-gray-500">{isJeanPierre ? 'Grand Sommelier' : 'Sommelier'}</p>
                            </div>
                            {isJeanPierre && (
                              <span className="text-[10px] px-1.5 py-0.5 bg-[#DAA520] text-white rounded-full">MASTER</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      <style jsx global>{`
        @keyframes breathe {
          0%, 100% { transform: scale(0.98); }
          50% { transform: scale(1.05); }
        }
      `}</style>
    </div>
  );
}
