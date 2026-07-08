# Quandora

Quandora is the all-in-one plugin package in the Quandora plugin marketplace. Factor Mining is the first bundled skill.

## What Factor Mining Does

Quandora Factor Mining helps an agent:

1. Connect to the user's Quandora account through the host's MCP authorization flow.
2. List public factor-mining tasks or create a custom factor session.
3. Generate a valid `plugin.py` in the local workspace when file writes are available.
4. Submit the factor source inline to Quandora.
5. Wait for the backtest, retrieve available factor cards and chart artifacts, and summarize the result.
6. Save the local working files and returned results together.

## Result Files

When the host supports local files, Factor Mining archives each run under:

```text
Quandora result/factor-mining/aggressive_flow_exhaustion_reversal/
```

The archive is named from the factor slug, preferably the generated `FACTOR_TYPE`. It contains the submitted `plugin.py`, a redacted `run_summary.json`, `factor_card_is.json` and `factor_card_all.json` when available, `artifact_manifest.json`, PNG charts under `artifacts/is/` and `artifacts/all/`, and the raw signal parquet at `signal_raw.parquet` when available. PNG API calls use the returned server `source_name`; local files are saved to `standard_local_path`. The agent prints the result, artifact, and chart folder paths after each run so the user can open the files directly.

## Skills

```text
skills/
  factor-mining/
```
