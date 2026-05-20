---
name: Revisi
description: Brand voice auditor for marketers, founders, and agencies.
colors:
  ink: "#171a16"
  dark-panel: "#050505"
  warm-cream: "#fbf8ee"
  soft-cream: "#f4efe3"
  aged-cream: "#ebe4d4"
  warm-white: "#fffdf7"
  parchment: "#ded4c2"
  muted-olive: "#67675f"
  faint-olive: "#928b7b"
  pea: "#416c38"
  deep-evergreen: "#2d4f29"
  editorial-pink: "#ff2d6f"
  brick: "#944226"
  harvest: "#f5a623"
  harvest-deep: "#c48118"
typography:
  display:
    fontFamily: "IBM Plex Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(64px, 7.8vw, 120px)"
    fontWeight: 800
    lineHeight: 0.9
    letterSpacing: "0"
  headline:
    fontFamily: "IBM Plex Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(40px, 5vw, 72px)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "0"
  title:
    fontFamily: "IBM Plex Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "0"
  body:
    fontFamily: "IBM Plex Sans, ui-sans-serif, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "0"
  label:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "10px"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "0.18em"
rounded:
  sm: "8px"
  md: "8px"
  lg: "8px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "12px"
  md: "18px"
  lg: "28px"
  xl: "56px"
components:
  button-primary:
    backgroundColor: "{colors.editorial-pink}"
    textColor: "{colors.warm-white}"
    rounded: "{rounded.sm}"
    padding: "12px 18px"
  button-utility:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.warm-white}"
    rounded: "{rounded.sm}"
    padding: "10px 14px"
  input-url:
    backgroundColor: "{colors.warm-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "16px 18px"
  report-panel:
    backgroundColor: "{colors.warm-cream}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "28px"
---

# Design System: Revisi

## 1. Overview

**Creative North Star: "The Copy Desk Console"**

Revisi should feel like a focused editorial workspace: large decisive type, quiet reading surfaces, exact line-level marks, and a small number of highly visible action colors. The design has two modes. The marketing surface can be expressive and memorable, but the report workspace should feel like a professional copy desk where every mark has a reason.

The system rejects generic AI SaaS polish, Grammarly-like bloat, dense enterprise tooling, playful copy toys, and heavy admin dashboards. It should look useful for a small site and still credible for an agency reviewing many pages.

**Key Characteristics:**

- Editorial, not decorative.
- Sparse controls, high signal.
- Pink is an annotation color, not a general decoration.
- Borders and grid lines create structure before shadows do.
- Large typography is reserved for marketing claims and report scores.

## 2. Colors

The palette is warm editorial paper, black ink, garden green, and a sharp pink markup accent.

### Primary

