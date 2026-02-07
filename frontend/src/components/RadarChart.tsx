'use client';

import React, { useMemo } from 'react';
import { cn } from '@/lib/utils';

interface RadarChartProps {
  data: { label: string; value: number; maxValue?: number }[];
  size?: number;
  className?: string;
  showLabels?: boolean;
  fillColor?: string;
  strokeColor?: string;
}

export function RadarChart({
  data,
  size = 200,
  className,
  showLabels = true,
  fillColor = 'rgba(114, 47, 55, 0.3)',
  strokeColor = '#722F37',
}: RadarChartProps) {
  const center = size / 2;
  const radius = (size / 2) * 0.7;
  const labelRadius = (size / 2) * 0.9;
  const numAxes = data.length;
  const angleStep = (2 * Math.PI) / numAxes;
  const startAngle = -Math.PI / 2;

  const axisPoints = useMemo(() => {
    return data.map((_, i) => {
      const angle = startAngle + i * angleStep;
      return {
        x: center + radius * Math.cos(angle),
        y: center + radius * Math.sin(angle),
        labelX: center + labelRadius * Math.cos(angle),
        labelY: center + labelRadius * Math.sin(angle),
        angle,
      };
    });
  }, [data, center, radius, labelRadius, angleStep, startAngle]);

  const dataPoints = useMemo(() => {
    return data.map((item, i) => {
      const maxVal = item.maxValue ?? 100;
      const normalizedValue = Math.min(item.value / maxVal, 1);
      const angle = startAngle + i * angleStep;
      return {
        x: center + radius * normalizedValue * Math.cos(angle),
        y: center + radius * normalizedValue * Math.sin(angle),
      };
    });
  }, [data, center, radius, angleStep, startAngle]);

  const dataPath = useMemo(() => {
    if (dataPoints.length === 0) return '';
    const points = dataPoints.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`));
    return points.join(' ') + ' Z';
  }, [dataPoints]);

  const gridPaths = useMemo(() => {
    const levels = [0.2, 0.4, 0.6, 0.8, 1.0];
    return levels.map((level) => {
      const points = Array.from({ length: numAxes }, (_, i) => {
        const angle = startAngle + i * angleStep;
        const x = center + radius * level * Math.cos(angle);
        const y = center + radius * level * Math.sin(angle);
        return i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
      });
      return points.join(' ') + ' Z';
    });
  }, [numAxes, center, radius, angleStep, startAngle]);

  if (data.length < 3) {
    return (
      <div className={cn('flex items-center justify-center text-gray-400 text-sm', className)} style={{ width: size, height: size }}>
        Minimum 3 data points required
      </div>
    );
  }

  return (
    <svg width={size} height={size} className={className} viewBox={`0 0 ${size} ${size}`}>
      {gridPaths.map((path, i) => (
        <path
          key={i}
          d={path}
          fill="none"
          stroke="#F7E7CE"
          strokeWidth={1}
          opacity={0.5 + i * 0.1}
        />
      ))}

      {axisPoints.map((point, i) => (
        <line
          key={i}
          x1={center}
          y1={center}
          x2={point.x}
          y2={point.y}
          stroke="#F7E7CE"
          strokeWidth={1}
        />
      ))}

      <path
        d={dataPath}
        fill={fillColor}
        stroke={strokeColor}
        strokeWidth={2}
        className="transition-all duration-500"
      />

      {dataPoints.map((point, i) => (
        <circle
          key={i}
          cx={point.x}
          cy={point.y}
          r={4}
          fill={strokeColor}
          stroke="white"
          strokeWidth={2}
          className="transition-all duration-300"
        />
      ))}

      {showLabels && axisPoints.map((point, i) => {
        const item = data[i];
        const maxVal = item.maxValue ?? 100;
        const textAnchor = point.angle > -Math.PI / 2 && point.angle < Math.PI / 2 ? 'start' : 'end';
        const isTop = point.angle < 0;
        const isCenter = Math.abs(point.angle + Math.PI / 2) < 0.1 || Math.abs(point.angle - Math.PI / 2) < 0.1;
        
        return (
          <g key={i}>
            <text
              x={point.labelX}
              y={point.labelY + (isTop ? -4 : 12)}
              textAnchor={isCenter ? 'middle' : textAnchor}
              className="fill-gray-700 text-[10px] font-medium"
            >
              {item.label}
            </text>
            <text
              x={point.labelX}
              y={point.labelY + (isTop ? 8 : 24)}
              textAnchor={isCenter ? 'middle' : textAnchor}
              className="fill-[#722F37] text-[9px] font-bold"
            >
              {item.value}/{maxVal}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
