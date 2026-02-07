'use client';

import React from 'react';
import Image from 'next/image';
import { Wine, Sparkles, Crown, Quote, Trophy, Medal, Award, Star } from 'lucide-react';
import { EvaluationResult } from '../types';
import { ScoreGauge } from './ScoreGauge';
import { SommelierCard } from './SommelierCard';
import { getScoreTier, getSommelierTheme } from '../lib/sommeliers';

interface TastingNotesTabProps {
  result: EvaluationResult;
}

function ScoreBreakdownChart({ results }: { results: EvaluationResult['results'] }) {
  const maxScore = Math.max(...results.map(r => r.score));
  const minScore = Math.min(...results.map(r => r.score));
  const avgScore = Math.round(results.reduce((sum, r) => sum + r.score, 0) / results.length);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
        <Sparkles size={18} className="text-[#722F37]" />
        Score Breakdown
      </h3>
      <div className="space-y-3">
        {results.map((somm) => {
          const theme = getSommelierTheme(somm.id);
          const barWidth = (somm.score / 100) * 100;
          const isMax = somm.score === maxScore;
          const isMin = somm.score === minScore;
          
          return (
            <div key={somm.id} className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full overflow-hidden relative flex-shrink-0 border-2 border-[#722F37]/30">
                <Image
                  src={theme.image}
                  alt={theme.name}
                  fill
                  className="object-cover object-top"
                  sizes="40px"
                />
              </div>
              <div className="w-20 text-sm font-medium text-gray-700 truncate">
                {theme.name}
              </div>
              <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden relative">
                <div
                  className="h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r from-[#722F37] to-[#8B3D47]"
                  style={{
                    width: `${barWidth}%`,
                  }}
                />
              </div>
              <div className="w-12 text-right font-bold text-[#722F37]">
                {somm.score}
              </div>
              <div className="w-16 flex justify-end">
                {isMax && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-xs font-semibold">
                    <Crown size={12} />
                    TOP
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Stats */}
      <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">Highest</p>
          <p className="text-lg font-bold text-green-600">{maxScore}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">Average</p>
          <p className="text-lg font-bold text-gray-700">{avgScore}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">Lowest</p>
          <p className="text-lg font-bold text-amber-600">{minScore}</p>
        </div>
      </div>
    </div>
  );
}

/* Hero Section: Jean-Pierre's Verdict */
function HeroSection({ result, tier }: { result: EvaluationResult; tier: ReturnType<typeof getScoreTier> }) {
  // Map tier to lucide icon
  const getTierIcon = (name: string) => {
    switch (name) {
      case 'Legendary': return <Trophy size={24} className="text-yellow-500" />;
      case 'Grand Cru': return <Trophy size={24} className="text-amber-600" />;
      case 'Premier Cru': return <Medal size={24} className="text-orange-500" />;
      case 'Village': return <Award size={24} className="text-green-600" />;
      case 'Table Wine': return <Star size={24} className="text-purple-500" />;
      default: return <Wine size={24} className="text-gray-500" />;
    }
  };

  return (
    <div className="bg-gradient-to-br from-[#722F37] via-[#8B3D47] to-[#5A252C] rounded-2xl shadow-xl overflow-hidden">
      <div className="relative">
        {/* Jean-Pierre on the right */}
        <div className="absolute right-0 top-0 bottom-0 w-64 md:w-80">
          <Image
            src="/sommeliers/jeanpierre.png"
            alt="Jean-Pierre"
            fill
            className="object-cover object-top"
            sizes="320px"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#722F37] via-[#722F37]/60 to-transparent" />
        </div>
        
        <div className="relative z-10 p-6 md:p-8 pr-32 md:pr-48">
          {/* Score + Badge inline, compact */}
          <div className="flex items-center gap-4 mb-5">
            <div className="flex items-baseline gap-1 text-white">
              <span className="text-5xl md:text-6xl font-bold leading-none">{result.totalScore}</span>
              <span className="text-white/50 text-lg">/100</span>
            </div>
            <div className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full ${tier.bgColor} shadow-lg`}>
              {getTierIcon(tier.name)}
              <span className={`font-bold text-lg ${tier.color}`}>{tier.name}</span>
            </div>
          </div>
          
          {/* Verdict as a quote */}
          <div className="border-l-4 border-[#F7E7CE]/40 pl-5">
            <div className="flex items-center gap-2 mb-2">
              <Quote size={14} className="text-[#F7E7CE]/60" />
              <span className="text-[#F7E7CE]/80 text-xs font-medium uppercase tracking-wider">
                Jean-Pierre&apos;s Verdict
              </span>
            </div>
            <blockquote className="text-white/90 text-base md:text-lg leading-relaxed italic font-serif max-w-2xl">
              &ldquo;{result.finalVerdict}&rdquo;
            </blockquote>
          </div>
        </div>
      </div>
    </div>
  );
}

export function TastingNotesTab({ result }: TastingNotesTabProps) {
  const tier = getScoreTier(result.totalScore || 0);

  return (
    <div className="animate-fadeIn space-y-8">
      {/* Hero Score Section */}
      <HeroSection result={result} tier={tier} />

      {/* Score Breakdown Chart */}
      <ScoreBreakdownChart results={result.results} />

      {/* Sommelier Cards Grid */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Wine size={20} className="text-[#722F37]" />
          Individual Tasting Notes
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {result.results.map((somm, index) => (
            <SommelierCard
              key={somm.id}
              id={somm.id}
              name={somm.name}
              role={somm.role}
              score={somm.score}
              feedback={somm.feedback}
              recommendations={somm.recommendations}
              pairingSuggestion={somm.pairingSuggestion}
              delay={index * 100}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
