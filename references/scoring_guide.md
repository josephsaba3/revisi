# Scoring Guide

Use 0-100 scores. Scores should be useful, not falsely precise. Round to whole numbers.

## Bands

| Band | Label | Meaning |
|---|---:|---|
| 90-100 | Excellent | Distinctive, clear, credible, and ready to publish with only minor edits. |
| 75-89 | Strong | Works well, with clear revision targets such as missed proof, weak specificity, or uneven voice. |
| 60-74 | Adequate | Usable but generic, soft, or under-supported. Needs targeted revision before it feels strong. |
| 40-59 | Weak | Readers can follow it, but the voice, clarity, proof, or offer is materially off. |
| 0-39 | Poor | Confusing, generic, unsupported, off-brand, or likely to reduce trust. |

## Core Metrics

Always score these metrics:

- Brand Fit
- Audience Fit
- Clarity
- Human Sound
- Specificity
- Trust
- Distinctiveness

Do not score Conversion Readiness as a default core metric. Treat it as a contextual modifier unless the page is explicitly a landing page, product page, service page, sales page, or signup page.

## Scoring Context Weights

Choose the closest context before computing the overall score. If none fits cleanly, use `general brand copy` and state the assumption.

| Metric | SaaS feature page | Dental / healthcare page | Founder-led homepage | Blog / educational content | General brand copy |
|---|---:|---:|---:|---:|---:|
| Brand Fit | 16% | 10% | 20% | 10% | 16% |
| Audience Fit | 12% | 16% | 10% | 12% | 13% |
| Clarity | 22% | 18% | 17% | 22% | 19% |
| Human Sound | 14% | 12% | 18% | 15% | 15% |
| Specificity | 18% | 14% | 8% | 17% | 15% |
| Trust | 10% | 24% | 12% | 18% | 14% |
| Distinctiveness | 8% | 6% | 15% | 6% | 8% |

## Contextual Modifiers

Apply 2-4 modifiers. Use them to explain why certain core metrics were weighted more heavily or judged more strictly.

| Modifier | What it changes |
|---|---|
| Conversion Readiness | Raises expectations for CTA clarity, objection handling, and action path. |
| Message Hierarchy | Raises expectations for information order and early comprehension. |
| Risk / Sensitivity Level | Raises Trust and Audience Fit expectations. |
| Proof Requirement | Raises Trust and Specificity expectations. |
| Decision Complexity | Raises Clarity, Specificity, and objection-handling expectations. |
| Emotional Stakes | Raises Human Sound, Trust, and Audience Fit expectations. |
| Category Familiarity | Changes how much explanation is required for Clarity. |
| Objection Handling | Raises expectations for answering doubts before the CTA. |
| Local / Personal Reassurance | Raises expectations for real-world credibility and approachability. |

## Dimension Scoring Examples

### Brand Fit

- 90-100: Sounds unmistakably aligned with the guide; consistent across sections.
- 75-89: Mostly aligned, with a few generic or off-tone moments.
- 60-74: Acceptable tone, but little brand character.
- 40-59: Noticeable mismatch with audience or guide.
- 0-39: Sounds like a different company.

### Audience Fit

- 90-100: Speaks directly to the right reader, their situation, and their level of knowledge.
- 75-89: Mostly audience-aware, with a few generic or mismatched moments.
- 60-74: Understands the broad audience but misses important context, anxieties, or buying-stage details.
- 40-59: Often speaks to the wrong reader, wrong level of sophistication, or wrong motivation.
- 0-39: Audience is unclear or materially mismatched.

### Clarity

- 90-100: Product, audience, value, and next step are obvious quickly.
- 75-89: Clear overall, but some sections need sharper nouns or sequence.
- 60-74: Reader understands the category but not the exact offer or why it matters.
- 40-59: Many abstract claims; important details are buried.
- 0-39: Reader cannot tell what is being sold.

### Human Sound

- 90-100: Natural, specific, confident, and free of formulaic filler.
- 75-89: Mostly human with occasional polished template language.
- 60-74: Competent but synthetic or overly smooth in places.
- 40-59: Repetitive, corporate, or AI-like enough to hurt trust.
- 0-39: Reads like generic generated marketing copy.

### Specificity

- 90-100: Uses concrete examples, workflows, outcomes, constraints, and proof.
- 75-89: Specific enough, with a few vague claims to replace.
- 60-74: Some concrete detail, but major benefits remain generic.
- 40-59: Mostly abstract; could fit many businesses.
- 0-39: Almost no concrete nouns or verifiable claims.

### Trust

- 90-100: Claims are supported, transparent, and believable.
- 75-89: Credible, but needs a few more proof points or clearer caveats.
- 60-74: Reasonable but under-evidenced.
- 40-59: Relies heavily on unsupported claims.
- 0-39: Hype, fake certainty, or unclear proof damages trust.

### Conversion Readiness

- 90-100: CTAs, objections, and section order strongly support action.
- 75-89: Good path, but a few CTAs or objections need tightening.
- 60-74: Action path exists but lacks urgency, specificity, or reassurance.
- 40-59: Weak or mismatched CTAs; reader is left with basic questions.
- 0-39: No credible conversion path.

### Distinctiveness

- 90-100: Memorable point of view and phrasing.
- 75-89: Some ownable language, but still a few category defaults.
- 60-74: Clear but easy to confuse with competitors.
- 40-59: Mostly generic.
- 0-39: Fully interchangeable.

## AI Sludge Risk

Score risk higher when the copy uses many formulaic phrases, vague benefits, inflated adjectives, symmetrical paragraph structures, overused transitions, unsupported claims, or excessive em dashes.

Risk bands:

- 0-20: Low. Human, specific, and grounded.
- 21-40: Mild. Some generic patterns but not dominant.
- 41-60: Moderate. Noticeable AI/corporate texture.
- 61-80: High. Generic polish is a major issue.
- 81-100: Severe. Reads primarily like generated marketing copy.

Apply AI Sludge Risk as a penalty after the weighted average:

- 0-20: no penalty
- 21-40: minus 4 points
- 41-60: minus 9 points
- 61-80: minus 16 points
- 81-100: minus 25 points

If AI Sludge Risk is 70 or higher, the final overall score cannot exceed 74.
If AI Sludge Risk is 85 or higher, the final overall score cannot exceed 59.
