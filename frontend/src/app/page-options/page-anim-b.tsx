'use client';

import { useState, useEffect, useRef } from 'react';
import { Wine, ArrowRight, FolderGit, Code, Shield, Lightbulb, Wrench, Trophy } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

const sommeliers = [
  { id: "marcel", name: "Marcel", color: "#8B7355", icon: FolderGit, drift: { x: 15, y: 10, speed: 8 } },
  { id: "isabella", name: "Isabella", color: "#C41E3A", icon: Code, drift: { x: -12, y: 18, speed: 6 } },
  { id: "heinrich", name: "Heinrich", color: "#2F4F4F", icon: Shield, drift: { x: 20, y: -8, speed: 10 } },
  { id: "sofia", name: "Sofia", color: "#DAA520", icon: Lightbulb, drift: { x: -18, y: 15, speed: 5 } },
  { id: "laurent", name: "Laurent", color: "#228B22", icon: Wrench, drift: { x: 10, y: -20, speed: 9 } },
  { id: "jeanpierre", name: "Jean-Pierre", color: "#4169E1", icon: Trophy, drift: { x: 0, y: 0, speed: 0 } },
];

export default function Home() {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [positions, setPositions] = useState(sommeliers.map(() => ({ x: 0, y: 0 })));
  const containerRef = useRef<HTMLDivElement>(null);
  const timeRef = useRef(0);

  useEffect(() => {
    let animationId: number;
    
    const animate = () => {
      timeRef.current += 0.005;
      
      setPositions(sommeliers.map((s, i) => {
        if (s.id === 'jeanpierre') return { x: 0, y: 0 };
        
        // Random drift using noise-like movement
        const driftX = Math.sin(timeRef.current * s.drift.speed + i) * s.drift.x;
        const driftY = Math.cos(timeRef.current * s.drift.speed * 0.7 + i) * s.drift.y;
        
        // Magnetic effect toward hovered sommelier
        let magneticX = 0, magneticY = 0;
        if (hoveredId && hoveredId !== s.id) {
          const hoveredIndex = sommeliers.findIndex(som => som.id === hoveredId);
          if (hoveredIndex !== -1) {
            const pullStrength = 0.3;
            magneticX = (positions[hoveredIndex]?.x || 0) * pullStrength;
            magneticY = (positions[hoveredIndex]?.y || 0) * pullStrength;
          }
        }
        
        return {
          x: driftX + magneticX,
          y: driftY + magneticY,
        };
      }));
      
      animationId = requestAnimationFrame(animate);
    };
    
    animate();
    return () => cancelAnimationFrame(animationId);
  }, [hoveredId, positions]);

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
              <Link href="/evaluate" className="inline-flex items-center gap-2 px-8 py-4 bg-[#722F37] text-[#F7E7CE] rounded-full">
                Start Free Evaluation <ArrowRight className="w-5 h-5" />
              </Link>
            </div>

            {/* Breathing Cluster + Random Drift */}
            <div ref={containerRef} className="relative h-[600px] flex items-center justify-center">
              <div 
                className="absolute w-full h-full"
                style={{
                  animation: 'breathe 6s ease-in-out infinite',
                }}
              >
                {sommeliers.map((s, i) => {
                  const basePositions = [
                    { x: -150, y: -100 },
                    { x: 150, y: -120 },
                    { x: 180, y: 50 },
                    { x: 80, y: 180 },
                    { x: -120, y: 150 },
                    { x: 0, y: 0 },
                  ];
                  
                  const isJeanPierre = s.id === 'jeanpierre';
                  const size = isJeanPierre ? 'w-40 h-40' : 'w-24 h-24';
                  
                  return (
                    <div
                      key={s.id}
                      className={`absolute transition-transform duration-300 ${size} ${isJeanPierre ? 'z-30' : 'z-20'}`}
                      style={{
                        left: `calc(50% + ${basePositions[i].x}px)`,
                        top: `calc(50% + ${basePositions[i].y}px)`,
                        transform: `translate(-50%, -50%) translate(${positions[i]?.x || 0}px, ${positions[i]?.y || 0}px) scale(${hoveredId === s.id ? 1.15 : 1})`,
                      }}
                      onMouseEnter={() => setHoveredId(s.id)}
                      onMouseLeave={() => setHoveredId(null)}
                    >
                      <div className={`w-full h-full rounded-full overflow-hidden border-4 border-white shadow-xl transition-all duration-300 ${isJeanPierre ? 'ring-4 ring-[#DAA520]' : ''}`}
                        style={{ 
                          borderColor: isJeanPierre ? undefined : s.color,
                          boxShadow: hoveredId === s.id ? `0 0 40px ${s.color}60` : undefined,
                        }}
                      >
                        <Image src={`/sommeliers/${s.id}.png`} alt={s.name} fill className="object-cover object-top" />
                      </div>
                      
                      {hoveredId === s.id && (
                        <div className="absolute -bottom-16 left-1/2 -translate-x-1/2 bg-white px-3 py-2 rounded-lg shadow-lg whitespace-nowrap z-40">
                          <p className="font-semibold text-sm text-[#722F37]">{s.name}</p>
                          <p className="text-xs text-gray-500">{s.color === '#4169E1' ? 'Grand Sommelier' : 'Sommelier'}</p>
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
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
      `}</style>
    </div>
  );
}
