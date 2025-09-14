# Claude Code Groq Proxy

## About

A FastAPI proxy server that enables using any text-based model hosted on Groq with [Claude Code CLI](https://github.com/anthropics/claude-code), providing significant cost savings while maintaining strong performance for coding tasks.

## Getting Started

### Prerequisites

#### Required Dependencies

- [Docker](https://www.docker.com/get-started/): Container platform for running the proxy
- [Groq API Key](https://console.groq.com/): Sign up for free API access to Groq's models
- [Claude Code CLI](https://github.com/anthropics/claude-code): Anthropic's command-line interface

#### Optional Dependencies

- [fzf](https://github.com/junegunn/fzf): Fuzzy finder for interactive model and token selection
- [Python 3.8+](https://www.python.org/): Only needed for local development (not Docker usage)
- [pip](https://pip.pypa.io/en/stable/installation/): Python package manager (for local development)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/MehmetMHY/cc-groq-proxy.git
cd cc-groq-proxy
```

2. Configure your Groq API key:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

3. Build and run with Docker:

```bash
# Build the Docker image
./run.sh build

# Start the proxy (interactive model/token selection with fzf)
./run.sh run

# Or specify model and tokens directly
./run.sh --model llama-3.1-70b-versatile --max-tokens 8192 run
```

### Usage

Configure Claude Code to use the proxy:

```bash
export ANTHROPIC_BASE_URL=http://localhost:7187
export ANTHROPIC_API_KEY=NOT_NEEDED
claude
```

The proxy will now route Claude Code requests through your selected Groq model. Choose from various models including Kimi K2, Llama, Mixtral, and other text-based models available on Groq's platform.

#### Quick Start Script

For convenience, use the included `call.sh` script that automatically configures the environment and launches Claude Code:

```bash
./call.sh
```

This script sets the proxy URL, starts Claude Code, and cleans up the environment variables when done.

## Management Commands

The `run.sh` script provides several commands for managing the proxy:

```bash
# Build the Docker image
./run.sh build

# Start the proxy container (interactive selection)
./run.sh run

# Stop the proxy container
./run.sh stop

# Show container status and resource usage
./run.sh status

# View container logs
./run.sh logs

# Follow container logs in real-time
./run.sh follow

# Show help
./run.sh --help
```

## Features

- **Universal Groq Model Support**: Works with any text-based model on Groq (OpenAI OSS, Kimi K2, Llama, etc)
- **Interactive Model Selection**: Uses `fzf` to browse and select from available Groq models
- **Token Limit Configuration**: Choose from 4096 to 1,048,576 tokens in 1024 increments
- **Detailed Logging**: View input/output content and token usage for debugging
- **Docker-based**: Easy deployment and management with zero local Python setup
- **Cost Monitoring**: Track token usage per request
- **Convenience Scripts**: Quick setup with `call.sh` and comprehensive management with `run.sh`

## Feedback

Share your experience using different Groq models compared to Claude by opening an issue. Your feedback helps improve this tool.

## Acknowledgements

Inspired by [claude-code-proxy](https://github.com/1rgs/claude-code-proxy) and this repo is a fork of [fakerybakery/claude-code-kimi-groq](https://github.com/fakerybakery/claude-code-kimi-groq).

## License

This code base is licensed under the MIT License. See [LICENSE](./LICENSE.md) for more details.

## Evaluation Report (09/07/2025)

### 09/07/2025

#### Overview

Anthropic's Claude models Sonnet 4 and Opus 4.1 are used in [Claude Code CLI](https://github.com/anthropics/claude-code). These models are powerful but expensive for large-scale coding and writing tasks. By redirecting **Claude Code CLI** through a local proxy to **Groq's `moonshotai/kimi-k2-instruct-0905`**, this evaluation tested whether Kimi can serve as a cost-effective substitute without sacrificing too much quality.

#### Pricing Comparison

- **Claude Sonnet 4**: $3/M input, $15/M output
- **Claude Opus 4.1**: $15/M input, $75/M output
- **Groq Kimi K2-0905**: $1/M input, $3/M output

This makes Kimi **67–93% cheaper on input** and **80–96% cheaper on output**, depending on which Claude tier you compare against.

#### Performance

- **Coding**: Kimi scores ~70–80% as strong as Claude Sonnet/Opus in benchmarked tasks. It trails slightly on curated coding sets but sometimes matches or exceeds in interactive coding (e.g., LiveCodeBench).
- **Writing**: Comparable technical writing performance, though Claude remains more polished on complex narrative tasks.
- **Context**: Kimi supports ~262k tokens vs Claude’s 1M, but this is sufficient for most CLI use cases.

#### Conclusion

For most **day-to-day Claude Code CLI tasks** (bug fixes, refactoring, tool use, documentation), Kimi provides **substantial cost savings with only moderate quality trade-offs**. Claude Sonnet/Opus are still preferable for the most demanding, long-context, or mission-critical tasks, but **using Kimi via the proxy is a highly economical default option**.
