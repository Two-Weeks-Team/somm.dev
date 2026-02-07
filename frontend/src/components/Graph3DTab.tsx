'use client';

import React, { useEffect, useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { AlertCircle, RefreshCw, ChevronDown, ChevronUp, Network } from 'lucide-react';
import { api } from '@/lib/api';
import { Graph3DPayload } from '@/types/graph';
import { TimelinePlayer } from './graph/TimelinePlayer';
import { useTimelinePlayer } from '@/hooks/useTimelinePlayer';
import { ModeIndicatorBadge } from './ModeIndicatorBadge';
import { GraphLegend } from './graph/GraphLegend';
import { GraphSkeleton } from './graph/GraphSkeleton';

interface Graph3DTabProps {
  evaluationId: string;
}

const GraphView3D = dynamic(() => import('./graph/GraphView3D'), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full">
      <GraphSkeleton />
    </div>
  ),
});

export function Graph3DTab({ evaluationId }: Graph3DTabProps) {
  const [data, setData] = useState<Graph3DPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [maxStep, setMaxStep] = useState(0);
  const [isExpanded, setIsExpanded] = useState(true);

  const {
    currentStep,
    setCurrentStep,
    isPlaying,
    togglePlay,
    playbackSpeed,
    setPlaybackSpeed,
  } = useTimelinePlayer(maxStep);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const graphData = await api.getGraph3D(evaluationId);
      setData(graphData);
      if (graphData.metadata?.max_step_number) {
        setMaxStep(graphData.metadata.max_step_number);
        setCurrentStep(graphData.metadata.max_step_number);
      }
    } catch (err) {
      console.error('Failed to fetch 3D graph data:', err);
      setError('Failed to load 3D graph data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [evaluationId, setCurrentStep]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="md:h-[600px] h-[400px]">
        <GraphSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center md:h-[600px] h-[400px] bg-white rounded-2xl shadow-sm border border-gray-100">
        <AlertCircle className="w-10 h-10 text-red-500 mb-4" />
        <p className="text-gray-800 font-medium mb-2">{error}</p>
        <button 
          onClick={fetchData}
          className="flex items-center px-4 py-2 bg-[#722F37] text-white rounded-lg hover:bg-[#5D262D] transition-colors"
        >
          <RefreshCw size={16} className="mr-2" />
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full px-6 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Network size={20} className="text-[#722F37]" />
          <span className="font-semibold text-gray-900">Evaluation Flow</span>
          <ModeIndicatorBadge mode={data.mode} />
        </div>
        {isExpanded ? (
          <ChevronUp size={20} className="text-gray-400" />
        ) : (
          <ChevronDown size={20} className="text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="flex flex-col gap-4 px-6 pb-6">
          <div className="md:h-[600px] h-[400px] bg-neutral-900 rounded-2xl shadow-sm border border-gray-200 overflow-hidden relative">
            <GraphLegend mode={data.mode} />
            <GraphView3D
              data={data}
              evaluationId={evaluationId}
              currentStep={currentStep}
              isPlaying={isPlaying}
              playbackSpeed={playbackSpeed}
            />
          </div>

          <TimelinePlayer
            currentStep={currentStep}
            maxStep={maxStep}
            isPlaying={isPlaying}
            onStepChange={setCurrentStep}
            onPlayPause={togglePlay}
            playbackSpeed={playbackSpeed}
            onSpeedChange={setPlaybackSpeed}
          />
        </div>
      )}
    </div>
  );
}
