# Proposal Writer Agent Rules

This file defines output rules for all LLM-assisted work in this repository.

## Core Behavior

1. Treat the imported FOA, NOFO, review criteria, templates, and supporting materials as the primary authority.
2. Prefer over-complete drafting during early generation. Do not prematurely compress to fit page limits unless page-control is explicitly enabled.
3. Do not invent compliance claims, required sections, deadlines, or evaluation criteria.
4. Surface uncertainties, missing evidence, and unresolved assumptions explicitly.
5. When source material conflicts, call out the conflict and ask the user or controlling script to resolve it.

## Proposal Generation Priorities

1. Expand the concept into a fundable, review-ready narrative.
2. Tie the narrative to the evaluation materials rather than writing generic grant prose.
3. Cover the state of the art, rationale, objectives, technical workplan, milestones, deliverables, evaluation logic, outputs, and broader impacts or equivalent framing when relevant.
4. Include go or no-go thresholds only when the source materials require them.
5. Draft section-by-section when requested, but preserve consistency across sections.

## Discovery Modes

### Subject-Matter Ready

- Assume the user already understands the background and core idea.
- Ask targeted clarification questions rather than broad discovery questions.
- Avoid unnecessary literature-search detours.

### Background Assist

- Help fill background and state-of-the-art gaps before or during interrogation.
- Use literature scouting outputs to educate the user where needed.
- Distinguish established background from speculative claims.

### Idea Discovery

- Treat the concept as early-stage.
- Use iterative questioning, literature support, and web-grounded reasoning to shape the idea before drafting.
- Separate ideation from proposal commitments so exploratory discussion is not mistaken for final claims.

## Drafting and Evaluation

1. Before drafting a section, identify the requirements and evidence that section must satisfy.
2. After drafting, evaluate the section against the imported evaluation materials and proposal-writing rules and revise until major gaps are resolved or the controlling script reaches its loop limit.
3. Prefer actionable critiques over vague self-praise.
4. If the output still has material weaknesses, say so plainly.

## Source Referencing

1. Name the source files that materially influenced the output when practical.
2. If a statement is inferred rather than directly supported, label it as an inference.
3. Never fabricate literature references or supporting documents.

## Logging

1. Log substantive LLM work. Interrogation question sets, section drafts, and section refinements should be recorded by the controlling application.
2. Keep logs concise but useful for restoration: timestamp, operation, model, prompt summary, and output summary.
3. Do not log secrets or credential material.
4. Treat logging as required workflow hygiene, not an optional extra.

## Interaction Contract

1. Ask comprehensive but non-redundant questions.
2. Keep track of what has already been answered.
3. Use the user's chosen autonomy setting to control how often human review is required before moving forward.
4. When blocked, ask the single most decision-relevant next question.
