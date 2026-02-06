import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResultTabs } from '@/components/ResultTabs';

// Mock window.location and window.history
const mockReplaceState = jest.fn();
Object.defineProperty(window, 'location', {
  value: { hash: '' },
  writable: true,
});
Object.defineProperty(window, 'history', {
  value: { replaceState: mockReplaceState },
  writable: true,
});

describe('ResultTabs', () => {
  const mockOnTabChange = jest.fn();

  beforeEach(() => {
    mockOnTabChange.mockClear();
    mockReplaceState.mockClear();
    window.location.hash = '';
  });

  afterEach(() => {
    // Clean up event listeners
    window.removeEventListener('keydown', expect.any(Function));
  });

  it('renders all tabs correctly', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    expect(screen.getByRole('tab', { name: /Tasting Notes/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /2D Graph/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /3D Graph/i })).toBeInTheDocument();
  });

  it('marks the active tab as selected', () => {
    render(
      <ResultTabs activeTab="graph-2d" onTabChange={mockOnTabChange} />
    );

    const tastingTab = screen.getByRole('tab', { name: /Tasting Notes/i });
    const graph2dTab = screen.getByRole('tab', { name: /2D Graph/i });
    const graph3dTab = screen.getByRole('tab', { name: /3D Graph/i });

    expect(tastingTab).toHaveAttribute('aria-selected', 'false');
    expect(graph2dTab).toHaveAttribute('aria-selected', 'true');
    expect(graph3dTab).toHaveAttribute('aria-selected', 'false');
  });

  it('hides 3D tab on mobile (mobileHidden prop)', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    const graph3dTab = screen.getByRole('tab', { name: /3D Graph/i });
    expect(graph3dTab).toHaveClass('hidden', 'md:flex');
  });

  it('does not hide tasting or 2D tabs on mobile', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    const tastingTab = screen.getByRole('tab', { name: /Tasting Notes/i });
    const graph2dTab = screen.getByRole('tab', { name: /2D Graph/i });

    expect(tastingTab).not.toHaveClass('hidden');
    expect(graph2dTab).not.toHaveClass('hidden');
  });

  it('calls onTabChange when a tab is clicked', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    const graph2dTab = screen.getByRole('tab', { name: /2D Graph/i });
    fireEvent.click(graph2dTab);

    expect(mockOnTabChange).toHaveBeenCalledWith('graph-2d');
  });

  it('updates URL hash when tab is clicked', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    const graph3dTab = screen.getByRole('tab', { name: /3D Graph/i });
    fireEvent.click(graph3dTab);

    expect(mockReplaceState).toHaveBeenCalledWith(null, '', '#graph-3d');
  });

  it('handles keyboard navigation with ArrowRight', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    fireEvent.keyDown(window, { key: 'ArrowRight' });

    expect(mockOnTabChange).toHaveBeenCalledWith('graph-2d');
  });

  it('handles keyboard navigation with ArrowLeft', () => {
    render(
      <ResultTabs activeTab="graph-2d" onTabChange={mockOnTabChange} />
    );

    fireEvent.keyDown(window, { key: 'ArrowLeft' });

    expect(mockOnTabChange).toHaveBeenCalledWith('tasting');
  });

  it('wraps around to first tab when pressing ArrowRight on last tab', () => {
    render(
      <ResultTabs activeTab="graph-3d" onTabChange={mockOnTabChange} />
    );

    fireEvent.keyDown(window, { key: 'ArrowRight' });

    expect(mockOnTabChange).toHaveBeenCalledWith('tasting');
  });

  it('wraps around to last tab when pressing ArrowLeft on first tab', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    fireEvent.keyDown(window, { key: 'ArrowLeft' });

    expect(mockOnTabChange).toHaveBeenCalledWith('graph-3d');
  });

  it('renders correctly when hash is set (hash handling is now in useResultTab hook)', () => {
    window.location.hash = '#graph-2d';

    render(
      <ResultTabs activeTab="graph-2d" onTabChange={mockOnTabChange} />
    );

    const graph2dTab = screen.getByRole('tab', { name: /2D Graph/i });
    expect(graph2dTab).toHaveAttribute('aria-selected', 'true');
  });

  it('has correct active styling for selected tab', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    const tastingTab = screen.getByRole('tab', { name: /Tasting Notes/i });
    expect(tastingTab).toHaveClass('text-[#722F37]', 'border-[#722F37]');
  });

  it('has correct inactive styling for unselected tabs', () => {
    render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    const graph2dTab = screen.getByRole('tab', { name: /2D Graph/i });
    expect(graph2dTab).toHaveClass('text-gray-600', 'border-transparent');
  });

  it('matches snapshot', () => {
    const { container } = render(
      <ResultTabs activeTab="tasting" onTabChange={mockOnTabChange} />
    );

    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot with graph-2d active', () => {
    const { container } = render(
      <ResultTabs activeTab="graph-2d" onTabChange={mockOnTabChange} />
    );

    expect(container.firstChild).toMatchSnapshot();
  });
});
