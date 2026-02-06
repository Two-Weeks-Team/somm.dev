# LangGraph Server & Monitoring Setup

This guide covers setting up LangGraph Server for local development and LangSmith for production monitoring.

## Quick Start

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy and edit)
cp .env.example .env

# Start LangGraph development server
langgraph dev
```

Open http://localhost:8123 for LangGraph Studio UI.

## Configuration

### langgraph.json

The server configuration file at `backend/langgraph.json`:

```json
{
  "graphs": {
    "evaluation": "./app/graph:evaluation_graph"
  },
  "env": ".env",
  "python_version": "3.12",
  "dependencies": ["./requirements.txt"]
}
```

| Field | Description |
|-------|-------------|
| `graphs` | Map of graph name to module path (format: `module:attribute`) |
| `env` | Environment file to load |
| `python_version` | Python version for the server |
| `dependencies` | Dependency files to install |

### Environment Variables

Add to your `.env` file for LangSmith tracing:

```bash
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_TRACING=true
LANGCHAIN_PROJECT=somm-dev-local
```

Get your API key from: https://smith.langchain.com/settings

## LangGraph CLI Commands

| Command | Description |
|---------|-------------|
| `langgraph dev` | Start development server with hot reload |
| `langgraph up` | Start production server |
| `langgraph build` | Build Docker image |
| `langgraph dockerfile` | Generate Dockerfile |

### Development Mode

```bash
cd backend
langgraph dev
```

Features:
- Hot reload on code changes
- LangGraph Studio UI at http://localhost:8123
- API at http://localhost:8123/api

### Testing a Graph Run

Via LangGraph Studio:
1. Open http://localhost:8123
2. Select "evaluation" graph
3. Input initial state and run

Via API:
```bash
curl -X POST http://localhost:8123/api/runs \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "evaluation",
    "input": {
      "repo_url": "https://github.com/user/repo",
      "evaluation_criteria": "basic",
      "repo_context": {},
      "user_id": "test-user"
    }
  }'
```

## LangSmith Monitoring

When `LANGSMITH_TRACING=true`, all graph executions are traced to LangSmith.

### Viewing Traces

1. Go to https://smith.langchain.com
2. Select your project (configured via `LANGCHAIN_PROJECT`)
3. View runs with full node-by-node execution traces

### What Gets Traced

- Graph invocation start/end
- Each node execution (marcel, isabella, heinrich, sofia, laurent, jeanpierre)
- LLM calls with input/output
- Token usage and latency
- Errors and exceptions

### Failure Case: Missing API Key

If `LANGSMITH_API_KEY` is not set but `LANGSMITH_TRACING=true`:
- Server will start normally
- Traces will fail silently (no crash)
- Check logs for LangSmith connection warnings

## Deployment Modes

### Self-Hosted (Recommended)

> [!CAUTION]
> **Security Warning**: LangGraph Server does not have built-in authentication. Do not expose port 8123 to the public internet without a reverse proxy (e.g., Nginx, Apache) that handles authentication. Unauthenticated access allows:
> - Unauthorized LLM usage (consuming API credits)
> - User impersonation via `user_id` in request JSON
> - Access to sensitive evaluation data

Deploy using Docker:

```bash
cd backend
langgraph build -t somm-langgraph:latest
docker run -p 8123:8123 --env-file .env somm-langgraph:latest
```

Or use the generated Dockerfile:

```bash
langgraph dockerfile > Dockerfile.langgraph
docker build -f Dockerfile.langgraph -t somm-langgraph .
```

### LangGraph Cloud

For managed deployment:
1. Push code to GitHub
2. Connect repo in LangGraph Cloud console
3. Configure environment variables
4. Deploy

See: https://langchain-ai.github.io/langgraph/cloud/

## Troubleshooting

### Graph Not Found

```
Error: No graph found at app.graph:evaluation_graph
```

Fix: Ensure `backend/app/graph/__init__.py` exports `evaluation_graph`.

### Database Connection Error

```
Error: MongoDB connection failed
```

The graph uses lazy loading. Ensure MongoDB is running or set `MONGODB_URI` correctly.

### Import Test

Verify the graph export works:

```bash
cd backend
python -c "from app.graph import evaluation_graph; print(type(evaluation_graph))"
```

Expected output: `<class 'langgraph.graph.state.CompiledStateGraph'>`
