'use client';

import React, { useState } from 'react';
import { ArrowLeft, Share2, Download, Check, Trophy, Wine } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

// Static demo data from real evaluation of ai/nanoid
const DEMO_RESULT = {
  id: 'demo',
  repoUrl: 'https://github.com/ai/nanoid',
  repoName: 'ai/nanoid',
  status: 'completed',
  createdAt: '2026-02-07T07:15:00Z',
  totalScore: 97,
  tier: 'Legendary',
  finalVerdict: `"After decades in the cellar, one occasionally encounters a vintage that defies the standard laws of software viticulture. Nano ID is such a rarity—a 'Grand Cru' of extreme reduction. It is the software equivalent of a perfectly concentrated Icewine, where the freezing out of every unnecessary byte has left behind a potent, crystalline essence of logic. My colleagues have correctly identified the 'senseless perfectionism' that defines this work. Marcel finds a vault of remarkable economy; Isabella tastes the crisp, dependency-free clarity; Heinrich confirms the robust, hardware-backed security tannins; Sofia notes its forward-looking readiness for new registries; and Laurent admires the artisanal precision of the mask-based algorithm that avoids the bitterness of modulo bias. It is a codebase that understands that in the highest forms of craft, beauty is not found in what is added, but in what can no longer be stripped away."`,
  results: [
    {
      id: 'marcel',
      name: 'Marcel',
      role: 'Cellar Master',
      desc: 'Structure & Metrics',
      color: '#8B7355',
      score: 96,
      feedback: `As I walk through this cellar, I am struck by its remarkable economy. This is not a sprawling estate, but a high-density boutique vault where every cubic inch is accounted for. The 'Nano ID' vintage is a masterclass in distillation—a rare icon of minimalist architecture that has been aged to perfection.`,
      techniques: ['Constraint Mapping', 'Ecosystem Thinking', 'Data Mining', 'Fact Checking'],
      pairingSuggestion: 'Constraint Mapping'
    },
    {
      id: 'isabella',
      name: 'Isabella',
      role: 'Wine Critic',
      desc: 'Code Quality',
      color: '#C41E3A',
      score: 98,
      feedback: `The Nano ID repository is a masterclass in software viticulture—a rare vintage that achieves a profound depth of flavor through extreme reduction. Upon the first pour, one is struck by its remarkable clarity; the 118-byte footprint is not a limitation, but the result of an uncompromising pursuit of essence.`,
      techniques: ['Constraint Mapping', 'Ecosystem Thinking', 'Evolutionary Pressure Analysis', 'Morphological Analysis'],
      pairingSuggestion: 'Constraint Mapping'
    },
    {
      id: 'heinrich',
      name: 'Heinrich',
      role: 'Quality Inspector',
      desc: 'Security & Testing',
      color: '#2F4F4F',
      score: 96,
      feedback: `A magnificent vintage, refined to the point of crystalline purity. Like a Grand Cru that has been stripped of all unnecessary sediment, this library achieves a rare balance between minimalist structure and robust defense. The use of crypto.getRandomValues() provides a solid foundation.`,
      techniques: ['Fact Checking', 'Failure Analysis (FMEA)', 'Constraint Mapping', 'Ecosystem Thinking'],
      pairingSuggestion: 'Fact Checking'
    },
    {
      id: 'sofia',
      name: 'Sofia',
      role: 'Vineyard Scout',
      desc: 'Innovation & Tech',
      color: '#DAA520',
      score: 96,
      feedback: `Nanoid is like a rare, perfectly concentrated Icewine—a result of intense focus and a 'senseless perfectionism' that yields something both tiny and incredibly potent. I've scouted this territory and found a project that doesn't just follow trends, it sets them.`,
      techniques: ['Ecosystem Thinking', 'Evolutionary Pressure Analysis', 'Constraint Mapping', 'Fact Checking'],
      pairingSuggestion: 'Ecosystem Thinking'
    },
    {
      id: 'laurent',
      name: 'Laurent',
      role: 'Winemaker',
      desc: 'Implementation',
      color: '#228B22',
      score: 98,
      feedback: `Ah, here we have a vintage that truly understands the beauty of restraint. Like a perfect Sancerre, Nano ID achieves its brilliance not through complexity, but through the absolute purity of its elements. The choice of 'grapes'—the URL-safe alphabet—is impeccable.`,
      techniques: ['Constraint Mapping', 'Failure Analysis (FMEA)', 'Algorithm efficiency and correctness evaluation', 'Ecosystem Thinking'],
      pairingSuggestion: 'Constraint Mapping'
    },
  ]
};

