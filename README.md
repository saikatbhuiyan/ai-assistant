# AI Agent

A command-line AI assistant built step by step into an AI agent, using local models through [Ollama](https://ollama.com). It can hold a conversation, take on a role, use tools chosen by an LLM planner and served over the Model Context Protocol (MCP), answer questions about text files, and answer from a knowledge base with retrieval-augmented generation (RAG).

The code talks to Ollama through its OpenAI-compatible API, so it can also run against any other OpenAI-compatible server by changing `.env`.

## Features

| Feature | Where | What it does |
| --- | --- | --- |
| Chat with memory | `assistant.py` | Keeps the conversation history, so the model remembers earlier messages |
| Roles | `assistant.py` | Choose a teacher, Python expert, travel guide, motivational coach, or interviewer at startup |
| Tools chosen by a planner | `planner.py` | An LLM decides whether to tell the time, roll a die, or generate a password |
| MCP tool server | `mcp_tools/` | The tools run on a FastMCP server that the assistant starts and connects to |
| File commands | `assistant.py`, `data/` | Summarize, explain, or ask questions about `.txt` files in `data/` |
| Keyword retriever | `retriever.py` | Ranks knowledge documents by the words they share with a question |
| RAG assistant | `rag.py`, `knowledge/` | Finds the most relevant knowledge document using embeddings and answers only from it |

## Requirements

- **Python 3.14.** The project was developed and tested on 3.14.
- **Ollama**, running locally, with:
  - a chat model, for example `qwen3:4b`
  - the embedding model `nomic-embed-text`, needed only for `rag.py`

## Setup

1. Create a virtual environment and install the dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Download the models:

   ```bash
   ollama pull qwen3:4b
   ollama pull nomic-embed-text
   ```

3. Create your `.env` from the example, then set `MODEL` to the chat model you pulled:

   ```bash
   cp .env.example .env
   ```

   | Variable | Example | Notes |
   | --- | --- | --- |
   | `BASE_URL` | `http://localhost:11434/v1` | Ollama's OpenAI-compatible endpoint |
   | `API_KEY` | `ollama` | Ollama ignores the value, but the OpenAI client refuses to start if it's empty |
   | `MODEL` | `qwen3:4b` | Chat model used by `assistant.py`, `planner.py`, and `rag.py`. `assistant.py` exits if it isn't set |

   `.env` is in `.gitignore`. Don't commit it.

## Usage

Run every command from the project folder, because `assistant.py` reads files from `data/` relative to the current directory.

### Assistant

```bash
python assistant.py
```

Pick a role (1–5), or press any other key for a general assistant. Then type:

| You type | What happens |
| --- | --- |
| Any question | The planner checks whether a tool is needed; if not, the model answers using the conversation history |
| `What time is it?` | The planner picks `get_current_time`, the MCP server runs it, and the result is printed |
| `summarize notes.txt` | Summarizes `data/notes.txt` |
| `explain notes.txt` | Explains `data/notes.txt` in simple language |
| `ask project.txt Who worked on the project?` | Answers from `data/project.txt` only, or says it couldn't find the answer |
| `quit` | Exits |

File commands read only `.txt` files placed directly inside `data/`, and they don't add anything to the conversation history.

### RAG assistant

```bash
python rag.py
```

At startup, every `.txt` file in `knowledge/` is embedded. For each question, the most similar document is found by cosine similarity and sent to the model as context. The answer is followed by its source, for example:

```text
You : What is machine learning?

AI : Machine learning is a branch of Artificial Intelligence that enables computers to learn from data without being explicitly programmed.

(Source: machine_learning.txt, similarity 0.88)
```

To add knowledge, put more `.txt` files in `knowledge/` and restart.

## How it works

**Tool use.** When `assistant.py` starts, it launches the MCP server in `mcp_tools/server.py` and asks which tools it offers. The planner's prompt is built from those tool names and descriptions, so a tool added to the server is available without changing any other code. Each message, except file commands and `quit`, then goes to the planner first:

```text
User message → planner (LLM) → tool name or "none"
                                 │
                 tool name ──────┴────── none
                     │                     │
         MCP server runs it       model answers the message
                     │
              result is printed
```

The planner's reply is only a suggestion. A tool runs only if the reply exactly matches a name the MCP server reported, so any other reply runs nothing. The server stops when the assistant exits, including after Ctrl+C.

To try the MCP tools without the assistant, use the client functions directly:

```python
import asyncio
from mcp_tools.mcp_client import connect, disconnect, discover_tools, execute_tool

async def main():
    client = await connect()
    print([tool.name for tool in await discover_tools(client)])
    print(await execute_tool(client, "roll_dice", {"sides": 20}))
    await disconnect(client)

asyncio.run(main())
```

**RAG.** Retrieval, then augmentation, then generation: embed the question, pick the document whose embedding is most similar, put that document in the prompt, and ask the model to answer only from it.

## Project structure

```text
.
├── assistant.py          # Main assistant: roles, memory, file commands, tools
├── planner.py            # LLM planner that chooses one of the discovered tools
├── mcp_tools/
│   ├── server.py         # FastMCP server with the time, dice, and password tools
│   └── mcp_client.py     # Starts the server, lists its tools, and runs them
├── tools/
│   ├── tools.py          # Time, dice, password, and file-reading functions
│   └── tool_manager.py   # Earlier, non-MCP way of running tools; still tested
├── rag.py                # RAG assistant over knowledge/
├── retriever.py          # Loads knowledge documents; keyword retriever
├── embedding.py          # Creates embeddings with nomic-embed-text
├── similarity.py         # Cosine similarity
├── data/                 # Text files for the file commands
├── knowledge/            # Documents for the RAG assistant
├── tests/                # Unit tests
├── requirements.txt
└── .env.example
```

## Tests

```bash
python -m unittest
```

The tests don't call a model, so they run quickly and don't need Ollama. They report `OK (expected failures=3)`. Each of the three expected failures marks a known limitation, such as keyword matching treating "Explain time complexity" as a time request. They're there to show those limits are real.

`tests/test_file_tool.py` is a script rather than a test, so it prints a "file not found" message during the run. That's expected.

## Limitations

- **The planner picks one tool per message.** A request that needs two tools, like "generate a password and roll a dice", runs neither.
- **Each message waits for an extra model call.** The planner answers before the main reply, which adds a few seconds with larger models.
- **RAG uses only the single best document.** It always returns something, even for unrelated questions, so the prompt tells the model to say when the answer isn't in it. Questions spanning two documents get partial answers.
- **Embeddings are recomputed every time `rag.py` starts.** Nothing is stored between runs.

## Dependencies

| Package | Used for |
| --- | --- |
| `openai` | Talking to Ollama's OpenAI-compatible API |
| `python-dotenv` | Loading settings from `.env` |
| `numpy` | Cosine similarity |
| `fastmcp` | The MCP tool server and the client that connects to it |

## Naming note

The MCP folder is called `mcp_tools/`, not `mcp/`. A local folder named `mcp` clashes with the `mcp` package that fastmcp depends on: `import mcp.something` finds the installed package instead, and with an `__init__.py` the folder hides the real package, so `from fastmcp import Client` fails.
