---
name: economist-cartoon
description: >
  This skill should be used when the user wants to generate an editorial cartoon,
  news cartoon, or political cartoon in the style of The Economist. Triggers on
  phrases like "make a cartoon about", "economist cartoon", "editorial cartoon",
  "political cartoon from today's news", or when the /economist-cartoon command is run.
  Requires the gemini-image MCP server to be connected (gemini_generate_image tool).
version: 0.1.0
---

# Economist Cartoon Skill

Generate editorial cartoons in The Economist's style from real news stories.
The full workflow: fetch news → brainstorm concepts → user picks → generate image.

## Workflow

### Step 1: Get the news

If the user provided a specific topic or story, use that. Otherwise, run a web
search for today's top news stories and pick the 3 most visually interesting,
politically significant stories.

```
WebSearch: "top news stories today [current date]"
```

Pick stories with clear protagonists, tensions, or ironies — these make the best cartoons.

### Step 2: Brainstorm 3 cartoon concepts

For each candidate story, develop one distinct concept using The Economist style
principles (see `references/style-guide.md`). Good concepts have:

- A single, instantly readable central metaphor
- At least one labeled object (e.g. a machine labeled "IRAN'S NUCLEAR PROGRAM")
- An exaggerated caricature of a recognizable figure if relevant
- Dark irony or a visual punchline
- Something that would work in pure B&W

Present the 3 concepts clearly — one paragraph each, describing the visual scene.
Do NOT generate any images yet.

### Step 3: Ask the user to pick

Use AskUserQuestion with the 3 concepts as options. Allow free-text input so
they can mix or refine. Example format:

- Option A: [concept title] — [one-sentence description]
- Option B: [concept title] — [one-sentence description]
- Option C: [concept title] — [one-sentence description]

### Step 4: Refine if needed

If the user wants to tweak (e.g. "remove the UN inspector", "make it funnier"),
incorporate the feedback and confirm the final concept before generating.

### Step 5: Build the Gemini prompt

First, identify the actual real-world figures in the chosen story. Use their
real names directly in the prompt (e.g. "Donald Trump", "Benjamin Netanyahu") —
the model knows what they look like and produces far better caricatures from
names than from physical descriptions.

Then translate the concept into a detailed image generation prompt using this template:

```
Black and white editorial cartoon in the style of The Economist magazine.
Pen and ink illustration with heavy cross-hatching and fine line work.
[SCENE DESCRIPTION — specific, visual, detailed].
[LABELS on key objects in CAPS].
[CARICATURE NOTES if applicable — exaggerated features, body language].
Bold, dramatic composition. No color, pure black and white ink style.
```

Refer to `references/style-guide.md` for prompt writing tips.

### Step 6: Generate the image

Call `gemini_generate_image` with the prompt. Use a descriptive filename
(e.g. `iran_nuclear_cartoon`, `trump_tariffs_cartoon`).

If the tool is not available, tell the user: "The gemini-image MCP server isn't
connected. Make sure it's set up and GEMINI_API_KEY is configured — see the
plugin README for instructions."

**After generation:**
- Read the `file_path` value from the JSON response
- Tell the user the image was saved and give them this exact command to open it:
  `open <file_path>`
- Do NOT attempt to copy, move, or read the file. Do NOT use Bash.
  The image is saved directly to the user's machine by the MCP server —
  the session VM cannot access it.

### Step 7: Iterate

Ask the user if they'd like to:
- Adjust the prompt and regenerate
- Try a different concept
- Move on (e.g. drop into Canva)
