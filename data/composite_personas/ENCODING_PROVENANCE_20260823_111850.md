# Canonical-dimension encoding — heuristic — 23 August 2026, 11:18

Input `data/composite_personas/composites.jsonl` (150 personas, sha256 97544f851667e118…) → `data/composite_personas/composites_v2.jsonl`.

| Dimension | Source counts | Mean salience |
|---|---|---|
| power_dynamics | {'encoded': 150} | 0.15 |
| identity_tensions | {'encoded': 150} | 0.09 |
| structural_barriers | {'encoded': 150} | 0.21 |
| dignity_respect | {'heuristic': 150} | 0.32 |
| continuity_of_care | {'heuristic': 150} | 0.31 |
| trust_distrust | {'alias': 150} | 0.25 |
| autonomy_vs_dependence | {'encoded': 150} | 0.1 |
| informal_care_networks | {'encoded': 150} | 0.07 |
| digital_information_seeking | {'heuristic': 150} | 0.41 |
| partner_role | {'heuristic': 150} | 0.47 |
| body_image_autonomy | {'heuristic': 150} | 0.42 |
| intergenerational_patterns | {'heuristic': 150} | 0.28 |

Heuristic rules: baseline 0.2; vulnerability-flag weights and narrative keyword hits (0.08 each, max five) per dimension as in `FLAG_WEIGHTS` and `KEYWORDS`; marital status and age for partner_role / digital_information_seeking / intergenerational_patterns. The narratives are unchanged: these values are the judge's reference for what each persona *could* surface, not new persona content. Decision point for the authors: accept the heuristic reference, run the LLM mode, or re-derive the pool.
