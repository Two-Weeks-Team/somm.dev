import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TimelinePlayer } from '@/components/graph/TimelinePlayer';

describe('TimelinePlayer', () => {
  const mockOnStepChange = jest.fn();
  const mockOnPlayPause = jest.fn();
  const mockOnSpeedChange = jest.fn();

  beforeEach(() => {
    mockOnStepChange.mockClear();
    mockOnPlayPause.mockClear();
    mockOnSpeedChange.mockClear();
  });

  it('renders with initial values', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    expect(screen.getByText('Step 5/10')).toBeInTheDocument();
    expect(screen.getByLabelText('Play')).toBeInTheDocument();
  });

  it('renders with initial values at step 0', () => {
    render(
      <TimelinePlayer
        currentStep={0}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    expect(screen.getByText('Step 0/10')).toBeInTheDocument();
  });

  it('renders with initial values at max step', () => {
    render(
      <TimelinePlayer
        currentStep={10}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    expect(screen.getByText('Step 10/10')).toBeInTheDocument();
  });

  it('shows pause button when playing', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={true}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    expect(screen.getByLabelText('Pause')).toBeInTheDocument();
  });

  it('shows play button when paused', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    expect(screen.getByLabelText('Play')).toBeInTheDocument();
  });

  it('toggles play/pause when play button is clicked', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const playButton = screen.getByLabelText('Play');
    fireEvent.click(playButton);

    expect(mockOnPlayPause).toHaveBeenCalledTimes(1);
  });

  it('toggles play/pause when pause button is clicked', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={true}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const pauseButton = screen.getByLabelText('Pause');
    fireEvent.click(pauseButton);

    expect(mockOnPlayPause).toHaveBeenCalledTimes(1);
  });

  it('steps backward when previous button is clicked', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const prevButton = screen.getByLabelText('Previous step');
    fireEvent.click(prevButton);

    expect(mockOnStepChange).toHaveBeenCalledWith(4);
  });

  it('steps forward when next button is clicked', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const nextButton = screen.getByLabelText('Next step');
    fireEvent.click(nextButton);

    expect(mockOnStepChange).toHaveBeenCalledWith(6);
  });

  it('does not trigger onStepChange when clicking disabled previous button at step 0', () => {
    render(
      <TimelinePlayer
        currentStep={0}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const prevButton = screen.getByLabelText('Previous step');
    fireEvent.click(prevButton);

    expect(mockOnStepChange).not.toHaveBeenCalled();
  });

  it('does not trigger onStepChange when clicking disabled next button at max step', () => {
    render(
      <TimelinePlayer
        currentStep={10}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const nextButton = screen.getByLabelText('Next step');
    fireEvent.click(nextButton);

    expect(mockOnStepChange).not.toHaveBeenCalled();
  });

  it('disables previous button at step 0', () => {
    render(
      <TimelinePlayer
        currentStep={0}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const prevButton = screen.getByLabelText('Previous step');
    expect(prevButton).toBeDisabled();
  });

  it('disables next button at max step', () => {
    render(
      <TimelinePlayer
        currentStep={10}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const nextButton = screen.getByLabelText('Next step');
    expect(nextButton).toBeDisabled();
  });

  it('enables previous button when step > 0', () => {
    render(
      <TimelinePlayer
        currentStep={1}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const prevButton = screen.getByLabelText('Previous step');
    expect(prevButton).not.toBeDisabled();
  });

  it('enables next button when step < max step', () => {
    render(
      <TimelinePlayer
        currentStep={9}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const nextButton = screen.getByLabelText('Next step');
    expect(nextButton).not.toBeDisabled();
  });

  it('updates currentStep when slider value changes', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '7' } });

    expect(mockOnStepChange).toHaveBeenCalledWith(7);
  });

  it('renders slider with correct min, max, and value attributes', () => {
    render(
      <TimelinePlayer
        currentStep={3}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('min', '0');
    expect(slider).toHaveAttribute('max', '10');
    expect(slider).toHaveAttribute('value', '3');
  });

  it('renders speed selector when onSpeedChange is provided', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={1}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    expect(screen.getByText('0.5x')).toBeInTheDocument();
    expect(screen.getByText('1x')).toBeInTheDocument();
    expect(screen.getByText('2x')).toBeInTheDocument();
  });

  it('does not render speed selector when onSpeedChange is not provided', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    expect(screen.queryByText('0.5x')).not.toBeInTheDocument();
    expect(screen.queryByText('1x')).not.toBeInTheDocument();
    expect(screen.queryByText('2x')).not.toBeInTheDocument();
  });

  it('calls onSpeedChange when speed button is clicked', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={1}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    const speed05Button = screen.getByText('0.5x');
    fireEvent.click(speed05Button);

    expect(mockOnSpeedChange).toHaveBeenCalledWith(0.5);
  });

  it('calls onSpeedChange with correct speed values', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={1}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    fireEvent.click(screen.getByText('0.5x'));
    expect(mockOnSpeedChange).toHaveBeenCalledWith(0.5);

    fireEvent.click(screen.getByText('2x'));
    expect(mockOnSpeedChange).toHaveBeenCalledWith(2);
  });

  it('highlights the active speed button', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={2}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    const speed2Button = screen.getByText('2x');
    expect(speed2Button).toHaveClass('bg-[#722F37]', 'text-white');
  });

  it('triggers play/pause on space key press', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    fireEvent.keyDown(window, { key: ' ' });

    expect(mockOnPlayPause).toHaveBeenCalledTimes(1);
  });

  it('triggers step backward on ArrowLeft key press', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    fireEvent.keyDown(window, { key: 'ArrowLeft' });

    expect(mockOnStepChange).toHaveBeenCalledWith(4);
  });

  it('triggers step forward on ArrowRight key press', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    fireEvent.keyDown(window, { key: 'ArrowRight' });

    expect(mockOnStepChange).toHaveBeenCalledWith(6);
  });

  it('changes speed to 0.5x on key press 1', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={1}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    fireEvent.keyDown(window, { key: '1' });

    expect(mockOnSpeedChange).toHaveBeenCalledWith(0.5);
  });

  it('changes speed to 1x on key press 2', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={0.5}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    fireEvent.keyDown(window, { key: '2' });

    expect(mockOnSpeedChange).toHaveBeenCalledWith(1);
  });

  it('changes speed to 2x on key press 3', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={1}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    fireEvent.keyDown(window, { key: '3' });

    expect(mockOnSpeedChange).toHaveBeenCalledWith(2);
  });

  it('does not trigger keyboard shortcuts when typing in input', () => {
    render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
      />
    );

    const input = document.createElement('input');
    document.body.appendChild(input);
    input.focus();

    fireEvent.keyDown(input, { key: ' ' });

    expect(mockOnPlayPause).not.toHaveBeenCalled();

    document.body.removeChild(input);
  });

  it('matches snapshot when paused', () => {
    const { container } = render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={false}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={1}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot when playing', () => {
    const { container } = render(
      <TimelinePlayer
        currentStep={5}
        maxStep={10}
        isPlaying={true}
        onStepChange={mockOnStepChange}
        onPlayPause={mockOnPlayPause}
        playbackSpeed={2}
        onSpeedChange={mockOnSpeedChange}
      />
    );

    expect(container.firstChild).toMatchSnapshot();
  });
});
