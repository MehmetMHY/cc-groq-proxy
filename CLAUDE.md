# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI proxy server that enables using any text-based model hosted on Groq with Claude Code CLI, providing significant cost savings while maintaining strong performance for coding tasks. It translates between Anthropic's API format and Groq's OpenAI-compatible format.

## Commands

### Docker-based Setup (Recommended)

```bash
# Set your Groq API key
export GROQ_API_KEY=your_groq_api_key_here

# Build the Docker image
python run.py build

# Start the proxy with interactive model/token selection (requires fzf)
python run.py run

# Alternative: Start with specific model and token limit
docker run -d --name cc-groq-proxy -p 7187:7187 \
  -e GROQ_API_KEY=your_key \
  claude-code-groq-proxy \
  python proxy.py --model llama-3.1-70b-versatile --max-tokens 8192
```

### Local Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the proxy server directly
python proxy.py

# Run with specific model and token settings
python proxy.py --model openai/gpt-oss-120b --max-tokens 16384
```

### Using with Claude Code

```bash
# Set environment variables to redirect Claude Code to the proxy
export ANTHROPIC_BASE_URL=http://localhost:7187
export ANTHROPIC_API_KEY=NOT_NEEDED

# Run Claude Code as normal
claude

# Or use the convenience script that handles env vars automatically
./call.sh
```

### Management Commands

```bash
# Container management
python run.py stop      # Stop the proxy container
python run.py status    # Show container status and resource usage
python run.py logs      # View container logs
python run.py follow    # Follow container logs in real-time
```

## Architecture

### Core Components

1. **proxy.py** - Main proxy server implementation

   - FastAPI application that intercepts Anthropic API calls
   - Converts Anthropic message format to OpenAI format for Groq
   - Handles tool use blocks and converts between formats
   - Returns responses in Anthropic's expected format (no streaming in this version)
   - Rich logging with colored output showing input/output content and token usage

2. **run.py** - Docker management script

   - Builds Docker images and manages containers
   - Interactive model selection using fzf
   - Interactive token limit selection (4096 to 1,048,576 tokens)
   - Container lifecycle management (start/stop/status/logs)

3. **call.sh** - Convenience script for Claude Code
   - Automatically sets proxy environment variables
   - Launches Claude Code CLI
   - Cleans up environment variables after use

### Key Technical Details

- **Default Model**: Uses `openai/gpt-oss-120b` by default (configurable via --model)
- **Token Limits**: Default 16384 tokens, configurable via --max-tokens up to 1M+ tokens
- **Port**: Runs on port 7187 by default
- **Authentication**: Requires `GROQ_API_KEY` in environment
- **Message Conversion**: Handles system prompts, user messages, assistant responses, and tool use blocks
- **Logging**: Rich colored output with request/response details and token usage tracking
- **Model Support**: Works with any text-based model available on Groq (Kimi K2, Llama, Mixtral, etc.)

### Environment Variables

- `GROQ_API_KEY` - Required for Groq API access
- `ANTHROPIC_BASE_URL` - Set to http://localhost:7187 when using the proxy
- `ANTHROPIC_API_KEY` - Can be set to any value when using the proxy

### Docker Configuration

- **Image Name**: `claude-code-groq-proxy`
- **Container Name**: `cc-groq-proxy`
- **Base Image**: `python:3.11-slim`
- **Dependencies**: Listed in requirements.txt (FastAPI, uvicorn, openai, rich, etc.)
