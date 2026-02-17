# SWL Agent Deployment Guide

## Quick Start

```bash
# Clone the repo
git clone https://github.com/Nil4s/swl-agent.git
cd swl-agent

# Install dependencies
pip install -r requirements.txt

# Set API key (optional, for hybrid mode)
export GEMINI_API_KEY="your-key-here"

# Run 100-agent swarm test
python swl_swarm_sync_test.py --mode audio_fm --agents 100 --iters 30 --plot
```

## Docker Deployment

```bash
# Build image
docker build -t swl-agent .

# Run API server
docker run -p 8000:8000 -e GEMINI_API_KEY=$GEMINI_API_KEY swl-agent

# Test endpoint
curl http://localhost:8000/api/swl/stats
```

## Moltbook Integration

```bash
# Start agent server
python moltbook_agent.py --mode server --port 8000

# Query endpoint
curl -X POST http://localhost:8000/api/swl/query \
  -H "Content-Type: application/json" \
  -d '{"query": "help with pathfinding", "mode": "human"}'
```

## Production Deploy

### Environment Variables
- `GEMINI_API_KEY` - Google Gemini API key (optional)
- `SWL_MODE` - Communication mode: `chord`, `mix`, or `fm` (default: `fm`)
- `SWL_PORT` - API server port (default: 8000)

### Resource Requirements
- **CPU**: 0.1 cores per agent
- **RAM**: 50 MB per agent
- **Storage**: 10 MB per agent

### Scaling
- Tested: 100 agents
- Theoretical: 1000+ agents
- Cost: $2 per 1K queries (96% cheaper than traditional)

## CI/CD

GitHub Actions automatically:
- Run tests on push
- Validate SWL encoding/decoding
- Check 40-concept vocabulary

## Support

- **Issues**: https://github.com/Nil4s/swl-agent/issues
- **Documentation**: See README.md
- **Cost Analysis**: 96% savings proven in DEPLOYMENT_REPORT_FEB_2026.md
