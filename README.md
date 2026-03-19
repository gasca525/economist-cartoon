# Economist Cartoon Plugin

Generate editorial cartoons in The Economist's pen-and-ink style, powered by
Google Gemini image generation. Give it a topic or let it pull today's top news.

## What it does

1. Fetches top news stories (or uses a topic you provide)
2. Brainstorms 3 Economist-style cartoon concepts
3. You pick the one you like (and can refine it)
4. Generates the image with Gemini and saves it locally

## Usage

```
/economist-cartoon
```
Fetches today's top news and proposes 3 cartoon concepts.

```
/economist-cartoon AI regulation
```
Skips the news fetch and generates concepts around your topic.

## Setup

### 1. Install Python dependencies

```bash
pip install mcp google-genai pillow pydantic
```

### 2. Set your Gemini API key

Get a key at [Google AI Studio](https://aistudio.google.com/apikey), then add
it to your environment. The plugin reads `GEMINI_API_KEY` automatically.

On macOS/Linux, add to `~/.zshrc` or `~/.bashrc`:
```bash
export GEMINI_API_KEY="your_key_here"
```

### 3. Optional: Custom output directory

Generated images are saved to `~/gemini_images/` by default. Override with:
```bash
export GEMINI_OUTPUT_DIR="/path/to/your/folder"
```

## Components

| Component | Description |
|-----------|-------------|
| `/economist-cartoon` command | Slash command entry point |
| `economist-cartoon` skill | Full workflow: news → concepts → generate |
| `style-guide.md` | Economist visual style principles and prompt templates |
| `servers/gemini-image/server.py` | Bundled Gemini image generation MCP server |

## Model

Uses `gemini-3.1-flash-image-preview` (a.k.a. "nanobanana2") for image generation.
