#!/usr/bin/env python3
"""
MCP Server for Gemini Image Generation.

Provides tools to generate and edit images using Google's Gemini models,
saving results locally and returning file paths for use in other tools.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

# ── Server init ──────────────────────────────────────────────────────────────
mcp = FastMCP("gemini_image_mcp")

# ── Constants ─────────────────────────────────────────────────────────────────
DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
OUTPUT_DIR = Path(os.environ.get("GEMINI_OUTPUT_DIR", Path.home() / "gemini_images"))


# ── Shared utilities ──────────────────────────────────────────────────────────

def get_client():
    """Return a configured Gemini client, raising clearly if key is missing."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Add it to your MCP server config env block."
        )
    from google import genai
    return genai.Client(api_key=api_key)


def ensure_output_dir() -> Path:
    """Create and return the output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def make_filename(prefix: str = "gemini") -> str:
    """Generate a timestamped filename stem."""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def save_image(image_bytes: bytes, stem: str) -> Path:
    """Decode image bytes with PIL (handles PNG or JPEG) and save as PNG."""
    from PIL import Image
    from io import BytesIO
    img = Image.open(BytesIO(image_bytes))
    path = ensure_output_dir() / f"{stem}.png"
    img.save(path, format="PNG")
    return path


def extract_image_and_text(response) -> tuple[Optional[bytes], str]:
    """Pull image bytes and text out of a Gemini generate_content response.

    Note: in google-genai SDK, inline_data.data is already raw bytes (not base64).
    The mime_type may be reported as image/png but actually be JPEG — we use PIL
    to normalise everything to PNG on save.
    """
    image_data: Optional[bytes] = None
    text: str = ""
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            text = part.text
        elif hasattr(part, "inline_data") and part.inline_data:
            image_data = part.inline_data.data  # already bytes, do NOT base64-decode
    return image_data, text


def handle_error(e: Exception) -> str:
    """Return a JSON error string with a helpful hint."""
    msg = str(e)
    hint = None
    if "GEMINI_API_KEY" in msg:
        hint = "Set GEMINI_API_KEY in the MCP server env config."
    elif "not found" in msg.lower() or "404" in msg:
        hint = "Check the model name — it may have changed. Try 'gemini-3.1-flash-image-preview'."
    elif "quota" in msg.lower() or "429" in msg:
        hint = "Rate limit hit. Wait a moment and retry."
    return json.dumps({"error": f"{type(e).__name__}: {msg}", "hint": hint}, indent=2)


# ── Input models ──────────────────────────────────────────────────────────────

class GenerateImageInput(BaseModel):
    """Input for gemini_generate_image."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    prompt: str = Field(
        ...,
        description=(
            "Detailed text description of the image to generate. "
            "Be specific about style, lighting, composition, and subject. "
            "Example: 'A misty mountain valley at golden hour, cinematic, 16:9'"
        ),
        min_length=3,
        max_length=2000,
    )
    filename: Optional[str] = Field(
        default=None,
        description="Output filename stem (no extension). Defaults to a timestamp-based name.",
    )
    model: Optional[str] = Field(
        default=DEFAULT_MODEL,
        description=f"Gemini model to use. Defaults to '{DEFAULT_MODEL}'.",
    )