const tierStyles: Record<string, { bg: string; text: string; border: string }> = {
  'Legendary': { bg: 'bg-gradient-to-r from-yellow-400 to-amber-500', text: 'text-white', border: 'border-yellow-400' },
  'Grand Cru': { bg: 'bg-gradient-to-r from-amber-400 to-yellow-500', text: 'text-white', border: 'border-amber-400' },
  'Premier Cru': { bg: 'bg-gradient-to-r from-orange-400 to-amber-500', text: 'text-white', border: 'border-orange-400' },
  'Village': { bg: 'bg-gradient-to-r from-emerald-400 to-green-500', text: 'text-white', border: 'border-emerald-400' },
};

export default function DemoResultPage() {
  const [copied, setCopied] = useState(false);
  const result = DEMO_RESULT;
  const tierStyle = tierStyles[result.tier] || tierStyles['Village'];

  const handleShare = async () => {
    const shareUrl = window.location.href;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      console.error('Failed to copy');
    }
  };

  const handleExportPDF = () => {
    window.print();
  };

  // Find top scorers
  const maxScore = Math.max(...result.results.map(r => r.score));
  const topScorers = result.results.filter(r => r.score === maxScore).map(r => r.id);

  return (
    <div className="min-h-screen bg-[#FAF4E8]">
      {/* Header */}
      <header className="bg-[#722F37] text-white py-4 px-6 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[#F7E7CE] flex items-center justify-center">
                <Wine className="w-4 h-4 text-[#722F37]" />
              </div>
              <span className="font-serif text-xl font-bold">Somm</span>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/evaluate" className="text-sm hover:underline">Evaluate</Link>
            <Link href="#" className="text-sm hover:underline">History</Link>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Back & Actions */}
        <div className="flex items-center justify-between mb-6">
          <Link href="/" className="flex items-center gap-2 text-[#722F37] hover:underline">
            <ArrowLeft className="w-4 h-4" />
            <span>New Tasting</span>
          </Link>
          <div className="flex items-center gap-3">
            <button
              onClick={handleShare}
              className="flex items-center gap-2 px-4 py-2 border border-[#722F37]/20 rounded-lg hover:bg-[#722F37]/5 transition-colors"
            >
              {copied ? <Check className="w-4 h-4 text-green-600" /> : <Share2 className="w-4 h-4" />}
              <span>{copied ? 'Copied!' : 'Share'}</span>
            </button>
            <button
              onClick={handleExportPDF}
              className="flex items-center gap-2 px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5A252C] transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Export PDF</span>
            </button>
          </div>
        </div>

        {/* Demo Badge */}
        <div className="mb-4 inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
          <span>📋 Demo Result</span>
          <span className="text-blue-500">|</span>
          <span>{result.repoName}</span>
        </div>

        {/* Main Score Card */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden mb-8">
          {/* Score Header */}
          <div className="bg-gradient-to-r from-[#722F37] to-[#5A252C] p-8 text-white relative">
            <div className="absolute top-4 right-4">
              <Image src="/sommeliers/jeanpierre.png" alt="Jean-Pierre" width={80} height={80} className="rounded-full border-4 border-white/20" />
            </div>
            <div className="flex items-end gap-4 mb-4">
              <span className="text-7xl font-bold">{result.totalScore}</span>
              <span className="text-2xl text-white/60 mb-2">/100</span>
              <span className={`px-4 py-1.5 rounded-full text-sm font-bold ${tierStyle.bg} ${tierStyle.text} mb-2 flex items-center gap-1`}>
                <Trophy className="w-4 h-4" />
                {result.tier}
              </span>
            </div>
            <p className="text-sm text-white/60 mb-2">JEAN-PIERRE&apos;S VERDICT</p>
            <p className="text-white/90 italic leading-relaxed max-w-3xl">{result.finalVerdict}</p>
          </div>

          {/* Score Breakdown */}
          <div className="p-8">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-[#722F37] mb-6">
              <span>✨</span> Score Breakdown
            </h3>
            <div className="space-y-4">
              {result.results.map((sommelier) => (
                <div key={sommelier.id} className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-white shadow flex-shrink-0">
                    <Image src={`/sommeliers/${sommelier.id}.png`} alt={sommelier.name} width={40} height={40} className="object-cover object-top" />
                  </div>
                  <span className="w-20 text-sm font-medium text-gray-700">{sommelier.name}</span>
                  <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${sommelier.score}%`, backgroundColor: sommelier.color }}
                    />
                  </div>
                  <span className="w-12 text-right font-bold" style={{ color: sommelier.color }}>{sommelier.score}</span>
                  {topScorers.includes(sommelier.id) && (
                    <span className="text-xs px-2 py-0.5 bg-red-100 text-red-600 rounded-full font-medium">🔥 TOP</span>
                  )}
                </div>
              ))}
            </div>

            {/* Stats */}
            <div className="flex items-center justify-around mt-8 pt-6 border-t border-gray-100">
              <div className="text-center">
                <p className="text-xs text-gray-500 uppercase">Highest</p>
                <p className="text-2xl font-bold text-blue-600">{maxScore}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 uppercase">Average</p>
                <p className="text-2xl font-bold text-gray-700">{result.totalScore}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-gray-500 uppercase">Lowest</p>
                <p className="text-2xl font-bold text-orange-500">{Math.min(...result.results.map(r => r.score))}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Individual Tasting Notes */}
        <h3 className="flex items-center gap-2 text-xl font-semibold text-[#722F37] mb-6">
          <span>🍷</span> Individual Tasting Notes
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          {result.results.map((sommelier) => (
            <div key={sommelier.id} className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
              <div className="p-4 text-white relative" style={{ backgroundColor: sommelier.color }}>
                <div className="absolute top-2 right-2 w-16 h-16 rounded-full overflow-hidden border-2 border-white/30">
                  <Image src={`/sommeliers/${sommelier.id}.png`} alt={sommelier.name} fill className="object-cover object-top" />
                </div>
                <h4 className="font-bold text-lg">{sommelier.name}</h4>
                <p className="text-sm text-white/80">{sommelier.desc}</p>
                <div className="mt-2 inline-flex items-center px-2 py-1 bg-white/20 rounded text-sm font-bold">
                  {sommelier.score}<span className="text-white/60 text-xs ml-0.5">/100</span>
                </div>
              </div>
              <div className="p-4">
                <p className="text-gray-600 text-sm leading-relaxed mb-4">{sommelier.feedback}</p>
                <div className="border-t border-gray-100 pt-4">
                  <p className="text-xs text-gray-400 uppercase mb-2">Techniques Applied</p>
                  <div className="flex flex-wrap gap-1">
                    {sommelier.techniques.map((tech, i) => (
                      <span key={i} className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: `${sommelier.color}15`, color: sommelier.color }}>
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-xs text-gray-400 uppercase">Pairing Suggestion</p>
                  <p className="text-sm font-medium" style={{ color: sommelier.color }}>{sommelier.pairingSuggestion}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <p className="text-gray-500 mb-4">Want to evaluate your own repository?</p>
          <Link href="/evaluate" className="inline-flex items-center gap-2 px-8 py-4 bg-[#722F37] text-white rounded-full font-semibold hover:bg-[#5A252C] transition-colors">
            Start Your Evaluation
          </Link>
        </div>
      </main>
    </div>
  );
}