- **Ink Black** (#171a16): Primary text, report chrome, bars, score emphasis, and utility buttons.
- **Editorial Pink** (#ff2d6f): Flags, squiggles, critical emphasis, active marketing CTAs, and visible "look here" moments.
- **Pea Green** (#416c38): Positive states, brand support, progress, and quiet success cues.

### Secondary

- **Deep Evergreen** (#2d4f29): Hover and deeper state for green actions.
- **Brick Review** (#944226): Warnings, issue context, and warm diagnostic accents.
- **Harvest Note** (#f5a623): Occasional warning or note color where pink would imply a stronger editorial flag.

### Neutral

- **Warm Cream** (#fbf8ee): Default page background.
- **Soft Cream** (#f4efe3): Secondary surface and low-contrast sections.
- **Aged Cream** (#ebe4d4): Disabled or recessed surface.
- **Warm White** (#fffdf7): Inputs and foreground panels.
- **Parchment Line** (#ded4c2): Dividers, borders, table/grid rules.
- **Muted Olive** (#67675f): Secondary text.
- **Faint Olive** (#928b7b): Hints, timestamps, and low-priority metadata.
- **Dark Panel** (#050505): Immersive dark sections and footer surfaces only.

### Named Rules

**The Annotation Rule.** Pink means editorial attention. Use it for flags, squiggles, highlights, and high-value CTAs. Do not spread it across generic decoration.

**The Paper Rule.** Warm cream and parchment should make reading feel calm. Avoid pure white or pure black surfaces.

## 3. Typography

**Display Font:** IBM Plex Sans, with system sans fallback  
**Body Font:** IBM Plex Sans, with system sans fallback  
**Editorial Serif:** Crimson Pro, for selected italic emphasis and wordmark-like moments  
**Label/Mono Font:** JetBrains Mono

**Character:** The type system is blunt, readable, and editorial. IBM Plex Sans carries the working product; Crimson Pro adds copy-desk personality only where contrast helps.

### Hierarchy

- **Display** (800, `clamp(64px, 7.8vw, 120px)`, 0.9): Marketing hero lines and major closing claims.
- **Headline** (800, `clamp(40px, 5vw, 72px)`, 0.95): Section headings and large product statements.
- **Title** (700, `24px`, 1.15): Panel headings, report titles, cards, and section labels.
- **Body** (400, `16px`, 1.45): Reading copy, report explanations, and form content. Keep long reading areas around 65 to 75ch.
- **Label** (500, `10px`, 1.3, uppercase mono with tracking): Metadata, audit states, page type, timestamps, and status labels.

### Named Rules

**The Reading First Rule.** Report copy must beat visual drama. Do not compress findings, explanations, or rewrites just to preserve a layout.

**The Big Type Earns It Rule.** Use hero-scale type only for landing page statements, major CTAs, and scores. Do not use oversized type inside compact controls.

## 4. Elevation

Revisi is mostly flat and structural. Depth comes from borders, grid divisions, tonal paper layers, and occasional soft ambient shadows. Shadows should support affordance, not make cards float decoratively.

### Shadow Vocabulary

- **Ambient Low** (`0 12px 38px rgb(65 51 31 / 5%)`): Light lift for active drop areas, selected cards, and quiet hover state.
- **Ambient Mid** (`0 16px 48px rgb(65 51 31 / 10%)`): Rare emphasis for active or foregrounded controls.

### Named Rules

**The Grid Before Shadow Rule.** Reach for a divider, border, or surface change before adding a shadow.

## 5. Components

### Buttons

- **Shape:** Mostly squared editorial buttons with 8px radius; utility pills may use 999px.
- **Primary:** Editorial pink background with warm-white text, compact padding, strong weight.
- **Utility:** Ink-black background with warm-white text for report actions and panel toggles.
- **Hover / Focus:** Subtle color or border shift with a visible focus ring. Avoid bounce and elastic motion.
- **Ghost:** Warm-cream or transparent background with ink text and parchment border.

### Chips

- **Style:** Small mono or sans labels, pill radius, muted surface, and status-specific text color.
- **State:** Green means on-brand or complete. Pink means review or flag. Muted means neutral metadata.

### Cards / Containers

- **Corner Style:** 8px radius or square report cells.
- **Background:** Warm cream, soft cream, and warm white.
- **Shadow Strategy:** Flat by default. Use ambient low only for active or selected states.
- **Border:** 1px parchment or ink in report views.
- **Internal Padding:** 18px to 28px depending on density.

### Inputs / Fields

- **Style:** Warm-white background, parchment border, 8px radius, calm spacing.
- **Focus:** Border shift plus a soft green ring.
- **Error / Disabled:** Brick for errors, aged cream for disabled fields. Pair status with words, not color alone.

### Navigation

Marketing navigation is minimal and airy. Audit navigation is utilitarian: topbar, page list, report actions, and collapsible side panels. Keep nav labels short and avoid exposing unused product breadth.

### Audit Workspace

The report is the signature component. It uses three functional zones: page list, document, scorecard. Findings appear inline, with the original sentence first and explanations revealed on demand. The workspace should always preserve reading flow.

## 6. Do's and Don'ts

### Do:

- **Do** keep Revisi niche and sharp: scan, diagnose, revise, rescore.
- **Do** use pink for editorial attention: flags, highlights, squiggles, and decisive CTAs.
- **Do** let borders and grid lines organize report surfaces.
- **Do** preserve generous reading space in the report document.
- **Do** make large and small sites feel equally supported without adding enterprise bloat.
- **Do** support WCAG 2.2 AA, keyboard navigation, reduced motion, and non-color status cues.

### Don't:

- **Don't** make the product feel like generic AI SaaS.
- **Don't** copy Grammarly's broad writing-assistant shape or feature bloat.
- **Don't** make the report busy, dense, or enterprise-heavy.
- **Don't** turn the brand into a playful copywriting toy.
- **Don't** use gradient text, decorative glass cards, side-stripe card accents, or repeated identical icon-card grids.
- **Don't** use pure #000 or #fff as the primary surface language.
