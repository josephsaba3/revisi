---
name: brand-voice-auditor
description: Audit website, landing page, blog, marketing, pasted, local HTML/Markdown/MDX/TXT, JSON content blocks, or fetched URL copy for brand voice fit, clarity, specificity, trust, conversion readiness, and AI-sludge risk. Use for requests such as brand voice audit, copy audit, website copy critique, AI-sludge check, clarity audit, content voice review, landing page copy review, does this sound like my brand, does this sound AI-generated, or rewrite this to fit the brand voice. Do not use for technical SEO audits, keyword research, UI/design critique, accessibility audits, performance audits, general grammar-only proofreading, or SaaS/app builds.
---

# Brand Voice Auditor

## Purpose

Audit copy as a structured diagnostic product, not a loose critique. Help a founder, marketer, freelancer, or small business owner decide whether content sounds like the intended brand, feels human, explains the offer clearly, earns trust, and gives readers a reason to act.

Never build a SaaS app, frontend, auth, payment flow, database, or dashboard for this skill. Produce Markdown reports and, when requested, focused rewrites.

## Supported Inputs

Accept any mix of:

- Local `.html`, `.md`, `.mdx`, `.txt`, or obvious JSON content-block files.
- Pasted copy.
- A URL if available tools can fetch it.
- A provided brand voice guide.
- A short brand description when no guide exists.
- Optional audience, competitor, or industry context.

If no brand voice guide is provided, infer a provisional voice from the strongest available copy and label it exactly as `inferred voice, not confirmed`. Do not invent brand values. Ask at most one clarifying question only when the audit would be impossible without it; otherwise proceed with stated assumptions.

## Reference Loading

Load only the references needed for the current request:

- `references/report_template.md`: always use for a full audit report.
- `references/brand_voice_rubric.md`: use when scoring or explaining criteria.
- `references/scoring_guide.md`: use when assigning 0-100 scores or verdict labels.
- `references/phrase_flags.md`: use for deterministic phrase and pattern checks.
- `references/rewrite_rules.md`: use before writing replacements or mini voice-guide examples.
- `assets/sample_report.md`: use only when the user asks for an example or when calibrating report shape.

## Audit Workflow

1. Gather content.
   - Identify pages, paths, URLs, sections, or pasted blocks reviewed.
   - Extract meaningful visible copy.
   - Ignore repeated nav, boilerplate, legal, and footer text unless it affects the voice or conversion path.
   - Preserve source paths, headings, and section names where possible.

2. Establish the intended voice.
   - Prefer a supplied brand voice guide over inference.
   - If using inference, state `inferred voice, not confirmed`.
   - Summarize the intended voice in 3-6 plain-English bullets.

3. Run deterministic checks.
   - Flag AI-sounding phrases, SaaS buzzwords, vague claims, inflated adjectives, over-polished corporate language, overuse of em dashes, long sentences, passive or abstract phrasing, weak CTAs, unclear product explanation, generic benefit claims, repeated phrases, audience mismatch, trust gaps, and unsupported claims.

4. Run judgment-based review.
   - Select the closest scoring context before assigning the overall score.
   - Score Brand Fit, Audience Fit, Clarity, Human Sound, Specificity, Trust, and Distinctiveness from 0-100.
   - Score AI Sludge Risk from 0-100, where higher is worse.
   - Apply 2-4 contextual modifiers to explain which expectations were stricter for the page type.

5. Produce a structured Markdown report.
   - Use `references/report_template.md` as the shape.
   - Keep the tone direct, practical, specific, and fair.
   - Avoid generic praise, fake certainty, and SEO advice unless copy clarity overlaps with search intent.
   - Avoid overusing bold formatting.

## Scoring Rules

Always score these core metrics:

- Brand Fit
- Audience Fit
- Clarity
- Human Sound
- Specificity
- Trust
- Distinctiveness

Choose the closest scoring context before computing the overall score. If none fits cleanly, use `general brand copy` and state the assumption.

### Scoring Context Weights

Use these presets unless the user gives a stronger business context. If the content type or industry changes the risk profile, choose the closest preset and state which one was used.

