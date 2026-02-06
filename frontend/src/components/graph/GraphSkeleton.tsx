import React from 'react';

export function GraphSkeleton() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-neutral-50/50 relative overflow-hidden rounded-lg border border-neutral-200">
      <div className="absolute inset-0 opacity-10" 
           style={{
             backgroundImage: 'radial-gradient(#722F37 1px, transparent 1px)',
             backgroundSize: '20px 20px'
           }}>
      </div>

      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shimmer" 
           style={{ transform: 'skewX(-20deg)' }}>
      </div>

      <div className="relative z-10 w-3/4 h-3/4 flex items-center justify-center">
        <div className="grid grid-cols-3 gap-12 opacity-30">
          {[...Array(9)].map((_, i) => (
            <div key={i} className="flex flex-col items-center gap-2 animate-pulse" style={{ animationDelay: `${i * 100}ms` }}>
              <div className="w-12 h-12 rounded-full bg-[#722F37]/20 border-2 border-[#722F37]/40"></div>
              <div className="w-16 h-2 rounded bg-[#722F37]/10"></div>
            </div>
          ))}
        </div>
        
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20">
          <path d="M100,100 L200,200 M300,100 L200,200 M100,300 L200,200 M300,300 L200,200" 
                stroke="#722F37" strokeWidth="2" fill="none" />
        </svg>
      </div>

      <div className="absolute bottom-8 flex flex-col items-center gap-2">
        <div className="text-[#722F37] font-medium text-lg animate-pulse">
          Decanting your graph...
        </div>
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full bg-[#722F37] animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 rounded-full bg-[#722F37] animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 rounded-full bg-[#722F37] animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
}
