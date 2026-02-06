import React from 'react';
import { render, screen } from '@testing-library/react';
import { GraphSkeleton } from '@/components/graph/GraphSkeleton';

describe('GraphSkeleton', () => {
  it('renders skeleton container', () => {
    const { container } = render(<GraphSkeleton />);

    const skeletonContainer = container.firstChild;
    expect(skeletonContainer).toBeInTheDocument();
  });

  it('renders loading text', () => {
    render(<GraphSkeleton />);

    expect(screen.getByText('Decanting your graph...')).toBeInTheDocument();
  });

  it('renders 9 placeholder nodes in a grid', () => {
    const { container } = render(<GraphSkeleton />);

    const gridContainer = container.querySelector('.grid');
    expect(gridContainer).toBeInTheDocument();

    const pulseElements = container.querySelectorAll('.animate-pulse');
    expect(pulseElements.length).toBeGreaterThanOrEqual(9);
  });

  it('renders bouncing dots at the bottom', () => {
    const { container } = render(<GraphSkeleton />);

    const bounceElements = container.querySelectorAll('.animate-bounce');
    expect(bounceElements.length).toBe(3);
  });

  it('has shimmer animation element', () => {
    const { container } = render(<GraphSkeleton />);

    const shimmerElement = container.querySelector('.animate-shimmer');
    expect(shimmerElement).toBeInTheDocument();
  });

  it('has correct background styling', () => {
    const { container } = render(<GraphSkeleton />);

    const skeletonContainer = container.firstChild as HTMLElement;
    expect(skeletonContainer).toHaveClass('bg-neutral-50/50');
  });

  it('has rounded corners', () => {
    const { container } = render(<GraphSkeleton />);

    const skeletonContainer = container.firstChild as HTMLElement;
    expect(skeletonContainer).toHaveClass('rounded-lg');
  });

  it('has border styling', () => {
    const { container } = render(<GraphSkeleton />);

    const skeletonContainer = container.firstChild as HTMLElement;
    expect(skeletonContainer).toHaveClass('border', 'border-neutral-200');
  });

  it('renders radial gradient background pattern', () => {
    const { container } = render(<GraphSkeleton />);

    const radialBackground = container.querySelector('.opacity-10');
    expect(radialBackground).toBeInTheDocument();
    expect(radialBackground).toHaveStyle({
      backgroundImage: 'radial-gradient(#722F37 1px, transparent 1px)',
    });
  });

  it('renders SVG with connecting lines', () => {
    const { container } = render(<GraphSkeleton />);

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();

    const path = svg?.querySelector('path');
    expect(path).toBeInTheDocument();
  });

  it('renders pulse animation with staggered delays', () => {
    const { container } = render(<GraphSkeleton />);

    const gridItems = container.querySelectorAll('.grid > div');
    expect(gridItems.length).toBe(9);

    gridItems.forEach((item, index) => {
      expect(item).toHaveStyle({
        animationDelay: `${index * 100}ms`,
      });
    });
  });

  it('matches snapshot', () => {
    const { container } = render(<GraphSkeleton />);

    expect(container.firstChild).toMatchSnapshot();
  });
});
