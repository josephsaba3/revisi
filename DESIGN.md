---
name: SplitPea
description: Calm, helpful experimentation UI for small teams testing modern websites.
colors:
  garden-ink: "#171a16"
  garden-dark: "#1E2A16"
  pea-green: "#416c38"
  deep-evergreen: "#2d4f29"
  deep-teal: "#102f31"
  deep-teal-pressed: "#0b2425"
  harvest-orange: "#f5a623"
  warm-cream: "#fbf8ee"
  soft-cream: "#f4efe3"
  aged-cream: "#ebe4d4"
  warm-white: "#fffdf7"
  muted-olive: "#67675f"
  faint-olive: "#928b7b"
  parchment-line: "#ded4c2"
typography:
  display:
    fontFamily: '"Crimson Pro", Georgia, "Times New Roman", Times, serif'
    fontSize: "clamp(3.5rem, 7.4vw, 8rem)"
    fontWeight: 500
    lineHeight: 0.84
    letterSpacing: "-0.035em"
  headline:
    fontFamily: '"Crimson Pro", Georgia, "Times New Roman", Times, serif'
    fontSize: "clamp(2.6rem, 5vw, 4.4rem)"
    fontWeight: 500
    lineHeight: 0.9
    letterSpacing: "-0.055em"
  title:
    fontFamily: '"Crimson Pro", Georgia, "Times New Roman", Times, serif'
    fontSize: "2rem"
    fontWeight: 500
    lineHeight: 0.92
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "0"
  label:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: ".66rem"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: ".24em"
rounded:
  pill: "999px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "36px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  section: "72px"
components:
  button-dark:
    backgroundColor: "{colors.garden-ink}"
    textColor: "{colors.warm-white}"
    rounded: "{rounded.pill}"
    padding: "11px 16px"
    typography: "{typography.body}"
  button-green:
    backgroundColor: "{colors.pea-green}"
    textColor: "{colors.warm-white}"
    rounded: "{rounded.pill}"
    padding: "11px 16px"
    typography: "{typography.body}"
  button-orange:
    backgroundColor: "{colors.harvest-orange}"
    textColor: "#23170a"
    rounded: "{rounded.pill}"
    padding: "11px 16px"
    typography: "{typography.body}"
  button-outline:
    backgroundColor: "{colors.warm-cream}"
    textColor: "{colors.garden-ink}"
    rounded: "{rounded.pill}"
    padding: "11px 16px"
    typography: "{typography.body}"
  card-default:
    backgroundColor: "{colors.warm-white}"
    textColor: "{colors.garden-ink}"
    rounded: "{rounded.lg}"
    padding: "26px"
  chip-kicker:
    backgroundColor: "{colors.warm-white}"
    textColor: "{colors.muted-olive}"
    rounded: "{rounded.pill}"
    padding: "8px 12px"
    typography: "{typography.label}"
---

# Design System: SplitPea

## 1. Overview

**Creative North Star: "The Calm Lab Notebook"**

SplitPea should feel like a product surface for people making careful decisions: calm, legible, warm, and useful. The visual system borrows from paper, garden tones, soft browser chrome, and plain product controls, so experimentation feels like a manageable workflow rather than a growth-team ritual.

The system is quietly tactile and evidence-led. Rounded pills, bordered panels, restrained ambient shadows, and serif display type create warmth, while compact labels, tables, snippets, and report previews keep the interface practical. It must stay confident without becoming arrogant, clear without becoming sterile, and helpful without becoming cute.

It explicitly rejects enterprise experimentation software, enterprise analytics dashboards, noisy startup hype, forced quirk, mascots, and inflated claims. If a screen looks like it is trying to impress investors instead of helping a small team decide what to test, it is off-brand.

**Key Characteristics:**
- Warm cream surfaces with garden-green structure.
- Large serif headlines balanced by clear sans body copy.
- Soft bordered cards and browser-like previews, never heavy glass.
- Orange used as a direct action accent, not decoration.
- Evidence patterns that explain decisions without statistical theater.

## 2. Colors

