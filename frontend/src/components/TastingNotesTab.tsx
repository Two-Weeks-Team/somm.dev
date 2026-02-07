'use client';

import React from 'react';
import { Wine, Sparkles, TrendingUp, TrendingDown, Minus } from 'lucide-react';
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
              <div className="w-8 text-center text-lg">{theme.emoji}</div>
              <div className="w-20 text-sm font-medium text-gray-600 truncate">
                {theme.name}
              </div>
              <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden relative">
                <div
                  className="h-full rounded-full transition-all duration-1000 ease-out"
                  style={{
                    width: `${barWidth}%`,
                    backgroundColor: theme.color,
                  }}
                />
              </div>
              <div className="w-12 text-right font-bold" style={{ color: theme.color }}>
                {somm.score}
              </div>
              <div className="w-6">
                {isMax && <TrendingUp size={16} className="text-green-500" />}
                {isMin && results.length > 1 && <TrendingDown size={16} className="text-amber-500" />}
                {!isMax && !isMin && <Minus size={16} className="text-gray-300" />}
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

export function TastingNotesTab({ result }: TastingNotesTabProps) {
  const tier = getScoreTier(result.totalScore || 0);

  return (
    <div className="animate-fadeIn space-y-8">
      {/* Hero Score Section */}
      <div className="bg-gradient-to-br from-[#722F37] via-[#8B3D47] to-[#5A252C] rounded-2xl shadow-xl overflow-hidden">
        <div className="relative">
          {/* Decorative pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white rounded-full -translate-y-1/2 translate-x-1/2" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white rounded-full translate-y-1/2 -translate-x-1/2" />
          </div>
          
          <div className="relative z-10 p-8 md:p-12">
            <div className="flex flex-col md:flex-row items-center gap-8">
              {/* Left: Score */}
              <div className="text-center">
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                  <ScoreGauge score={result.totalScore || 0} size="lg" showLabel={false} />
                  <div className={`mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full ${tier.bgColor}`}>
                    <span className="text-xl">{tier.emoji}</span>
                    <span className={`font-bold ${tier.color}`}>{tier.name}</span>
                  </div>
                </div>
              </div>
              
              {/* Right: Verdict */}
              <div className="flex-1 text-white text-center md:text-left">
                <div className="flex items-center justify-center md:justify-start gap-2 mb-4">
                  <Wine size={24} className="text-[#F7E7CE]" />
                  <h2 className="text-xl font-serif">Jean-Pierre&apos;s Verdict</h2>
                </div>
                <blockquote className="text-lg md:text-xl leading-relaxed opacity-90 italic">
                  &ldquo;{result.finalVerdict}&rdquo;
                </blockquote>
                {result.repoUrl && (
                  <p className="mt-4 text-sm opacity-60 font-mono">
                    {result.repoUrl}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

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
