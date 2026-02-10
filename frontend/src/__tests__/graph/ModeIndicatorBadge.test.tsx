import React from 'react';
import { render, screen } from '@testing-library/react';
import { ModeIndicatorBadge } from '@/components/ModeIndicatorBadge';

describe('ModeIndicatorBadge', () => {
  it('renders "Standard Tasting" for six_hats mode', () => {
    render(<ModeIndicatorBadge mode="six_hats" />);

    expect(screen.getByText('Standard Tasting')).toBeInTheDocument();
  });

  it('renders "Grand Tasting" for full_techniques mode', () => {
    render(<ModeIndicatorBadge mode="full_techniques" />);

    expect(screen.getByText('Grand Tasting')).toBeInTheDocument();
  });

  it('renders description text for Standard Tasting', () => {
    render(<ModeIndicatorBadge mode="six_hats" />);

    expect(screen.getByText('Six Sommeliers · ~2min')).toBeInTheDocument();
  });

  it('renders description text for Grand Tasting', () => {
    render(<ModeIndicatorBadge mode="full_techniques" />);

    expect(screen.getByText('Sommelier Masterclass · 75 techniques · ~10min')).toBeInTheDocument();
  });

  it('renders Wine icon for six_hats mode', () => {
    const { container } = render(<ModeIndicatorBadge mode="six_hats" />);

    const wineIcon = container.querySelector('svg');
    expect(wineIcon).toBeInTheDocument();
  });

  it('renders Trophy icon for full_techniques mode', () => {
    const { container } = render(<ModeIndicatorBadge mode="full_techniques" />);

    const trophyIcon = container.querySelector('svg');
    expect(trophyIcon).toBeInTheDocument();
  });

  it('applies burgundy styling for six_hats mode', () => {
    render(<ModeIndicatorBadge mode="six_hats" />);

    const badge = screen.getByText('Standard Tasting').closest('div')?.parentElement;
    expect(badge).toHaveClass('from-[#F7E7CE]/30', 'to-[#F7E7CE]/10');
  });

  it('applies amber styling for full_techniques mode', () => {
    render(<ModeIndicatorBadge mode="full_techniques" />);

    const badge = screen.getByText('Grand Tasting').closest('div')?.parentElement;
    expect(badge).toHaveClass('from-amber-50', 'to-yellow-50');
  });

  it('renders six_hats as default for unknown mode strings', () => {
    render(<ModeIndicatorBadge mode="unknown_mode" as GraphEvaluationMode />);

    expect(screen.getByText('Standard Tasting')).toBeInTheDocument();
  });

  it('has correct border styling for six_hats mode', () => {
    render(<ModeIndicatorBadge mode="six_hats" />);

    const badge = screen.getByText('Standard Tasting').closest('div')?.parentElement;
    expect(badge).toHaveClass('border-[#F7E7CE]');
  });

  it('has correct border styling for full_techniques mode', () => {
    render(<ModeIndicatorBadge mode="full_techniques" />);

    const badge = screen.getByText('Grand Tasting').closest('div')?.parentElement;
    expect(badge).toHaveClass('border-amber-200');
  });

  it('matches snapshot for six_hats mode', () => {
    const { container } = render(<ModeIndicatorBadge mode="six_hats" />);

    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot for full_techniques mode', () => {
    const { container } = render(<ModeIndicatorBadge mode="full_techniques" />);

    expect(container.firstChild).toMatchSnapshot();
  });
});
