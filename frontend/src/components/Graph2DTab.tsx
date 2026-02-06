'use client';

import React from 'react';
import { BarChart3 } from 'lucide-react';

interface Graph2DTabProps {
  evaluationId: string;
}

export function Graph2DTab({ evaluationId }: Graph2DTabProps) {
  return (
    <div className="animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#F7E7CE] text-[#722F37] mb-4">
          <BarChart3 size={32} />
        </div>
        <h2 className="text-2xl font-serif font-bold text-gray-900 mb-2">2D Graph Visualization</h2>
        <p className="text-gray-500 mb-4">
          Interactive ReactFlow graph showing the evaluation pipeline
        </p>
        <p className="text-sm text-gray-400">
          Evaluation ID: {evaluationId}
        </p>
        <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300">
          <p className="text-sm text-gray-500">
            ReactFlow 2D Graph Viewer will be implemented in Issue #168
          </p>
        </div>
      </div>
    </div>
  );
}
