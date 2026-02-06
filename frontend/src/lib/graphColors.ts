export const SIX_HATS_COLORS = {
  Marcel: { name: 'Wine Red', hex: '#722F37' },
  Isabella: { name: 'Rose Pink', hex: '#C06C84' },
  Heinrich: { name: 'Deep Navy', hex: '#2C3E50' },
  Sofia: { name: 'Gold', hex: '#D4A574' },
  Laurent: { name: 'Forest Green', hex: '#2D5016' },
  'Jean-Pierre': { name: 'Royal Purple', hex: '#6C3483' },
} as const;

export const FULL_TECHNIQUES_COLORS = {
  Aroma: { name: 'Scent Analysis', hex: '#9B59B6' },
  Palate: { name: 'Taste Analysis', hex: '#E74C3C' },
  Body: { name: 'Body Feel', hex: '#F39C12' },
  Finish: { name: 'Aftertaste', hex: '#1ABC9C' },
  Balance: { name: 'Harmony', hex: '#3498DB' },
  Vintage: { name: 'Age Quality', hex: '#27AE60' },
  Terroir: { name: 'Origin', hex: '#E67E22' },
  Cellar: { name: 'Storage', hex: '#34495E' },
} as const;

export type SixHatsAgent = keyof typeof SIX_HATS_COLORS;
export type FullTechniquesCategory = keyof typeof FULL_TECHNIQUES_COLORS;

export function getAgentColor(agentName: string): string {
  return SIX_HATS_COLORS[agentName as SixHatsAgent]?.hex || '#722F37';
}

export function getCategoryColor(category: string): string {
  return FULL_TECHNIQUES_COLORS[category as FullTechniquesCategory]?.hex || '#722F37';
}
