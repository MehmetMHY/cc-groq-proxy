#!/usr/bin/env python3

from pathlib import Path
import subprocess
import argparse
import json
import sys
import os

SCRIPT_DIR = Path(__file__).parent.absolute()
IMAGE_NAME = "claude-code-groq-proxy"
CONTAINER_NAME = "cc-groq-proxy"
PORT = "7187"


def check_groq_key():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY environment variable is not set!")
        print("Setup and get your Groq API key here: https://console.groq.com/")
        sys.exit(1)


def build_image():
    print("Building Docker image...")
    subprocess.run(["docker", "build", "-t", IMAGE_NAME, str(SCRIPT_DIR)], check=True)


def get_groq_models():
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        print("GROQ_API_KEY not set")
        return ""

    try:
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-H",
                f"Authorization: Bearer {groq_key}",
                "-H",
                "Content-Type: application/json",
                "https://api.groq.com/openai/v1/models",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                models = [item["id"] for item in data.get("data", [])]
                return "\n".join(models)
            except (json.JSONDecodeError, KeyError):
                return ""
    except Exception:
        pass
    return ""


def select_model_interactive(model_arg):
    if model_arg:
        return model_arg

    if not subprocess.run(["which", "fzf"], capture_output=True).returncode == 0:
        print("fzf not found. Please install fzf for interactive model selection.")
        sys.exit(1)

    print("Fetching available models...")
    models = get_groq_models()
    if not models:
        print("No models available.")
        sys.exit(1)

    model_list = "DEFAULT\n" + models

    try:
        result = subprocess.run(
            ["fzf", "--prompt=Select model: ", "--reverse"],
            input=model_list,
            text=True,
            capture_output=True,
        )

        if result.returncode != 0 or not result.stdout.strip():
            print("Selection cancelled or no model selected. Exiting.")
            sys.exit(1)

        selected_model = result.stdout.strip()
        if selected_model == "DEFAULT":
            print("Selected: DEFAULT")
            return ""
        else:
            print(f"Selected: {selected_model}")
            return f"--model {selected_model}"
    except Exception:
        print("Selection cancelled or no model selected. Exiting.")
        sys.exit(1)


def select_tokens_interactive(token_arg):
    if token_arg:
        return token_arg

    if not subprocess.run(["which", "fzf"], capture_output=True).returncode == 0:
        print("fzf not found. Please install fzf for interactive token selection.")
        sys.exit(1)

    token_options = ["DEFAULT"]
    for i in range(4096, 1048577, 1024):
        token_options.append(str(i))

    token_list = "\n".join(token_options)

    try:
        result = subprocess.run(
            ["fzf", "--prompt=Select max tokens: ", "--reverse"],
            input=token_list,
            text=True,
            capture_output=True,
        )

        if result.returncode != 0 or not result.stdout.strip():
            print("Selection cancelled or no tokens selected. Exiting.")
            sys.exit(1)

        selected_tokens = result.stdout.strip()
        if selected_tokens == "DEFAULT":
            print("Selected: DEFAULT")
            return ""
        else:
            print(f"Selected: {selected_tokens} tokens")
            return f"--max-tokens {selected_tokens}"
    except Exception:
        print("Selection cancelled or no tokens selected. Exiting.")
        sys.exit(1)


def container_exists():
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", f"name={CONTAINER_NAME}"],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def container_exists_any():
    result = subprocess.run(
        ["docker", "ps", "-aq", "-f", f"name={CONTAINER_NAME}"],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def run_container():
    check_groq_key()

    if container_exists():
        print(f"Container {CONTAINER_NAME} is already running")
        subprocess.run(["docker", "ps", "-f", f"name={CONTAINER_NAME}"])
        return

    model_arg = select_model_interactive("")
    token_arg = select_tokens_interactive("")

    print("Starting container...")

    cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        CONTAINER_NAME,
        "-p",
        f"{PORT}:7187",
        "-e",
        f"GROQ_API_KEY={os.environ.get('GROQ_API_KEY')}",
        IMAGE_NAME,
        "python",
        "proxy.py",
    ]

    if model_arg:
        cmd.extend(model_arg.split())
    if token_arg:
        cmd.extend(token_arg.split())

    subprocess.run(cmd, check=True)
    print(f"Proxy started on http://localhost:{PORT}")
    subprocess.run(["docker", "ps", "-f", f"name={CONTAINER_NAME}"])


def stop_container():
    if container_exists():
        print(f"Stopping container {CONTAINER_NAME}...")
        subprocess.run(["docker", "stop", CONTAINER_NAME])
        subprocess.run(["docker", "rm", CONTAINER_NAME])
        print("Container stopped and removed")
    else:
        print(f"Container {CONTAINER_NAME} is not running")


def show_logs():
    if container_exists_any():
        subprocess.run(["docker", "logs", CONTAINER_NAME])
    else:
        print(f"Container {CONTAINER_NAME} does not exist")


def follow_logs():
    if container_exists():
        print(f"Following logs for {CONTAINER_NAME} (Ctrl+C to exit)...")
        subprocess.run(["docker", "logs", "-f", CONTAINER_NAME])
    else:
        print(f"Container {CONTAINER_NAME} is not running")


def show_status():
    if container_exists():
        print("✅ Container is running:")
        subprocess.run(["docker", "ps", "-f", f"name={CONTAINER_NAME}"])
        print("")
        print("📊 Resource usage:")
        subprocess.run(["docker", "stats", CONTAINER_NAME, "--no-stream"])
    elif container_exists_any():
        print("⏸️ Container exists but is not running")
        subprocess.run(["docker", "ps", "-a", "-f", f"name={CONTAINER_NAME}"])
    else:
        print("❌ Container does not exist")


def main():
    parser = argparse.ArgumentParser(description="Docker proxy management CLI")
    subparsers = parser.add_subparsers(dest="command", metavar="")

    subparsers.add_parser("build", help="Build the Docker image")

    subparsers.add_parser("run", help="Start the proxy container")

    subparsers.add_parser("stop", help="Stop and remove the container")
    subparsers.add_parser("status", help="Show container status")
    subparsers.add_parser("logs", help="Show container logs")
    subparsers.add_parser("follow", help="Follow container logs (live)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "build":
            build_image()
        elif args.command == "run":
            run_container()
        elif args.command == "stop":
            stop_container()
        elif args.command == "status":
            show_status()
        elif args.command == "logs":
            show_logs()
        elif args.command == "follow":
            follow_logs()
    except subprocess.CalledProcessError:
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
