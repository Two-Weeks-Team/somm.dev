import { DimensionData } from '@/types';
import { DimensionCard } from './DimensionCard';
import { ItemTile } from './ItemTile';

interface BMADScorecardProps {
  dimensionScores: Record<string, DimensionData>;
}

export function BMADScorecard({ dimensionScores }: BMADScorecardProps) {
  const sortedDimensions = ['A', 'B', 'C', 'D']
    .map(id => dimensionScores[id])
    .filter(Boolean);

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-4">Dimension Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {sortedDimensions.map((dim) => (
            <DimensionCard key={dim.id} dimension={dim} />
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-4">Detailed Scorecard</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {sortedDimensions.flatMap((dim) =>
            dim.items.map((item) => (
              <ItemTile key={`${dim.id}-${item.id}`} item={item} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
