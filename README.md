# Claude Code Groq Proxy

> **📦 Archive Notice**
>
> As of **October 21, 2025**, the `ccg` project is no longer actively maintained. Anthropic's [Claude Haiku 4.5](https://www.anthropic.com/news/claude-haiku-4-5) was recently released and offers exceptional performance and pricing that rivals Groq's best hosted models, making this proxy largely redundant. For most **Claude Code CLI** use cases, using **Haiku 4.5** directly is the recommended approach. Models will come and go, but **Claude Haiku 4.5** shows that models will get better and cheaper over time, making `ccg` increasingly redundant as time moves on.

## About

Claude Code Groq Proxy (`ccg`) is a FastAPI proxy server that enables using any text-based model hosted on Groq with [Claude Code CLI](https://github.com/anthropics/claude-code), providing significant cost savings while maintaining strong performance for coding tasks.

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

2. Run the installer to make the `ccg` command available system-wide:

```bash
# this command simplifies all interactions with the proxy
bash install.sh
```

3. Configure your Groq API key:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

### Command-Line Wrapper (`ccg`)

The `ccg` command is a convenient wrapper for managing the proxy.

- **`ccg`**: Starts the proxy and Claude Code.
- **`ccg -c [args]`**: Pass arguments directly to `cli.py` for management tasks (e.g., `ccg -c --build`, `ccg -c --stop`).
- **`ccg -p`**: Prints the project's installation path. Use with `cd $(ccg -p)` to navigate to the directory.
- **`ccg -h`**: Shows the help menu.

### Usage

Once the proxy is running (using the `ccg` command), configure Claude Code to use it in a separate terminal:

```bash
export ANTHROPIC_BASE_URL=http://localhost:7187
export ANTHROPIC_API_KEY=NOT_NEEDED
claude
```

The proxy will now route Claude Code requests through your selected Groq model. Choose from various models including Kimi K2, Llama, Mixtral, and other text-based models available on Groq's platform.

## Management Commands

The `cli.py` script provides several commands for managing the proxy:

```bash
# Build the Docker image
python cli.py --build     # or python cli.py -b

# Start the proxy container (interactive selection)
python cli.py --run       # or python cli.py -r

# Stop the proxy container
python cli.py --stop      # or python cli.py -s

# Show container status and resource usage
python cli.py --status    # or python cli.py -t

# View container logs
python cli.py --logs      # or python cli.py -l

# Follow container logs in real-time
python cli.py --follow    # or python cli.py -f

# Reset container (stop → build → run)
python cli.py --reset     # or python cli.py -x

# Show help (default when no options provided)
python cli.py --help      # or python cli.py
```

## Advanced Usage

For direct Docker control without the management script:

```bash
# Build image manually
docker build -t claude-code-groq-proxy .

# Run with specific model and token limit
docker run -d --name cc-groq-proxy -p 7187:7187 \
  -e GROQ_API_KEY=your_key \
  claude-code-groq-proxy \
  python proxy.py --model llama-3.1-70b-versatile --max-tokens 8192

# Stop and remove
docker stop cc-groq-proxy && docker rm cc-groq-proxy
```

## Features

- **Universal Groq Model Support**: Works with any text-based model on Groq (OpenAI OSS, Kimi K2, Llama, etc)
- **Interactive Model Selection**: Uses `fzf` to browse and select from available Groq models
- **Token Limit Configuration**: Choose from 4096 to 1,048,576 tokens in 1024 increments
- **Detailed Logging**: View input/output content and token usage for debugging
- **Docker-based**: Easy deployment and management with zero local Python setup
- **Cost Monitoring**: Track token usage per request
- **Convenience Scripts**: Quick setup with `call.sh` and comprehensive CLI management with `cli.py`

## Feedback

Share your experience using different Groq models compared to Claude by opening an issue. Your feedback helps improve this tool.

## Acknowledgements

Inspired by [claude-code-proxy](https://github.com/1rgs/claude-code-proxy) and this repo is a fork of [fakerybakery/claude-code-kimi-groq](https://github.com/fakerybakery/claude-code-kimi-groq).

## License

This code base is licensed under the MIT License. See [LICENSE](./LICENSE) for more details.

## Evaluation Reports

### September 14, 2025

#### Overview

Anthropic's Claude models Sonnet 4 and Opus 4.1 are used in [Claude Code CLI](https://github.com/anthropics/claude-code). These models are powerful but expensive for large-scale coding and writing tasks. By redirecting **Claude Code CLI** through a local proxy to **Groq's `moonshotai/kimi-k2-instruct-0905`**, this evaluation tested whether Kimi can serve as a cost-effective substitute without sacrificing too much quality.

#### Pricing Comparison

- **Claude Sonnet 4**: $3/M input, $15/M output
- **Claude Opus 4.1**: $15/M input, $75/M output
- **Groq Kimi K2-0905**: $1/M input, $3/M output

This makes Kimi **67-93% cheaper on input** and **80-96% cheaper on output**, depending on which Claude tier you compare against.

#### Performance

- **Coding**: Kimi scores ~70-80% as strong as Claude Sonnet/Opus in benchmarked tasks. It trails slightly on curated coding sets but sometimes matches or exceeds in interactive coding (e.g., LiveCodeBench).
- **Writing**: Comparable technical writing performance, though Claude remains more polished on complex narrative tasks.
- **Context**: Kimi supports ~262k tokens vs Claude's 1M, but this is sufficient for most CLI use cases.

#### Conclusion

For most **day-to-day Claude Code CLI tasks** (bug fixes, refactoring, tool use, documentation), Kimi provides **substantial cost savings with only moderate quality trade-offs**. Claude Sonnet/Opus are still preferable for the most demanding, long-context, or mission-critical tasks, but **using Kimi via the proxy is a highly economical default option**.
