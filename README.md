# Claude Code Kimi Proxy

A FastAPI proxy server that enables using Groq's Kimi K2 model with [Claude Code CLI](https://github.com/anthropics/claude-code), providing significant cost savings while maintaining strong performance for coding tasks.

## Getting Started

### Prerequisites

- [Python 3.8+](https://www.python.org/)
- [Groq API key](https://console.groq.com/)
- [Claude Code CLI](https://github.com/anthropics/claude-code)

### Installation

1. Clone and set up the environment:

```bash
cd claude-code-kimi-groq
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Configure your Groq API key:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

3. Start the proxy server:

```bash
python proxy.py
```

### Usage

Configure Claude Code to use the proxy:

```bash
export ANTHROPIC_BASE_URL=http://localhost:7187
export ANTHROPIC_API_KEY=NOT_NEEDED
claude
```

The proxy will now route Claude Code requests through Groq's Kimi K2 model.

## Feedback

Share your experience using Kimi K2 compared to Claude by opening an issue. Your feedback helps improve this tool.

## Acknowledgements

Inspired by [claude-code-proxy](https://github.com/1rgs/claude-code-proxy) and this repo is a fork of [fakerybakery/claude-code-kimi-groq](https://github.com/fakerybakery/claude-code-kimi-groq).

## License

[MIT](LICENSE.md)

## Evaluation Report (09/07/2025)

### Overview

Anthropic's Claude models Sonnet 4 and Opus 4.1 are used in [Claude Code CLI](https://github.com/anthropics/claude-code). These models are powerful but expensive for large-scale coding and writing tasks. By redirecting **Claude Code CLI** through a local proxy to **Groq's `moonshotai/kimi-k2-instruct-0905`**, this evaluation tested whether Kimi can serve as a cost-effective substitute without sacrificing too much quality.

### Pricing Comparison

- **Claude Sonnet 4**: \$3/M input, \$15/M output
- **Claude Opus 4.1**: \$15/M input, \$75/M output
- **Groq Kimi K2-0905**: \$1/M input, \$3/M output

This makes Kimi **67–93% cheaper on input** and **80–96% cheaper on output**, depending on which Claude tier you compare against.

### Performance

- **Coding**: Kimi scores \~70–80% as strong as Claude Sonnet/Opus in benchmarked tasks. It trails slightly on curated coding sets but sometimes matches or exceeds in interactive coding (e.g., LiveCodeBench).
- **Writing**: Comparable technical writing performance, though Claude remains more polished on complex narrative tasks.
- **Context**: Kimi supports \~262k tokens vs Claude’s 1M, but this is sufficient for most CLI use cases.

### Conclusion

For most **day-to-day Claude Code CLI tasks** (bug fixes, refactoring, tool use, documentation), Kimi provides **substantial cost savings with only moderate quality trade-offs**. Claude Sonnet/Opus are still preferable for the most demanding, long-context, or mission-critical tasks, but **using Kimi via the proxy is a highly economical default option**.
