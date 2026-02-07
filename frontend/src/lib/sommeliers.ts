/**
 * Sommelier Theme Configuration
 * Each sommelier has their own color palette and icon for consistent branding
 */

export interface SommelierTheme {
  id: string;
  name: string;
  role: string;
  emoji: string;
  color: string;
  bgColor: string;
  borderColor: string;
  textColor: string;
  lightBg: string;
  description: string;
  image: string;
}

export const SOMMELIER_THEMES: Record<string, SommelierTheme> = {
  marcel: {
    id: 'marcel',
    name: 'Marcel',
    role: 'Cellar Master',
    emoji: '🏛️',
    color: '#8B7355',
    bgColor: 'bg-amber-800',
    borderColor: 'border-amber-700',
    textColor: 'text-amber-800',
    lightBg: 'bg-amber-50',
    description: 'Structure & Metrics',
    image: '/sommeliers/marcel.png',
  },
  isabella: {
    id: 'isabella',
    name: 'Isabella',
    role: 'Wine Critic',
    emoji: '🎭',
    color: '#C41E3A',
    bgColor: 'bg-rose-700',
    borderColor: 'border-rose-600',
    textColor: 'text-rose-700',
    lightBg: 'bg-rose-50',
    description: 'Code Quality',
    image: '/sommeliers/isabella.png',
  },
  heinrich: {
    id: 'heinrich',
    name: 'Heinrich',
    role: 'Quality Inspector',
    emoji: '🔍',
    color: '#2F4F4F',
    bgColor: 'bg-slate-700',
    borderColor: 'border-slate-600',
    textColor: 'text-slate-700',
    lightBg: 'bg-slate-50',
    description: 'Security & Testing',
    image: '/sommeliers/heinrich.png',
  },
  sofia: {
    id: 'sofia',
    name: 'Sofia',
    role: 'Vineyard Scout',
    emoji: '🌱',
    color: '#DAA520',
    bgColor: 'bg-yellow-600',
    borderColor: 'border-yellow-500',
    textColor: 'text-yellow-700',
    lightBg: 'bg-yellow-50',
    description: 'Innovation & Tech',
    image: '/sommeliers/sofia.png',
  },
  laurent: {
    id: 'laurent',
    name: 'Laurent',
    role: 'Winemaker',
    emoji: '🛠️',
    color: '#228B22',
    bgColor: 'bg-emerald-700',
    borderColor: 'border-emerald-600',
    textColor: 'text-emerald-700',
    lightBg: 'bg-emerald-50',
    description: 'Implementation',
    image: '/sommeliers/laurent.png',
  },
  jeanpierre: {
    id: 'jeanpierre',
    name: 'Jean-Pierre',
    role: 'Grand Sommelier',
    emoji: '🎯',
    color: '#722F37',
    bgColor: 'bg-[#722F37]',
    borderColor: 'border-[#722F37]',
    textColor: 'text-[#722F37]',
    lightBg: 'bg-[#F7E7CE]',
    description: 'Final Synthesis',
    image: '/sommeliers/jeanpierre.png',
  },
};

export function getSommelierTheme(id: string): SommelierTheme {
  const normalizedId = id.toLowerCase().replace(/[^a-z]/g, '');
  return SOMMELIER_THEMES[normalizedId] || SOMMELIER_THEMES.jeanpierre;
}

export function getScoreTier(score: number): {
  name: string;
  emoji: string;
  color: string;
  bgColor: string;
} {
  if (score >= 95) return { name: 'Legendary', emoji: '🏆', color: 'text-yellow-600', bgColor: 'bg-gradient-to-r from-yellow-100 to-amber-100' };
  if (score >= 90) return { name: 'Grand Cru', emoji: '🥇', color: 'text-amber-700', bgColor: 'bg-gradient-to-r from-amber-50 to-yellow-50' };
  if (score >= 85) return { name: 'Premier Cru', emoji: '🥈', color: 'text-orange-600', bgColor: 'bg-gradient-to-r from-orange-50 to-amber-50' };
  if (score >= 80) return { name: 'Village', emoji: '🥉', color: 'text-[#722F37]', bgColor: 'bg-gradient-to-r from-[#F7E7CE] to-[#EDE0C8]' };
  if (score >= 70) return { name: 'Table Wine', emoji: '🏅', color: 'text-blue-600', bgColor: 'bg-gradient-to-r from-blue-50 to-sky-50' };
  if (score >= 60) return { name: 'House Wine', emoji: '🍷', color: 'text-purple-600', bgColor: 'bg-gradient-to-r from-purple-50 to-violet-50' };
  return { name: 'Corked', emoji: '⚠️', color: 'text-red-600', bgColor: 'bg-gradient-to-r from-red-50 to-rose-50' };
}