| Metric | SaaS feature page | Dental / healthcare page | Founder-led homepage | Blog / educational content | General brand copy |
|---|---:|---:|---:|---:|---:|
| Brand Fit | 16% | 10% | 20% | 10% | 16% |
| Audience Fit | 12% | 16% | 10% | 12% | 13% |
| Clarity | 22% | 18% | 17% | 22% | 19% |
| Human Sound | 14% | 12% | 18% | 15% | 15% |
| Specificity | 18% | 14% | 8% | 17% | 15% |
| Trust | 10% | 24% | 12% | 18% | 14% |
| Distinctiveness | 8% | 6% | 15% | 6% | 8% |

### Contextual Modifiers

Apply 2-4 modifiers. Do not score every modifier every time. Use modifiers to explain why certain core metrics were weighted more heavily or judged more strictly.

| Modifier | What it changes | Use when |
|---|---|---|
| Conversion Readiness | Raises expectations for CTA clarity, objection handling, and action path. | Landing pages, product pages, service pages, sales pages, signup pages. |
| Message Hierarchy | Raises expectations for information order and early comprehension. | The page has multiple sections, audiences, offers, or decisions. |
| Risk / Sensitivity Level | Raises Trust and Audience Fit expectations. | Healthcare, dental, legal, finance, childcare, safety, or high-stakes personal decisions. |
| Proof Requirement | Raises Trust and Specificity expectations. | The copy makes expertise, outcome, quality, security, or performance claims. |
| Decision Complexity | Raises Clarity, Specificity, and objection-handling expectations. | Readers need to compare options, understand process, or evaluate tradeoffs before acting. |
| Emotional Stakes | Raises Human Sound, Trust, and Audience Fit expectations. | The reader may feel anxious, embarrassed, overwhelmed, uncertain, or exposed. |
| Category Familiarity | Changes how much explanation is required for Clarity. | The audience may not already understand the product, treatment, service, or method. |
| Objection Handling | Raises expectations for answering doubts before the CTA. | Price, risk, timing, difficulty, proof, switching cost, or credibility are likely blockers. |
| Local / Personal Reassurance | Raises expectations for real-world credibility and approachability. | Local service, healthcare, coaching, consulting, legal, or founder-led pages. |

### Metric Definitions

- Brand Fit: Does this sound like this brand? Judge alignment with the supplied guide or inferred voice.
- Audience Fit: Does this speak to the right reader, their situation, and their level of knowledge?
- Clarity: Can a new reader quickly understand what this is, who it is for, why it matters, and what to do next?
- Human Sound: Does it sound like a real person wrote it, or does it feel synthetic, over-polished, or formulaic?
- Specificity: Are claims grounded in concrete nouns, examples, mechanisms, workflows, outcomes, constraints, or proof?
- Trust: Does the copy give readers enough reason to believe the claims and feel safe continuing?
- Distinctiveness: Is there a memorable point of view or ownable language, or could any competitor say the same thing?

Apply AI Sludge Risk as a penalty after the weighted average:

- 0-20: no penalty
- 21-40: minus 4 points
- 41-60: minus 9 points
- 61-80: minus 16 points
- 81-100: minus 25 points

Do not let AI Sludge Risk directly increase the overall score. Clamp the final score to 0-100.

If AI Sludge Risk is 70 or higher, the final overall score cannot exceed 74.
If AI Sludge Risk is 85 or higher, the final overall score cannot exceed 59.

Use these verdict labels:

- 90-100: Sharp and distinctive
- 75-89: Strong, with clear revision targets
- 60-74: Usable but generic or under-supported
- 40-59: Understandable but off-brand
- 0-39: Needs serious rewrite

## Report Requirements

A full audit must include these sections in order:

1. `# Brand Voice & Clarity Audit`
2. `## Audit Context`
3. `## Executive Summary`
4. `## Scorecard`
5. `## AI Sludge Risk`
6. `## What's Working`
7. `## Highest-Priority Fixes`
8. `## Line-Level Audit`
9. `## Before / After Rewrites`
10. `## Generated Mini Voice Guide`
11. `## Founder / Team Questions`
12. `## Final Recommendation`
13. `## Machine-Readable Summary`

The machine-readable summary must be a fenced `json` block with: `overall_score`, `verdict`, `scoring_context`, `contextual_modifiers`, `scores`, `ai_sludge_risk`, `top_issues`, `top_rewrites`, and `recommended_next_action`.

## Rewriting Guidance

When rewriting, keep the user's intent and the brand's level of warmth. Prefer specific nouns and verbs, concrete outcomes, short sentences, and believable proof. Do not create fake metrics, testimonials, customer names, certifications, guarantees, or product capabilities. Preserve claims only when supported by the source copy.
