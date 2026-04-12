# Validation Snapshot

The aerodynamic estimate in Manta Airlab is a quick engineering check. It is not CFD and not a full XFOIL replacement.

To keep this claim grounded, the repository includes a benchmark suite based on UIUC, NASA, and NLR/OSU reference data.

## Current summary

On the best-supported cases:

- mean `Cl` differences are around `0.3%` to `5%`
- mean `Cd` differences are around `6%` to `9%`

Harder low-Reynolds cases can still reach about `20%` mean `Cl` difference, so this estimate should be used as directional support for first-pass sizing, not final validation.

## Benchmark assets

- Script: `benchmarks/compare_cli_vs_reference.py`
- Cases: `benchmarks/cases/*.json`
- Reference data: `benchmarks/data/*.csv`
- Reports: `benchmarks/results/*_report.md`
- Summary chart: `benchmarks/results/benchmark_summary.png`

![benchmark summary](benchmarks/results/benchmark_summary.png)

## Positioning

Manta Airlab helps users reach a better first approximation faster:

- rapid geometry iteration
- immediate quick-aero feedback
- direct export for downstream work

It does not replace CFD, wind-tunnel testing, or physical validation.

## Source notices

Benchmark-source notices and required attributions are in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

