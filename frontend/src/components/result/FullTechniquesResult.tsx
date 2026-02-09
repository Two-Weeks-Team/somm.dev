import { FullTechniqueResultData } from '@/types';
import { QualityGateSeal } from './QualityGateSeal';
import { BMADScorecard } from './BMADScorecard';
import { CheckCircle2, XCircle, Clock, Coins } from 'lucide-react';

interface FullTechniquesResultProps {
  result: FullTechniqueResultData;
}

export function FullTechniquesResult({ result }: FullTechniquesResultProps) {
  const successfulTechniquesCount = result.techniquesUsed.length - result.failedTechniques.length;
  const failedTechniquesCount = result.failedTechniques.length;
  const totalTechniquesCount = result.techniquesUsed.length;

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-[#722F37] to-[#8B3D47] p-8 text-white">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-6">
              <QualityGateSeal 
                gate={result.qualityGate} 
                score={result.totalScore} 
                size="lg" 
              />
              <div>
                <h1 className="text-3xl font-bold font-serif mb-2">Evaluation Complete</h1>
                <p className="text-white/80 text-lg max-w-xl">
                  {result.qualityGate === 'PASS' 
                    ? "This repository meets the quality standards defined by the BMAD framework."
                    : "This repository has identified areas for improvement based on the BMAD framework."}
                </p>
                
                <div className="flex items-center gap-4 mt-4 text-sm font-medium text-white/70">
                  <div className="flex items-center gap-1.5">
                    <Clock size={16} />
                    {((result.durationMs ?? 0) / 1000).toFixed(1)}s
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Coins size={16} />
                    ${(result.costSummary?.estimatedCost ?? 0).toFixed(4)}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex flex-col items-end gap-2">
              <div className="text-right">
                <div className="text-sm text-white/60 uppercase tracking-wider font-medium">Coverage</div>
                <div className="text-3xl font-bold">{Math.round(result.coverage * 100)}%</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-white/60 uppercase tracking-wider font-medium">Techniques</div>
                <div className="text-xl font-bold">{totalTechniquesCount}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-6 bg-gray-50 border-t border-gray-100 flex flex-wrap gap-6 justify-center md:justify-start">
          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-gray-200 shadow-sm">
            <CheckCircle2 size={18} className="text-green-600" />
            <span className="font-bold text-gray-900">{successfulTechniquesCount}</span>
            <span className="text-gray-500 text-sm">Successful</span>
          </div>
          
          {failedTechniquesCount > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-red-200 shadow-sm">
              <XCircle size={18} className="text-red-600" />
              <span className="font-bold text-gray-900">{failedTechniquesCount}</span>
              <span className="text-gray-500 text-sm">Failed</span>
            </div>
          )}

          <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-gray-200 shadow-sm">
            <div className="w-2 h-2 rounded-full bg-[#722F37]" />
            <span className="font-bold text-gray-900">{result.techniquesUsed.length}</span>
            <span className="text-gray-500 text-sm">Total Evaluated</span>
          </div>
        </div>
      </div>

      <BMADScorecard 
        itemScores={result.itemScores} 
        dimensionScores={result.dimensionScores} 
      />
    </div>
  );
}
