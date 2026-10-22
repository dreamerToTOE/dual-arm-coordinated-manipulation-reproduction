# D082 saved-analysis01

Postprocessing of the saved 50-call D081 stability pilot. No planning, model, IK, collision, RBS, or rank calculation is performed. Original inputs remain unchanged.

Reproduce from repository root:

```bash
python3 results/20261022_D082_saved_analysis01/analyze_saved.py
```

`summary.json` records counts, scientific-call scope, historical timing limitations and analysis wall/CPU. `input_sha256.json` fixes inputs. Tables retain the actual denominators, censoring and tree-versus-solution partition semantics. The Chinese interpretation is `reports/P4_D082_ALGORITHM_FINDINGS_20261022.md`.

The prior 20-call pilot overlaps seeds 7/23 and must not be pooled as additional independent seeds. Snapshot checks and arithmetic postprocessing do not constitute independent numerical trajectory validation.
