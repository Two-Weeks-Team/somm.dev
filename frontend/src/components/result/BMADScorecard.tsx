import { DimensionData, ItemData } from '@/types';
import { DimensionCard } from './DimensionCard';
import { ItemTile } from './ItemTile';

interface BMADScorecardProps {
  itemScores: Record<string, ItemData>;
  dimensionScores: Record<string, DimensionData>;
}

export function BMADScorecard({ dimensionScores }: BMADScorecardProps) {
  const sortedDimensions = ['A', 'B', 'C', 'D']
    .map(id => dimensionScores[id])
    .filter(Boolean);

  const allItems = sortedDimensions.flatMap(dim => dim.items);

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
          {allItems.map((item) => (
            <ItemTile key={item.id} item={item} />
          ))}
        </div>
      </div>
    </div>
  );
}
