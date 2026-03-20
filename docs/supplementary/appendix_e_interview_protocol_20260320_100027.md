# Appendix E: Interview Protocol

## Multi-Provider Rotation Approach

The synthetic interview pipeline uses a multi-provider rotation strategy
to ensure response diversity and reduce single-model bias:

1. **Interviewer agent:** A single model conducts all interviews for consistency
   in question delivery and follow-up probing.

2. **Persona agent (rotating):** The persona role-play responses rotate across
   three providers (Anthropic, Google, OpenAI) to introduce stylistic and
   reasoning diversity. Each provider brings different strengths:
   - Anthropic models tend toward nuanced emotional expression
   - Google models often provide structured, detail-rich responses
   - OpenAI models balance narrative flow with analytical depth

3. **BIBD assignment:** Sessions are assigned to versions and personas using a
   Balanced Incomplete Block Design (BIBD) to ensure each persona encounters
   exactly two versions, enabling within-subject comparison.

## Interview Structure

Each interview session follows this protocol:

1. The interviewer agent presents questions from the assigned questionnaire version
2. Questions are adapted to the persona's EHR profile (personalised probes)
3. The persona agent responds in-character based on their enriched narrative
4. The interviewer follows up with probes when responses lack depth
5. A transcript is built with metadata (model, tokens, timing) for each turn

## Session Runner Configuration

The session runner is implemented in `src/orchestration/session_runner.py` and supports:

- Parallel session execution with configurable thread count
- Resume support (skips already-completed sessions)
- Per-environment cost ceilings (dev: $20, test: $50, prod: $100)
- Automatic cost tracking across all LLM calls

## Example Interviewer System Prompt

The interviewer agent uses a system prompt structured as follows:

```
You are a skilled qualitative researcher conducting a semi-structured
interview about maternity care experiences. Your role is to:
- Ask questions naturally, following the questionnaire structure
- Use probes when responses lack depth or specificity
- Maintain a warm, empathetic tone throughout
- Adapt follow-up questions to the participant's specific context
- Ensure all journey phases and latent dimensions are explored
```

## Example Persona System Prompt

Each persona agent receives a system prompt incorporating:

```
You are [Name], a [age]-year-old [type] in [location].
[Enriched narrative providing backstory, emotional state,
 clinical context, and vulnerability factors.]

Respond as this person would in a real interview:
- Stay in character throughout
- Draw on your specific experiences and emotions
- Be authentic — include hesitations, contradictions, and unspoken fears
- Reference your medical history where relevant
```
