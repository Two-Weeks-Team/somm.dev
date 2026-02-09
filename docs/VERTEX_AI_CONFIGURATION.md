# Vertex AI Configuration Guide

## Final Configuration (2026-02-09)

### Single API Key Architecture

All LLM calls use **VERTEX_API_KEY only** with `vertexai=True`.

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key=VERTEX_API_KEY,
    vertexai=True,
)
```

### Environment Variables

```bash
# .env - Only VERTEX_API_KEY required
VERTEX_API_KEY=AQ.Ab8RN6KKSS-...

# Do NOT set these (triggers ADC lookup failure):
# GOOGLE_CLOUD_PROJECT=xxx
# GOOGLE_CLOUD_LOCATION=xxx
```

### Supported Models

| Model | Status |
|-------|--------|
| `gemini-3-flash-preview` | Available |
| `gemini-3-pro-preview` | Available |
| `gemini-2.0-flash` | NOT available (404) |

### thinking_level Configuration

| Model | thinking_level |
|-------|----------------|
| gemini-3-flash-preview | `minimal` |
| gemini-3-pro-preview | `low` |

## Test Results

```
[1] provider='vertex' + gemini-3-flash-preview: SUCCESS
[2] provider='gemini' + gemini-3-flash-preview: SUCCESS (uses VERTEX_API_KEY)
[3] provider='vertex' + gemini-3-pro-preview: SUCCESS
```

## Root Cause of Previous 401 Errors

1. **Wrong Project ID**: `.env` had `GOOGLE_CLOUD_PROJECT=somm-dev-486901` (incorrect)
2. **ADC Lookup**: Setting `project` parameter triggers ADC lookup, fails without gcloud credentials
3. **Solution**: Remove `GOOGLE_CLOUD_PROJECT` from `.env`, use only `VERTEX_API_KEY`

## Code Changes

### llm.py
- Unified all providers to use `VERTEX_API_KEY` with `vertexai=True`
- Removed separate gemini/vertex provider logic
- BYOK users can still provide their own key

### .env
- Removed `GEMINI_API_KEY` (not needed)
- Removed `GOOGLE_CLOUD_PROJECT` (causes ADC lookup)
- Only `VERTEX_API_KEY` required

## References

- [LangChain ChatGoogleGenerativeAI Docs](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai)
- [GitHub Issue #1473](https://github.com/langchain-ai/langchain-google/issues/1473) - ADC lookup issue
