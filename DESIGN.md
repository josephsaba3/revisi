# Revisi — Design System

Revisi is a brand-voice auditor for marketing copy. The design language reflects the product: editorial, opinionated, surgical. It looks like a manuscript meets a control panel — high contrast, mono labels, generous typography, and a single hot-pink mark used the way an editor draws on paper.

---

## 1. Brand idea

**The squiggle is the brand.**

The signature gesture is the wavy underline an editor draws under copy that needs work. It appears as:

- A pink wavy underline beneath select words in headlines (`<span class="sq">`, `<span class="sq-inline">`)
- A `text-decoration: underline wavy` on inline flagged spans inside copy
- A repeated dot/arc pattern under quotes on dark slabs
- The visual anchor of the logo itself

Use it sparingly — one squiggle per headline, never two adjacent. It is a verdict, not decoration.

The **caret** (`^`) appeared as an alternate logomark direction in `Logo v2` but the squiggle won; treat the caret as deprecated unless explicitly revisited.

**Creative North Star: "The Copy Desk Console"**

Revisi should feel like a focused editorial workspace: large decisive type, quiet reading surfaces, exact line-level marks, and a small number of highly visible action colors. The design has two modes. The marketing surface can be expressive and memorable, but the report workspace should feel like a professional copy desk where every mark has a reason.

The system rejects generic AI SaaS polish, Grammarly-like bloat, dense enterprise tooling, playful copy toys, and heavy admin dashboards. It should look useful for a small site and still credible for an agency reviewing many pages.

**Key Characteristics:**

- Editorial, not decorative.
- Sparse controls, high signal.
- Pink is an annotation color, not a general decoration.
- Borders and grid lines create structure before shadows do.
- Large typography is reserved for marketing claims and report scores.

---

## 2. Color

### Tokens

```css
:root {
  /* Ink — body + structure */
  --ink:      #0a0a0a;   /* primary text, borders, dark slabs */
  --ink-2:    #1a1a1a;   /* secondary body copy */
  --ink-3:    #2a2a2a;   /* rare; deepest neutral on light bg */

  /* Paper — backgrounds */
  --paper:    #fafafa;   /* default page background (NOT pure white) */
  --paper-2:  #f4f4f4;   /* section variation, recessed surfaces */

  /* Lines — hairlines and dividers */
  --line:     #e5e5e5;   /* default border (Homepage uses #e5e5e5, Audit uses #e9e9e9 — both fine) */
  --line-2:   #d4d4d4;   /* heavier divider, scrollbar */

  /* Muted text */
  --muted:    #737373;   /* mono labels, metadata, captions */
  --muted-2:  #525252;   /* secondary prose */

  /* Accent — the pink */
  --accent:       #FF2D6F;
  --accent-ink:   #fafafa;   /* text color when sitting ON accent */
  --accent-deep:  #d61f59;   /* hover / pressed pink */
  --accent-soft:  #ffe3ec;   /* highlight wash behind flagged sentences */
  --accent-softer:#fff3f7;   /* lightest pink wash */
}
```

### Usage rules

