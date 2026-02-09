import { cn } from '@/lib/utils';

interface QualityGateSealProps {
  gate: 'PASS' | 'CONCERNS' | 'FAIL' | 'INCOMPLETE' | string;
  score: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function QualityGateSeal({ gate, score, size = 'md', className }: QualityGateSealProps) {
  const normalizedGate = gate.toUpperCase();
  
  const config = {
    PASS: {
      color: '#228B22',
      bg: 'bg-[#228B22]',
      border: 'border-[#228B22]',
      text: 'text-[#228B22]',
      label: 'PASS',
      shadow: 'shadow-[0_0_15px_rgba(34,139,34,0.4)]',
    },
    CONCERNS: {
      color: '#DAA520',
      bg: 'bg-[#DAA520]',
      border: 'border-[#DAA520]',
      text: 'text-[#DAA520]',
      label: 'CONCERNS',
      shadow: 'shadow-[0_0_15px_rgba(218,165,32,0.4)]',
    },
    FAIL: {
      color: '#C41E3A',
      bg: 'bg-[#C41E3A]',
      border: 'border-[#C41E3A]',
      text: 'text-[#C41E3A]',
      label: 'FAIL',
      shadow: 'shadow-[0_0_15px_rgba(196,30,58,0.4)]',
    },
    INCOMPLETE: {
      color: '#9CA3AF',
      bg: 'bg-[#9CA3AF]',
      border: 'border-[#9CA3AF]',
      text: 'text-[#9CA3AF]',
      label: 'INCOMPLETE',
      shadow: 'shadow-[0_0_15px_rgba(156,163,175,0.4)]',
    },
  };

  const style = config[normalizedGate as keyof typeof config] || config.INCOMPLETE;

  const sizeClasses = {
    sm: { container: 'w-24 h-24', text: 'text-2xl', label: 'text-[10px]' },
    md: { container: 'w-32 h-32', text: 'text-4xl', label: 'text-xs' },
    lg: { container: 'w-40 h-40', text: 'text-5xl', label: 'text-sm' },
  };

  const sizes = sizeClasses[size];

  return (
    <div className={cn('relative flex flex-col items-center justify-center', className)}>
      <div 
        className={cn(
          'rounded-full flex flex-col items-center justify-center border-4 bg-white relative z-10',
          sizes.container,
          style.border,
          style.shadow
        )}
      >
        {/* Inner ring for embossing effect */}
        <div className="absolute inset-1 rounded-full border border-gray-100" />
        
        <span className={cn('font-bold font-serif leading-none', style.text, sizes.text)}>
          {Math.round(score)}
        </span>
        <span className="text-gray-400 text-[10px] font-medium uppercase tracking-wider mt-1">
          Score
        </span>
      </div>
      
      {/* Ribbon/Banner effect */}
      <div className={cn(
        'absolute -bottom-3 px-4 py-1 rounded-full text-white font-bold tracking-widest uppercase shadow-md z-20',
        style.bg,
        sizes.label
      )}>
        {style.label}
      </div>
    </div>
  );
}
