# Performance Benchmark Report

> **Generated**: 2026-02-07
> **Status**: Initial baseline (mock data - run actual benchmarks to update)

## Executive Summary

This report compares the performance characteristics of **Six Sommeliers** (standard mode) 
and **Grand Tasting** (comprehensive 75-technique mode) evaluation pipelines.

## Methodology

### Test Environment
- **Python Version**: 3.12+
- **Framework**: LangGraph + FastAPI
- **LLM Provider**: Gemini Flash
- **Iterations**: 10 per mode (recommended minimum)

### Input Data
- Standard repository evaluation request
- Consistent input across all iterations

### Running Benchmarks

```bash
cd backend
python -m benchmarks.benchmark_modes --iterations 10 --output results.json
```

## Expected Results

### Latency Comparison

| Metric | Six Sommeliers | Grand Tasting | Expected Ratio |
|--------|----------------|---------------|----------------|
| P50 | ~2,000 ms | ~4,500 ms | ~2.25x |
| P90 | ~2,500 ms | ~5,500 ms | ~2.2x |
| P99 | ~3,000 ms | ~6,500 ms | ~2.1x |
| Mean | ~2,200 ms | ~5,000 ms | ~2.3x |

### Memory Usage

| Mode | Expected Peak Memory |
|------|---------------------|
| Six Sommeliers | ~256 MB |
| Grand Tasting | ~384 MB |
| **Expected Ratio** | **~1.5x** |

### Token Consumption

| Mode | Expected Tokens per Evaluation |
|------|-------------------------------|
| Six Sommeliers | ~5,000 |
| Grand Tasting | ~15,000 |
| **Expected Ratio** | **~3x** |

## Performance Targets

| Target | Threshold | Rationale |
|--------|-----------|-----------|
| Grand Tasting latency < 2x Six Sommeliers | < 2.0x | User experience acceptable for comprehensive analysis |
| Memory usage < 1.5x baseline | < 1.5x | Prevent OOM on standard servers |
| No memory leaks | 0 leaked bytes | Long-running stability |
| Success rate > 95% | > 95% | Production reliability |

## Architecture Considerations

### Six Sommeliers Mode
- 6 parallel agent executions (Marcel, Isabella, Heinrich, Sofia, Laurent)
- 1 synthesis node (Jean-Pierre)
- Fan-out → Fan-in pattern
- ~2 seconds total latency

### Grand Tasting Mode
- 8 category groups with 75 total techniques
- Batched parallel execution within categories
- More LLM round-trips for comprehensive analysis
- ~5 seconds total latency

## Optimization Strategies

### Implemented
1. **Parallel Execution**: LangGraph fan-out pattern for concurrent agent runs
2. **SSE Streaming**: Real-time progress updates for perceived performance
3. **Caching**: Result caching via cache_service for repeated evaluations

### Recommended Future Optimizations
1. **Technique Batching**: Group similar techniques to reduce LLM calls
2. **Prompt Optimization**: Reduce token usage in technique prompts
3. **Result Caching**: Cache intermediate results for faster re-evaluation
4. **Model Selection**: Use faster models for simple techniques

## Appendix

### Benchmark Script Location
- `backend/benchmarks/benchmark_modes.py`

### Result Storage
- JSON results: `backend/benchmarks/results/`

### Updating This Report
Run the benchmark script with `--report` flag to auto-generate updated statistics:

```bash
cd backend
python -m benchmarks.benchmark_modes --iterations 20 --report ../../docs/PERFORMANCE_BENCHMARK.md
```