- **#fafafa is the page**, never `#ffffff`. The whole system reads as cream-paper, not screen-white.
- **Ink and paper carry the design.** The pink is a mark, not a palette.
- **Pink earns its place.** Use only for: (1) the squiggle, (2) flagged content (highlights, underlines, count chips), (3) one primary CTA per view, (4) a single accent number/word in a headline, (5) the announcement bar pill.
- **One pink per surface, two max.** A page with five pink elements is broken.
- **Dark slabs** (`--ink` background) are how we change emotional gear — for testimonials, "How it works", and footer. Inside a dark slab, the pink pops harder, so use it even more sparingly.
- **Green (#c5f229)** appears only in early logo explorations. Do not use it in production.

### Status colors (used in product UI)

```css
--ok:   #16a34a;   /* "page passed" dot in the page list */
```

Status uses small dots and tag chips, never floods. Failure is communicated through pink; success through a small green dot, never green text.

---

## 3. Typography

### Families

```css
--sans: "Space Grotesk", system-ui, sans-serif;   /* everything except metadata */
--mono: "JetBrains Mono", ui-monospace, monospace; /* labels, metadata, eyebrows */
```

Loaded from Google Fonts with weights 400 / 500 / 600 / 700. Mono uses 400 / 500 / 600.

Body opts in to stylistic sets for character:

```css
body { font-feature-settings: "ss01", "ss02"; }
```

### Type scale

| Role | Family / Weight | Size | Line-height | Tracking |
|---|---|---|---|---|
| Display hero (homepage H1) | Sans 700 | `clamp(72px, 11vw, 168px)` | 0.88 | -0.045em |
| Display marketing (logo hero) | Sans 700 | `clamp(96px, 14vw, 220px)` | 0.86 | -0.045em |
| Big CTA | Sans 700 | `clamp(80px, 12vw, 184px)` | 0.86 | -0.05em |
| Section H2 | Sans 700 | 96px | 0.90 | -0.045em |
| Sub-section H2 | Sans 700 | 64–72px | 0.92 | -0.04em |
| Card title H3 | Sans 700 | 40–42px | 0.95 | -0.035em |
| Step / row title H4 | Sans 600 | 28px | 1.10 | -0.025em |
| Lede / sub | Sans 400 | 22px | 1.40 | -0.005em |
| Body | Sans 400 | 17px | 1.45 | -0.005em |
| Body (in-product) | Sans 400 | 17.5px (sentence rows) / 14.5px (lists) | 1.55 | -0.005em |
| Caption / muted | Sans 400 | 13.5–14px | 1.45 | -0.005em |
| Eyebrow / label (mono) | Mono 500 | 11–12px | — | 0.10–0.12em, UPPERCASE |
| Micro mono | Mono 500 | 10–10.5px | — | 0.06–0.10em, UPPERCASE |

Italic in display sizes is reserved for editorial flourish ("decide *here*") at weight 400–500 against a 700 base — it reads as a hand-written aside.

### Headline composition rules

1. **One emphasis per headline.** Either: a pink word (`.pink`), a squiggled word (`.sq`), or a struck-through word — never combined.
2. Wrap the emphasized word in a span; do not color whole headlines pink.
3. Headlines tighten tracking as they grow; never use default tracking above 40px.
4. Use `text-wrap: pretty` on multi-line headlines.

### Mono is for *labels*, not body

Mono is a chrome material. It frames content but is never the content. Eyebrows, breadcrumbs, URL prefixes, score denominators, tag chips, footer labels — all mono, uppercase, tracked. Never set body prose in mono.

---

## 4. Layout & spacing

### Grid

- Marketing pages: `max-width: 1440px`, centered, with `padding: 0 56px` gutters.
- Product UI: full-bleed, no max-width; three-column shell.

### Section padding rhythm

Vertical pacing moves between three tempos:

```css
.pad     { padding: 56px 60px; }   /* tight */
.pad-md  { padding: 96px 56px; }   /* default section */
.pad-lg  { padding: 120px 56px; }  /* hero adjacency, marquee sections */
.pad-xl  { padding: 140px 56px; }  /* big CTA */
```

Stick to **56px** horizontal in marketing surfaces and **48px** inside product center-column. Don't invent new gutters mid-page.

### Borders > shadows

Sections are separated by **`border-bottom: 1px solid var(--ink)`**, edge to edge. There are essentially no shadows in this system. Cards earn their structure from 1px hairlines (`--line`) and shared edges, not elevation.

```css
section          { border-bottom: 1px solid var(--ink); }
.card-grid > *   { border-right: 1px solid var(--ink);
                   border-bottom: 1px solid var(--ink); }
```

Last-child / nth-child rules strip the trailing borders so the outer container's border carries the edge.

Revisi is mostly flat and structural. Depth comes from borders, grid divisions, tonal paper layers, and occasional soft ambient shadows. Shadows should support affordance, not make cards float decoratively.

### Radius

**Default radius is 0.** Squares and right angles throughout: buttons, inputs, cards, tags, mock windows. Two exceptions:

- Dot indicators: `border-radius: 50%`
- Status pills inside product UI: `border-radius: 999px` (the small `.pill` chips next to metric names — pink-soft fill, pink-deep text)

If you find yourself wanting `border-radius: 8px`, you are drifting toward a generic SaaS aesthetic. Stop.

---

## 5. Components

### Button

```html
<a class="btn">Run audit</a>            <!-- ink fill, paper text -->
<a class="btn ghost">Sign in</a>        <!-- transparent + ink border -->
<a class="btn accent">Start free</a>    <!-- pink, paper text -->
```

```css
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 16px;
  font-family: var(--sans); font-weight: 500; font-size: 14px;
  letter-spacing: -0.005em;
  background: var(--ink); color: var(--paper);
  border: 1px solid var(--ink); border-radius: 0;
  transition: transform 80ms ease, background 120ms;
}
.btn:hover  { transform: translateY(-1px); }
.btn.ghost  { background: transparent; color: var(--ink); }
.btn.ghost:hover { background: var(--ink); color: var(--paper); }
.btn.accent { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
.btn.accent:hover { background: var(--accent-deep); border-color: var(--accent-deep); }
```

Large CTAs scale padding to `18px 24px` and font to 16px. Never use a drop shadow on a button; the 1px lift on hover is the entire affordance.

### Eyebrow

The mono micro-label that introduces a section. Always preceded by a small pink square.

```html
<div class="eyebrow"><span class="num">01</span> How it works</div>
```

```css
.eyebrow {
  font-family: var(--mono); font-size: 11px; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--muted);
  display: flex; gap: 14px; align-items: center;
}
.eyebrow::before {
  content: ""; width: 6px; height: 6px; background: var(--accent);
  display: inline-block;
}
```

### Chip / tag

```html
<span class="chip">Live</span>            <!-- ink fill -->
<span class="chip outline">Beta</span>    <!-- ink border -->
<span class="chip accent">+3 flags</span> <!-- pink fill -->
```

Mono, uppercase, tracked, 4–8px padding, no radius. The pink chip is reserved for flag counts and editorial verdicts.

### Input / form bar

Single 1px border around a row of `prefix + input + button`, all flush, no radius. The prefix shows the URL scheme in mono muted; the input is sans; the submit button reverses to pink on hover.

### Squiggle underline

Apply to a `<span>` inside a headline:

```html
<h1>Read your site like an <span class="sq">editor</span></h1>
```

```css
.sq { position: relative; display: inline-block; }
.sq::after {
  content: ""; position: absolute; left: 0; right: 0; bottom: -0.05em;
  height: 16px;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 16' preserveAspectRatio='none'><path d='M 0 10 Q 7.5 2 15 10 T 30 10 T 45 10 T 60 10' fill='none' stroke='%23FF2D6F' stroke-width='3' stroke-linecap='round'/></svg>");
  background-repeat: repeat-x;
  background-size: 60px 16px;
}
```

Variants: `sq-inline` (smaller 10px height for body-size text). For inline flagged spans inside paragraphs, use native wavy underlining instead:

```css
.u {
  text-decoration-line: underline;
  text-decoration-color: var(--accent);
  text-decoration-style: wavy;
  text-decoration-thickness: 2.5px;
  text-underline-offset: 5px;
}
```

### Highlight (accent wash)

A flagged sentence gets a soft pink background and a 2px pink bottom-rule. This is the "editor's marker" treatment.

```css
.sentence.flagged .text {
  background: var(--accent-soft);
  padding: 8px 12px;
  border-bottom: 2px solid var(--accent);
}
```

For inline emphasis inside running text, use `background: var(--accent-soft)` with no border — a quieter version of the same idea. The fully saturated pink fill (`var(--accent)` + `var(--accent-ink)` text) is reserved for the editorial "insertion" tag — like a redline mark, never a sentence highlight.

### Numbered gutter (audit rows)

Every audit sentence is preceded by a 36px gutter. Unflagged rows show a faint check; flagged rows show a pink filled circle with a mono number — the count corresponds to the issue's index in the right-pane scorecard.

```css
.sentence .flag-num {
  width: 26px; height: 26px; border-radius: 50%;
  background: var(--accent); color: var(--accent-ink);
  font-family: var(--mono); font-size: 11px;
}
```

### Tabs (segmented control)

Hairline-bordered row of equal-width cells. Active cell flips to ink fill + paper text. Counts ride in a smaller mono digit underneath the label.

```css
.tabs .t.on { background: var(--ink); color: var(--paper); }
```

### Score block

Used in left pane of the audit view and inside product mocks. A massive `font-size: 72px` numeral, weight 700, paired with a small mono `/ 100` denominator and an uppercase mono label below.

### Sticky chrome bar

Sticky top nav uses translucent paper (`rgba(250,250,250,0.92)`) + `backdrop-filter: blur(12px)` + 1px ink bottom border. The product top bar drops the blur and uses solid paper, because it sits on solid paper.

### Ticker

Marquee of live audit verdicts. Mono 12px, ticker dot pink, page URL in muted, verdict reversed pink on flagged items. 60s linear infinite, no pause. Use to communicate liveness without dashboards.

### Three-column product shell

```
+-------------+------------------+--------+
|  topbar (56px)                          |
+-------------+------------------+--------+
|  280px      |  flexible        |  360px |
|  pages +    |  audit body      |  metrics
|  score      |  (centered 48px) |  + working
+-------------+------------------+--------+
|  footer (56px)                          |
+-------------+------------------+--------+
```

Outer columns scroll independently; center is the document. Footer carries the byline, finding count, and primary action.

---

## 6. Iconography & illustration

- **No emoji.** Anywhere.
- **No illustration.** The system carries voice through type, the squiggle, and ink/paper rhythm.
- Icons (when needed) are line-only, 1.5px stroke, ink color, square caps, no fills. Treat them as glyphs that sit in a mono label, not as imagery.
- The pink dot, pink square, and squiggle are the brand's only "graphics."

---

## 7. Motion

Restrained. The system reads as printed. Interactions are crisp, not bouncy.

- **Hover lift**: `transform: translateY(-1px); transition: 80ms ease;` on buttons.
- **Color crossfades**: `transition: color 120ms, background 120ms;` on links and CTAs.
- **Ticker**: 60s linear infinite, never pauses.
- No spring physics, no scroll-jacking, no parallax. The squiggle stays still.

---

## 8. Copy voice

The visual language is loud; the copy is quiet and exact. This is intentional — the design says "we have opinions"; the copy proves them.

- **Headlines are claims, not features.** "Read your site like an editor." Not "AI-powered copy analysis."
- **Mono labels are filing tabs.** Short, descriptive, ALL CAPS. "01 / METHOD", "AUDIT · SPLITPEA.CO", "+3 FLAGS".
- **Findings are imperative.** "Cut the qualifier." "Lead with the verb." "This paragraph buries the offer." Speak the way an editor writes in a margin.
- **No exclamation marks. No marketing adverbs.** Words like "seamlessly", "powerful", "robust" do not appear.

---

## 9. Do / Don't

✅ Use the pink to mark exactly one thing per surface.
✅ Set body type at 17px+; this is an editor's tool, not a dashboard.
✅ Let sections butt against each other with 1px ink dividers, no margin between.
✅ Use mono for any label that names a thing (URL, score denominator, step number).
✅ Wrap one word per headline in a squiggle or a pink span.

❌ Don't use `#ffffff` for backgrounds — `#fafafa` is the paper color.
❌ Don't soften corners. Radius is 0.
❌ Don't add shadows to create depth. Borders carry structure.
❌ Don't use the green from `Logo v2` — that exploration is closed.
❌ Don't combine pink fill, pink squiggle, and pink chip in one block.
❌ Don't set body copy in mono.
❌ Don't add icons to mono labels — the pink dot is already the decoration.
❌ Don't introduce a third typeface.

---

## 10. The Audit Report — interaction patterns

The audit report is the heart of the product. It is where the brand's editorial promise becomes a concrete tool. This section documents how its surfaces compose and behave so future product views inherit the same vocabulary.

### 10.1 Shell

A fixed three-row × three-column grid that fills the viewport. Nothing scrolls except the three body columns, independently.

```
┌─ topbar  (56px) ────────────────────────────────────────────┐
│  brand   │   audit context (URL, last scan)   │   kebab     │
├──────────┼────────────────────────────────────┼─────────────┤
│ left     │  center                            │  right      │
│ 280px    │  flex                              │  360px      │
│          │                                    │             │
│ score    │  audit body                        │  scorecard  │
│ + pages  │  (sentence list)                   │  + working  │
│          │                                    │             │
├──────────┴────────────────────────────────────┴─────────────┤
│  footer (56px) — byline · finding count · actions           │
└─────────────────────────────────────────────────────────────┘
```

- `body { height: 100vh; overflow: hidden; }` — the report is a workstation, not a page.
- Outer dividers between columns use `--line` (`#e9e9e9` in this view), not `--ink`. Inside the product, hairlines are calmer than they are on marketing pages.
- Topbar columns mirror left/right body widths (`280px / 1fr / 280px`) so the brand mark sits over the page list and the kebab sits over the scorecard. The 360px right pane in the body is wider than the 280px topbar right cell intentionally — the topbar's right cell is a chrome button, the body's right pane is content.

### 10.2 The verdict header (center column, top)

A two-line summary that opens the audit. The first line is the **verdict** — one short editorial claim with one pink-deep span that names the count of issues. The second line is a softening note (`.sub`). Together they replace what a dashboard would render as a dial.

> **Mostly strong, with clear revision targets. <span style="color:#d61f59">6 of 93 sentences</span> need attention.**
> The page is broadly aligned, with a few line-level edits worth reviewing.

Rules:

- Verdict is **17px, weight 600**, never larger. It is prose, not a headline.
- The only color used in the verdict is `--accent-deep` (not `--accent`) — a deeper pink that reads as ink against paper, not as a highlighter.
- Never use `--accent` (the bright pink) on text smaller than 18px directly on paper — at that size it vibrates. Use `--accent-deep` instead.

### 10.3 The title block

Below the verdict sits the page being audited:

- A mono URL tag (`splitpea.co`)
- The page's `<title>` as a 36px H2 — sans 700, tight tracking
- A mono type label (`SaaS feature page`)
- On the right: a giant pink score (`56px`, weight 700, `--accent`), `/ 100` in mono muted, with `Page score` as the cap

The big number is the **only place** in the audit view where `--accent` is used at large size on paper. It is the headline number of the document.

### 10.4 The sentence row — the core unit

Every line of audited copy is a `Sentence`. This is the report's most-repeated component and the place where the editorial metaphor lands hardest.

```html
<div class="sentence flagged">
  <div class="gutter"><div class="flag-num">01</div></div>
  <div class="text">Test a change. See what happens.</div>
</div>

<div class="sentence">
  <div class="gutter"><div class="check">✓</div></div>
  <div class="text">SplitPea helps small teams…</div>
</div>
```

State matrix:

| State | Gutter | Text |
|---|---|---|
| `default` (on-brand) | Faint check `✓` in `--muted-2` | 17.5px sans, ink, no decoration |
| `flagged` | Pink filled circle, 26px, with mono number | Same size + `--accent-soft` background, 2px `--accent` bottom rule, 8px×12px padding, slight negative left margin so the highlight lines up with the gutter |
| `heading` | (gutter still present, empty or check) | Sans 700, 19px — used for section delimiters like `03 · Install` inside the audited copy |

Layout rules:

- **Grid is `36px 1fr` with `18px` gap.** This is non-negotiable. The 36px gutter is what makes the report look like a manuscript with margin notes.
- Rows are stacked with `gap: 18px` — not borders. Between sentences, breathing room replaces dividers.
- The flag number in the gutter (`01`, `24`, `27`, `31`…) is the **sentence's index among flagged items only**, not its position in the document. The numbers run consecutively through the report and cross-reference the scorecard.
- A flagged sentence is `display: inline-block` so the pink wash hugs the text. Don't stretch it to the column width — that turns the editorial mark into a card.

```css
.sentence { display: grid; grid-template-columns: 36px 1fr; gap: 18px; align-items: flex-start; }
.sentence .text { font-family: var(--sans); font-size: 17.5px; line-height: 1.55; letter-spacing: -0.005em; color: var(--ink); }
.sentence.flagged .text {
  background: var(--accent-soft);
  padding: 8px 12px;
  border-bottom: 2px solid var(--accent);
  margin-left: -12px;
  display: inline-block;
}
```

**Do not** add icons, tags, hover popovers, or expand chevrons to the sentence row in the default state. The number is the affordance. Anything else clicked on it would be revealed elsewhere in the shell (right pane), not inline.

### 10.5 The left pane — pages + score

Stacked sections, separated by padding (no rule between them):

1. **Score block** — `87 / 100` at 72px ink, with `Brand voice` as a mono label below. This is the *site* score, not the page score (the page score lives in the center title block).
2. **Pages** section with:
   - A row header: `Pages` H3 + a mono pagination cluster on the right
   - A 3-cell **segmented control** (`Needs review` · `All` · `On-brand`) with a count chip under each label
   - A `.pglist` — vertically stacked page rows, each showing title (truncated with ellipsis), path in mono, a big page-score on the right, and a `N flags` mono caption

Active page treatment:

```css
.pglist .pg.active {
  border-left: 2px solid var(--accent);
  padding-left: 14px; margin-left: -14px;
  padding-right: 14px; margin-right: -14px;
}
```

The full-bleed wash on `.active` is what makes "I am currently viewing this page" feel like a marked entry in a list rather than a button. The 2px pink left rule is the same gesture as the flagged-sentence underline — it is the editor's tick.

### 10.6 The right pane — scorecard + what's working

The right pane is a vertical stack of three blocks:

1. **Header row** — `Voice scorecard` H3 + sub + an `expand` square button (chevron), separated from the metrics by a 1px line.
2. **Metrics list** — one row per voice metric (`Brand Fit`, `Audience Fit`, `Clarity`, `Human Sound`, `Specificity`, `Trust`, `Distinctiveness`). Each row has:
   - Name (sans 700, 17px) + pill on the right
   - Bar (5px tall, paper-2 track, ink fill — pink fill if drifting)
   - 13.5px muted description
3. **What is working** — a small list of editorial observations, each item with a 2px pink left-rule (same gesture as the active page), 13.5px sans, ink-2 color.

Pill semantics:

```css
.metric .pill        { background: var(--accent-soft); color: var(--accent-deep); border-radius: 999px; }
.metric .pill.drift  { background: var(--ink);         color: var(--paper); }
```

Note the inversion: `On-Brand` reads as soft pink (a calm verdict), `Drifting` reads as solid ink (a harder verdict). Pink is **not** the failure color in metric pills — it is the brand mark itself, used here as a stamp of identity. Failure escalates to ink fill, the visual equivalent of crossing something out.

This is the only place in the system where pill `border-radius: 999px` appears. It is the only place where rounded corners are permitted. Treat this as a deliberate exception, not license to add radius elsewhere.

### 10.7 The footer

A three-cell strip that mirrors the topbar's grid but with content rather than chrome:

- **Byline** — a 28px ink avatar circle with the user's initial + `Reviewed by Revisi` / mono note `Inferred voice · not confirmed`. The "inferred voice" caveat is part of the product's voice: never overclaim.
- **Findings summary** — sans 13.5px, ink: `**6 findings** on this page · roughly 36 min to fix`. Time-to-fix is a Revisi signature — it converts editorial mess into a unit of work.
- **Actions** — flush-right cells separated by 1px lines: `Share`, `Export PDF`, then a primary `Run another scan` in ink. The primary action's hover state flips to pink (`--accent`) — the only place in the footer where the accent appears.

### 10.8 Audit-view rules of thumb

✅ Numbers in the gutter are **flag indices**, not sentence positions. Renumber when filters change.
✅ Use `--accent-deep` (not `--accent`) for any small text on paper that needs to read as pink.
✅ Section headings inside the audited copy use `.sentence.heading` — they are still rows, still have a gutter. They do not become H2s.
✅ Three columns scroll independently. The center is the document; the left and right are tools.

❌ Don't add a sentence-level menu, expansion, or hover popover. The model is: read the sentence, see its number, find it in the scorecard.
❌ Don't tint flagged sentences with the saturated `--accent`. The wash is `--accent-soft`; the rule beneath it is `--accent`.
❌ Don't put `--ok` green anywhere in the audit view. On-brand sentences get a quiet check in muted ink. The audit is a document of revisions; even passing copy isn't celebrated.
❌ Don't add a progress bar, completion %, or "X of Y reviewed" tracker. The report is a static reading, not a task list.

---

## 11. File references

| Artifact | Source |
|---|---|
| Logomark explorations | `Revisi Logo v2.html`, `logos.jsx` |
| Marketing homepage | `Revisi Homepage.html`, `homepage.jsx` |
| In-product audit view | `Revisi Audit Report v2.html`, `audit-report-v2.jsx` |
| Shared styles | `styles.css` |

When extending the system, copy tokens from one of the three HTML files above — they are the source of truth. Update this doc when a new pattern is canonized across two or more surfaces.
