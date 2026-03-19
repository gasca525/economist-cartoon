# Economist Cartoon Style Guide

## Visual Style

The Economist's editorial cartoons are instantly recognizable:

- **Medium**: Pen and ink, pure black and white — no color, no grey wash
- **Shading**: Heavy cross-hatching and fine line work for depth and shadow
- **Linework**: Confident, slightly scratchy ink lines; not clean vector art
- **Composition**: Single strong focal point, dramatic angles, high contrast
- **Scale**: Key figures are large and central; background elements are smaller

## Caricature Principles

- Exaggerate 2-3 dominant physical features (hair, chin, posture, expression)
- Bodies can be cartoonishly small relative to oversized heads
- Facial expressions are extreme — fury, panic, smugness, obliviousness
- Clothing and props signal role (hard hats, suits, military uniforms, crowns)
- **Name political figures directly in the prompt** — use their actual names
  (e.g. "Donald Trump", "Benjamin Netanyahu"). The model knows what they look
  like and produces far better caricatures from names than from feature descriptions.
- Always use the actual people from the story — not stand-ins or generic figures.

## The Central Metaphor

Every great Economist cartoon has one strong visual metaphor that carries the story:

| Metaphor type | Example |
|---|---|
| Impossible task | Whack-a-mole, pushing a boulder uphill, bailing out a sinking ship |
| Power dynamic | One figure towering over another, puppet strings, leash |
| Irony/contradiction | Opening a door labeled "EXIT" that leads to another trap |
| Measurement/scale | Tiny figure vs enormous problem labeled in ALL CAPS |
| Classic symbol | Scales of justice, chess pieces, ticking clocks |

**Rule**: The metaphor should be readable in 2 seconds with no caption needed.

## Labeled Objects

Labels on objects are a signature Economist technique. Use them to:
- Name the abstract concept the object represents ("IRAN'S NUCLEAR PROGRAM")
- Show the stakes ("$3 TRILLION DEFICIT")
- Create irony ("DEMOCRACY" written on a crumbling pillar)

Labels should be in ALL CAPS, short (1-4 words), and on a prominent object.

## What Makes a Strong Concept

✓ One clear visual metaphor
✓ At least one labeled object
✓ Exaggerated caricature with recognizable silhouette
✓ Irony or unexpected twist
✓ Works in pure B&W
✓ Readable at a glance

✗ Too many figures or elements
✗ Requires reading a caption to understand
✗ Abstract or symbolic without a concrete visual hook
✗ Relies on color to convey meaning

## Gemini Prompt Template

```
Black and white pen and ink editorial cartoon in the style of a classic British political magazine. Heavy cross-hatching and fine line work, no color whatsoever.
[SCENE: describe the main action and figures in detail]
[LABELS: specify what text appears on objects, in ALL CAPS]
[CARICATURE: describe distinctive features of any figures]
Bold, dramatic composition. Pure black and white ink only.
No logos, no mastheads, no magazine names, no artist signatures, no text of any kind in the corners or borders.
```

### Prompt Tips

- Be specific about action ("frantically hammering", "smugly ignoring", "desperately bailing")
- Describe spatial relationships ("looming over", "shrinking away from", "perched on top of")
- Mention specific objects that carry the metaphor ("an arcade whack-a-mole machine", "a sinking ship", "a set of scales")
- Keep prompts under 150 words — Gemini performs best with focused, concrete descriptions
- If the first result is too clean/digital-looking, add: "rough hand-drawn ink style, imperfect lines, visible pen strokes"
- Always end with the no-masthead line

## Reference: What Worked

This prompt generated a strong result:

> "Black and white editorial cartoon in the style of The Economist magazine.
> Pen and ink illustration with heavy cross-hatching and fine line work.
> Two exaggerated caricatures — one with wild hair and a long tie, one stocky
> with a stern expression — both wearing oversized hard hats, frantically
> hammering a giant whack-a-mole arcade machine labeled 'IRAN'S NUCLEAR PROGRAM'.
> Every mole they smash down causes two more to pop up from other holes, each
> mole wearing a tiny radiation symbol. The figures look increasingly frantic
> and sweaty. Bold, dramatic composition. No color, pure black and white ink style."
