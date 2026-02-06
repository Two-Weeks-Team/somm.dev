'use client';

import React from 'react';
import { Wine, Star } from 'lucide-react';
import { EvaluationResult } from '../types';
import { ScoreCircle } from './ScoreCircle';

interface TastingNotesTabProps {
  result: EvaluationResult;
}

export function TastingNotesTab({ result }: TastingNotesTabProps) {
  return (
    <div className="animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-8">
        <div className="bg-[#722F37] text-white p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full opacity-10 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]"></div>
          <h1 className="text-3xl font-serif font-bold mb-2 relative z-10">Tasting Notes</h1>
          <p className="opacity-80 relative z-10">{result.repoUrl}</p>
        </div>
        
        <div className="p-8">
          <div className="flex flex-col md:flex-row items-center justify-center md:justify-between gap-8">
            <div className="flex flex-col items-center">
              <ScoreCircle score={result.totalScore || 0} size="lg" />
            </div>

            <div className="flex-1 max-w-xl bg-[#FAFAFA] p-6 rounded-xl border border-gray-100">
              <h3 className="font-serif font-bold text-[#722F37] mb-3 flex items-center">
                <Wine size={20} className="mr-2" />
                Jean-Pierre&apos;s Verdict
              </h3>
              <p className="text-gray-700 italic leading-relaxed">
                &quot;{result.finalVerdict}&quot;
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {result.results.map((somm) => (
          <div key={somm.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-bold text-gray-900">{somm.name}</h3>
                <p className="text-sm text-[#722F37]">{somm.role}</p>
              </div>
              <div className="flex items-center bg-gray-50 px-3 py-1 rounded-full">
                <Star size={14} className="text-yellow-500 mr-1 fill-current" />
                <span className="font-bold text-gray-900">{somm.score}</span>
              </div>
            </div>
            
            <p className="text-gray-600 text-sm mb-4 leading-relaxed">
              {somm.feedback}
            </p>

            {somm.pairingSuggestion && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Pairing Suggestion</h4>
                <p className="text-sm text-[#722F37] font-medium">
                  {somm.pairingSuggestion}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
