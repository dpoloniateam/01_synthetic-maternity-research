# Appendix A: AI Governance and Disclosure

This appendix documents the AI models, costs, and governance measures
employed throughout the synthetic maternity research pipeline.

## Pipeline Summary

- **Total pipeline iterations:** 2
- **Total sessions run:** 355
- **Total personas used:** 150
- **Total cost (USD):** $0.6371
- **Saturation reached:** False
- **Robustness verdict:** Robust across vulnerable populations

## Models Used

| Task | Model / Strategy |
|------|-----------------|
| quality_scoring | google/gemini-3-flash-preview |
| interviewer | openai/gpt-5-mini-2025-08-07 |
| persona_roleplay | multi-provider rotation |

## Model Providers and Tiers

The pipeline employs a three-provider, three-tier architecture:

| Provider | INTENSO (high quality) | MODERADO (balanced) | BAIXO (cost-efficient) |
|----------|----------------------|---------------------|----------------------|
| anthropic | claude-opus-4-6 | claude-sonnet-4-6 | claude-haiku-4-5 |
| openai | gpt-5.4-pro-2026-03-05 | gpt-5.4-2026-03-05 | gpt-5-mini-2025-08-07 |
| google | gemini-3.1-pro-preview | gemini-3-flash-preview | gemini-3.1-flash-lite-preview |

## Refinement Impact

- **Richness improvement:** 36.9%
- **Surfacing rate improvement:** 22.5%
- **Blind spots resolved:** 5
- **Blind spots remaining:** 2

## Governance Measures

- All prompts archived
- Audit trail for every modification
- Multi-provider inter-rater validation
- Adversarial robustness testing
- Synthetic-only data (no real patients)
- Cost tracking per call
- Timestamped outputs — no data overwritten
