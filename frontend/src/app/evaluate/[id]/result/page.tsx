'use client';

import React, { useEffect, useState, lazy, Suspense } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '../../../../lib/api';
import { EvaluationResult } from '../../../../types';
import { ArrowLeft, Share2, Download } from 'lucide-react';
import { ResultTabs, useResultTab, ResultTabId } from '../../../../components/ResultTabs';
import { TastingNotesTab } from '../../../../components/TastingNotesTab';
import { GraphSkeleton } from '../../../../components/graph/GraphSkeleton';

const Graph2DTab = lazy(() => import('../../../../components/Graph2DTab').then(m => ({ default: m.Graph2DTab })));
const Graph3DTab = lazy(() => import('../../../../components/Graph3DTab').then(m => ({ default: m.Graph3DTab })));

function TabLoadingFallback() {
  return (
    <div className="md:h-[600px] h-[400px]">
      <GraphSkeleton />
    </div>
  );
}

export default function ResultPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useResultTab('tasting');

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const data = await api.getEvaluationResult(id);
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchResult();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#722F37] mx-auto mb-4"></div>
          <p className="text-[#722F37] font-medium">Decanting results...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA]">
        <div className="text-center max-w-md mx-auto p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Corked!</h2>
          <p className="text-gray-600 mb-6">{error || 'Result not found'}</p>
          <button
            onClick={() => router.push('/evaluate')}
            className="px-6 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5a252c] transition-colors"
          >
            Try Another Vintage
          </button>
        </div>
      </div>
    );
  }

  const renderTabContent = (tabId: ResultTabId) => {
    switch (tabId) {
      case 'tasting':
        return <TastingNotesTab result={result} />;
      case 'graph-2d':
        return (
          <Suspense fallback={<TabLoadingFallback />}>
            <Graph2DTab evaluationId={id} />
          </Suspense>
        );
      case 'graph-3d':
        return (
          <Suspense fallback={<TabLoadingFallback />}>
            <Graph3DTab evaluationId={id} />
          </Suspense>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <button
            onClick={() => router.push('/evaluate')}
            className="flex items-center text-gray-600 hover:text-[#722F37] transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            New Tasting
          </button>
          <div className="flex space-x-4">
            <button className="flex items-center px-4 py-2 text-sm font-medium text-[#722F37] bg-white border border-[#722F37] rounded-lg hover:bg-[#FAFAFA]">
              <Share2 size={16} className="mr-2" />
              Share
            </button>
            <button className="flex items-center px-4 py-2 text-sm font-medium text-white bg-[#722F37] rounded-lg hover:bg-[#5a252c]">
              <Download size={16} className="mr-2" />
              Export PDF
            </button>
          </div>
        </div>

        <ResultTabs activeTab={activeTab} onTabChange={setActiveTab} />

        {renderTabContent(activeTab)}
      </div>
    </div>
  );
}