The palette is warm, grounded, and restrained: cream paper surfaces, garden greens, deep evergreen product moments, and a small harvest-orange action accent.

### Primary
- **Pea Green**: The default product accent for active navigation, icons, status marks, and trustworthy highlights.
- **Deep Evergreen**: The strongest product surface, used for featured plans, dark fact sections, and moments that need weight without feeling corporate.

### Secondary
- **Harvest Orange**: The conversion accent for primary marketing CTAs and important action buttons. Use it sparingly so it keeps its signal.

### Tertiary
- **Deep Teal**: The calm dark field for ribbons and final calls to action. It adds depth while staying warmer than a generic navy.
- **Garden Dark**: The darkest organic green for section backgrounds and strong contrast moments.

### Neutral
- **Garden Ink**: The default text and dark button color. It is green-tinted, not pure black.
- **Warm Cream**: The main page background, used for calm reading surfaces.
- **Soft Cream**: The secondary page band for blog and quiet transitions.
- **Aged Cream**: A denser cream for subtle fills and separators.
- **Warm White**: Card and elevated surface fill, warmer than pure white.
- **Muted Olive**: Body-secondary copy and supportive descriptions.
- **Faint Olive**: Tiny labels, eyebrow text, and low-emphasis metadata.
- **Parchment Line**: Borders, dividers, table rules, and card outlines.

### Named Rules

**The Warm Neutral Rule.** Never use pure black or pure white for new UI. Use Garden Ink and Warm White so the product keeps its quiet warmth.

**The Orange Means Action Rule.** Harvest Orange is for calls to action and high-signal progress, not for random decoration or icon garnish.

**The Green Carries Trust Rule.** Pea Green and Deep Evergreen should communicate status, selection, confidence, and product structure.

## 3. Typography

**Display Font:** Crimson Pro (with Georgia and Times fallbacks)  
**Body Font:** Inter or system sans (with platform UI fallbacks)  
**Label/Mono Font:** JetBrains Mono for snippets, otherwise Inter/system labels

**Character:** The pairing is warm and editorial without becoming magazine-like. Crimson Pro gives SplitPea a human, almost notebook-like voice; Inter keeps controls, navigation, and explanations crisp.

### Hierarchy
- **Display** (500, clamp(3.5rem, 7.4vw, 8rem), 0.84): Homepage and major page hero headlines only.
- **Headline** (500, clamp(2.6rem, 5vw, 4.4rem), 0.9): Dark fact numbers, major section titles, and high-emphasis storytelling.
- **Title** (500, 2rem, 0.92): Feature cards, pricing titles, report previews, and repeated content blocks.
- **Body** (400, 1rem, 1.45): Product explanations, FAQ copy, pricing descriptions, and ordinary page text. Keep long-form copy comfortable, roughly 65 to 75 characters per line.
- **Label** (800, .66rem, .24em, uppercase): Tiny section labels, category tags, and table headers. Use sparingly; too many tiny labels make the site feel fussy.

### Named Rules

**The One Serif Voice Rule.** Crimson Pro is for hierarchy and warmth, not for every piece of text. Controls and body copy stay sans so the product still feels usable.

**The Plain Explanation Rule.** Never let type styling compensate for vague copy. SplitPea earns trust through direct words first.

## 4. Elevation

SplitPea uses a hybrid of tonal layering, borders, and soft ambient shadows. Most depth comes from cream-on-cream surfaces, parchment borders, and browser-like framing. Shadows are quiet and diffuse, never glossy, dramatic, or glassy.

### Shadow Vocabulary
- **Ambient Card** (`box-shadow: 0 28px 80px rgba(65, 51, 31, .13)`): Featured pricing cards and large high-emphasis framed surfaces.
- **Soft Panel** (`box-shadow: 0 16px 48px rgba(65,51,31,.10)`): Mini windows and product preview panels.
- **Low Lift** (`box-shadow: 0 12px 38px rgba(65,51,31,.05)`): Feature cards and quiet repeated panels.
- **State Lift** (`box-shadow: 0 12px 30px rgba(65,51,31,.09)`): Small floating labels, badges, or interaction responses.