class EditImageInput(BaseModel):
    """Input for gemini_edit_image."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    image_path: str = Field(
        ...,
        description="Absolute path to the existing image file to edit (PNG or JPEG).",
    )
    prompt: str = Field(
        ...,
        description=(
            "Description of the edit to apply. "
            "Example: 'Add a sunset sky in the background' or 'Remove the person on the left'."
        ),
        min_length=3,
        max_length=2000,
    )
    filename: Optional[str] = Field(
        default=None,
        description="Output filename stem for the edited image. Defaults to a timestamp-based name.",
    )


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool(name="gemini_generate_image")
async def gemini_generate_image(params: GenerateImageInput) -> str:
    """Generate an image from a text prompt using Google Gemini.

    Calls the Gemini image generation model and saves the result as a PNG file
    in the configured output directory (~/gemini_images by default, or the path
    set in GEMINI_OUTPUT_DIR).

    Args:
        params (GenerateImageInput):
            - prompt (str): Detailed text description of the desired image.
            - filename (Optional[str]): Custom output filename stem (no extension).
            - model (Optional[str]): Gemini model name override.

    Returns:
        str: JSON with keys:
            - success (bool)
            - file_path (str): Absolute path to the saved PNG
            - filename (str): Just the filename
            - file_size_kb (float)
            - prompt (str): The prompt used
            - model (str): The model used
            - notes (str | null): Any text the model returned alongside the image

        On error:
            - error (str): Error description
            - hint (str | null): Suggested fix

    Examples:
        - "Generate a photo of a foggy Japanese forest" → gemini_generate_image
        - "Create a watercolor illustration of a cat" → gemini_generate_image
    """
    try:
        from google.genai import types

        client = get_client()
        model = params.model or DEFAULT_MODEL

        response = client.models.generate_content(
            model=model,
            contents=params.prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            ),
        )

        image_bytes, text = extract_image_and_text(response)
        if not image_bytes:
            return json.dumps({
                "error": "Gemini did not return an image.",
                "text": text,
                "hint": "Try a more descriptive prompt, or check that the model supports image output.",
            }, indent=2)

        stem = params.filename or make_filename("gemini")
        path = save_image(image_bytes, stem)

        return json.dumps({
            "success": True,
            "file_path": str(path),
            "filename": path.name,
            "file_size_kb": round(len(image_bytes) / 1024, 1),
            "prompt": params.prompt,
            "model": model,
            "notes": text or None,
        }, indent=2)

    except Exception as e:
        return handle_error(e)


@mcp.tool(name="gemini_edit_image")
async def gemini_edit_image(params: EditImageInput) -> str:
    """Edit an existing image using a text prompt with Google Gemini.

    Loads an existing image file, applies the described edits using Gemini,
    and saves the result as a new PNG file. The source image is not modified.

    Args:
        params (EditImageInput):
            - image_path (str): Absolute path to the source image (PNG or JPEG).
            - prompt (str): Description of the edits to apply.
            - filename (Optional[str]): Custom output filename stem (no extension).

    Returns:
        str: JSON with keys:
            - success (bool)
            - file_path (str): Absolute path to the edited PNG
            - filename (str)
            - file_size_kb (float)
            - source_image (str): Path to the original image
            - prompt (str)
            - notes (str | null)

        On error:
            - error (str)
            - hint (str | null)

    Examples:
        - Edit a photo to change the background → gemini_edit_image
        - Add text or a logo overlay → gemini_edit_image
    """
    try:
        import PIL.Image
        from google.genai import types

        client = get_client()

        input_path = Path(params.image_path)
        if not input_path.exists():
            return json.dumps({
                "error": f"Source image not found: {params.image_path}",
                "hint": "Use gemini_list_images to see available generated images.",
            }, indent=2)

        image = PIL.Image.open(input_path)

        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=[params.prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            ),
        )

        image_bytes, text = extract_image_and_text(response)
        if not image_bytes:
            return json.dumps({
                "error": "Gemini did not return an image.",
                "text": text,
                "hint": "Try rephrasing the edit prompt.",
            }, indent=2)

        stem = params.filename or make_filename("gemini_edit")
        path = save_image(image_bytes, stem)

        return json.dumps({
            "success": True,
            "file_path": str(path),
            "filename": path.name,
            "file_size_kb": round(len(image_bytes) / 1024, 1),
            "source_image": params.image_path,
            "prompt": params.prompt,
            "notes": text or None,
        }, indent=2)

    except Exception as e:
        return handle_error(e)


@mcp.tool(name="gemini_list_images")
async def gemini_list_images() -> str:
    """List all images previously generated or edited by the Gemini server.

    Scans the configured output directory and returns metadata for each PNG file,
    sorted newest-first.

    Returns:
        str: JSON with keys:
            - output_directory (str): The folder being scanned
            - total_images (int)
            - images (list): Each entry has filename, file_path, file_size_kb, created

    Examples:
        - "What images have we generated so far?" → gemini_list_images
        - "Show me the path to the latest image" → gemini_list_images
    """
    try:
        output_dir = ensure_output_dir()
        images = [
            {
                "filename": p.name,
                "file_path": str(p),
                "file_size_kb": round(p.stat().st_size / 1024, 1),
                "created": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            }
            for p in sorted(output_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        ]

        return json.dumps({
            "output_directory": str(output_dir),
            "total_images": len(images),
            "images": images,
        }, indent=2)

    except Exception as e:
        return handle_error(e)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
