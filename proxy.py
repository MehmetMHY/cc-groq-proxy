import argparse
import json
import os
import sys
import uuid
from typing import Any, Dict, List, Literal, Optional, Union

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel
from rich import print

load_dotenv()
app = FastAPI()

# Default configuration
DEFAULT_GROQ_MODEL = "moonshotai/kimi-k2-instruct-0905"
DEFAULT_GROQ_MAX_OUTPUT_TOKENS = 16384

# Parse command line arguments
parser = argparse.ArgumentParser(description="Groq Anthropic Tool Proxy")
parser.add_argument(
    "--model",
    default=DEFAULT_GROQ_MODEL,
    help=f"Model to use (default: {DEFAULT_GROQ_MODEL})",
)
parser.add_argument(
    "--max-tokens",
    type=int,
    default=DEFAULT_GROQ_MAX_OUTPUT_TOKENS,
    help=f"Maximum output tokens (default: {DEFAULT_GROQ_MAX_OUTPUT_TOKENS})",
)
args = parser.parse_args()

# Check for required API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("[bold red]❌ GROQ_API_KEY environment variable is not set![/bold red]")
    print("Setup and get your Groq API key here: https://console.groq.com/")
    sys.exit(1)

client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")

GROQ_MODEL = args.model
GROQ_MAX_OUTPUT_TOKENS = args.max_tokens


# ---------- Anthropic Schema ----------
class ContentBlock(BaseModel):
    type: Literal["text"]
    text: str


class ToolUseBlock(BaseModel):
    type: Literal["tool_use"]
    id: str
    name: str
    input: Dict[str, Union[str, int, float, bool, dict, list]]


class ToolResultBlock(BaseModel):
    type: Literal["tool_result"]
    tool_use_id: str
    content: Union[str, List[Dict[str, Any]], Dict[str, Any], List[Any], Any]


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, List[Union[ContentBlock, ToolUseBlock, ToolResultBlock]]]


class Tool(BaseModel):
    name: str
    description: Optional[str]
    input_schema: Dict[str, Any]


class MessagesRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 1024
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False
    tools: Optional[List[Tool]] = None
    tool_choice: Optional[Union[str, Dict[str, str]]] = "auto"


# ---------- Conversion Helpers ----------


def convert_messages(messages: List[Message]) -> List[dict]:
    converted = []
    for m in messages:
        if isinstance(m.content, str):
            content = m.content
        else:
            parts = []
            for block in m.content:
                if block.type == "text":
                    parts.append(block.text)
                elif block.type == "tool_use":
                    tool_info = f"[Tool Use: {block.name}] {json.dumps(block.input)}"
                    parts.append(tool_info)
                elif block.type == "tool_result":
                    result = block.content
                    print(
                        f"[bold yellow]📥 Tool Result for {block.tool_use_id}: {json.dumps(result, indent=2)}[/bold yellow]"
                    )
                    parts.append(f"<tool_result>{json.dumps(result)}</tool_result>")
            content = "\n".join(parts)
        converted.append({"role": m.role, "content": content})
    return converted


def convert_tools(tools: List[Tool]) -> List[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.input_schema,
            },
        }
        for t in tools
    ]


def convert_tool_calls_to_anthropic(tool_calls) -> List[dict]:
    content = []
    for call in tool_calls:
        fn = call.function
        arguments = json.loads(fn.arguments)

        print(
            f"[bold green]🛠 Tool Call: {fn.name}({json.dumps(arguments, indent=2)})[/bold green]"
        )

        content.append(
            {"type": "tool_use", "id": call.id, "name": fn.name, "input": arguments}
        )
    return content


# ---------- Main Proxy Route ----------


@app.post("/v1/messages")
async def proxy(request: MessagesRequest):
    print(f"[bold cyan]🚀 Anthropic → Groq | Model: {request.model}[/bold cyan]")

    openai_messages = convert_messages(request.messages)
    tools = convert_tools(request.tools) if request.tools else None

    # Log the input messages
    print(f"[bold blue]📝 INPUT TO MODEL:[/bold blue]")
    for msg in openai_messages:
        print(f"[blue]Role: {msg['role']}[/blue]")
        print(
            f"[blue]Content: {msg['content'][:500]}{'...' if len(msg['content']) > 500 else ''}[/blue]"
        )
        print("[blue]---[/blue]")

    max_tokens = min(
        request.max_tokens or GROQ_MAX_OUTPUT_TOKENS, GROQ_MAX_OUTPUT_TOKENS
    )

    if request.max_tokens and request.max_tokens > GROQ_MAX_OUTPUT_TOKENS:
        print(
            f"[bold yellow]⚠️  Capping max_tokens from {request.max_tokens} to {GROQ_MAX_OUTPUT_TOKENS}[/bold yellow]"
        )

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=openai_messages,
        temperature=request.temperature,
        max_tokens=max_tokens,
        tools=tools,
        tool_choice=request.tool_choice,
    )

    choice = completion.choices[0]
    msg = choice.message

    # Log the output from model
    print(f"[bold green]📤 OUTPUT FROM MODEL:[/bold green]")
    if msg.tool_calls:
        print(f"[green]Tool calls: {len(msg.tool_calls)} calls made[/green]")
        for call in msg.tool_calls:
            print(f"[green]Tool: {call.function.name}[/green]")
        tool_content = convert_tool_calls_to_anthropic(msg.tool_calls)
        stop_reason = "tool_use"
    else:
        output_content = msg.content or ""
        print(
            f"[green]Content: {output_content[:500]}{'...' if len(output_content) > 500 else ''}[/green]"
        )
        tool_content = [{"type": "text", "text": msg.content}]
        stop_reason = "end_turn"
    print("[green]---[/green]")

    # Log token usage
    print(
        f"[bold magenta]📊 TOKENS: Input: {completion.usage.prompt_tokens} | Output: {completion.usage.completion_tokens} | Total: {completion.usage.total_tokens}[/bold magenta]"
    )

    return {
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "model": f"groq/{GROQ_MODEL}",
        "role": "assistant",
        "type": "message",
        "content": tool_content,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": completion.usage.prompt_tokens,
            "output_tokens": completion.usage.completion_tokens,
        },
    }


@app.get("/")
def root():
    return {"message": "Groq Anthropic Tool Proxy is alive 💡"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7187)