### Named Rules

**The Border Before Shadow Rule.** Start with a Parchment Line border and warm surface. Add shadow only when the surface needs to read as interactive, featured, or spatially above the page.

**The No Glass Rule.** Blurred sticky chrome is acceptable for navigation; decorative glass cards are forbidden.

## 5. Components

### Buttons

Buttons are pill-shaped, compact, and practical. They should feel easy to press, not oversized or theatrical.

- **Shape:** Fully rounded pill (999px).
- **Primary:** Use Garden Ink for default serious actions, Pea Green for product entry actions, or Harvest Orange for the strongest conversion CTA.
- **Hover / Focus:** A small upward movement is acceptable (`translateY(-1px)`). Add visible focus states when extending the system.
- **Secondary / Ghost / Tertiary:** Outline buttons use Warm Cream, Parchment Line, and Garden Ink. They should stay quiet beside filled CTAs.

### Chips

Chips and kickers act like calm labels, not badges shouting for attention.

- **Style:** Warm White or translucent cream fill, Parchment Line border, Muted Olive text, small dot when status needs emphasis.
- **State:** Active or verified states can use Pea Green through the dot or text, not through full saturation.

### Cards / Containers

Cards are softly bounded product surfaces.

- **Corner Style:** Rounded but not bubbly, usually 24px to 30px for marketing cards and 16px to 22px for denser product previews.
- **Background:** Warm White for cards, Warm Cream for previews, Deep Evergreen for featured or dark sections.
- **Shadow Strategy:** Borders first, shadows second. Use Low Lift for repeated cards and Ambient Card only for featured surfaces.
- **Border:** Parchment Line on light surfaces; translucent warm white on dark surfaces.
- **Internal Padding:** 24px to 28px for cards; tighter 16px panels inside product previews.

### Inputs / Fields

The marketing site mostly demonstrates fields rather than accepting input, but new fields should inherit the same surface language.

- **Style:** Warm White or Warm Cream fill, Parchment Line border, 12px to 16px radius, readable sans text.
- **Focus:** Shift border to Pea Green and add a soft green focus ring. Never remove focus outlines without replacement.
- **Error / Disabled:** Error states should use clear copy and a restrained warm warning tone. Disabled states should lower contrast without becoming unreadable.

### Navigation

Navigation is centered, sticky, calm, and product-like.

- **Style:** 66px sticky header, translucent Warm Cream, subtle blur, Parchment Line bottom border.
- **Typography:** Small sans links with muted default color and Pea Green active state.
- **Actions:** Sign-in stays outline; start-free action is filled green.
- **Mobile Treatment:** Hide secondary actions before crowding the header. Preserve clear tap targets.

### Signature Component: Product Preview Window

Product previews use browser-like chrome, cream surfaces, subtle borders, and realistic snippets or report cards. They should show actual product state: variants, confidence, install snippets, editor selection, or decisions. Avoid generic abstract illustrations.

## 6. Do's and Don'ts

### Do:

- **Do** use Warm Cream, Warm White, Parchment Line, and Garden Ink as the base structure for new pages.
- **Do** use Pea Green for confidence, selection, verification, active navigation, and product structure.
- **Do** keep Harvest Orange rare and action-specific.
- **Do** make result states plain and useful: winner, loser, running, inconclusive, or needs more data.
- **Do** show product reality through snippets, report previews, editor states, and clear workflows.
- **Do** keep copy calm, warm, and direct.

### Don't:

- **Don't** make SplitPea look or sound arrogant.
- **Don't** make it feel enterprise, enterprise analytics, or growth-team-only.
- **Don't** use noisy startup hype, forced quirk, mascots, inflated claims, or VC SaaS language.
- **Don't** use glassmorphism as a decorative card style.
- **Don't** use pure black, pure white, neon palettes, or generic navy-and-gold SaaS cues.
- **Don't** turn every section into identical icon cards.
- **Don't** add colored side-stripe borders as accents.
- **Don't** use gradient text.
