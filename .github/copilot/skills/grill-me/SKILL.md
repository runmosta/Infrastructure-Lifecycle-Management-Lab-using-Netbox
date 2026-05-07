---
name: grill-me
description: Interview me relentlessly about the design choices and check out every branch of the design topic. Use the code implemented as information. Every choice made should be explained and documented in CONTEXT.md. Document and explain why we made the choice.
applyTo: "**"
---

# Grill Me Skill

## Purpose
Relentlessly interview the user about design choices using the existing codebase as context. Document every decision and its rationale in `CONTEXT.md`.

## Workflow
1. **Explore** the codebase first — read existing code, configs, docs
2. **Identify** all design decisions made (explicit and implicit)
3. **Challenge** every choice with pointed questions across multiple rounds
4. **Document** each resolved decision in `CONTEXT.md` with:
   - What was chosen
   - What alternatives were considered
   - Why this choice was made
   - What risks or trade-offs exist

## Rules
- Never accept vague answers — push for specifics
- Always explore at least 3 branches of each design topic
- Cross-reference answers against the actual code
- Update `CONTEXT.md` after each resolved question
- Group questions in rounds: Scope → Architecture → Implementation → Operations
