'use client';

import React, { useEffect, useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';
import { Graph3DPayload } from '@/types/graph';
import { TimelinePlayer } from './graph/TimelinePlayer';
import { useTimelinePlayer } from '@/hooks/useTimelinePlayer';

interface Graph3DTabProps {
  evaluationId: string;
}

const GraphView3D = dynamic(() => import('./graph/GraphView3D'), {
  ssr: false,
  loading: () => (
    <div className="flex flex-col items-center justify-center h-full text-white">
      <Loader2 className="w-10 h-10 text-[#722F37] animate-spin mb-4" />
      <p className="text-gray-500">Loading 3D Engine...</p>
    </div>
  ),
});

export function Graph3DTab({ evaluationId }: Graph3DTabProps) {
  const [data, setData] = useState<Graph3DPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [maxStep, setMaxStep] = useState(0);

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
      <div className="flex flex-col items-center justify-center h-[600px] bg-white rounded-2xl shadow-sm border border-gray-100">
        <Loader2 className="w-10 h-10 text-[#722F37] animate-spin mb-4" />
        <p className="text-gray-500 font-medium">Loading 3D graph visualization...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] bg-white rounded-2xl shadow-sm border border-gray-100">
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
    <div className="flex flex-col gap-4">
      <div className="h-[600px] bg-neutral-900 rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <GraphView3D data={data} currentStep={currentStep} />
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
  );
}
