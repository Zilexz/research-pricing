# Synthetic Quote-Context Sandbox

This folder contains **fully synthetic** ride-hailing quote data generated for
the internship forecasting and calibrated-uncertainty study.

It contains no event-level production rows, real customer identifiers,
source-event timestamps, or production quote IDs. With aggregate BigQuery
calibration, newly sampled rows inherit only privacy-thresholded
hex/service/hour quote distributions and hex/hour weather distributions.
Operator-provided H3 identifiers, display names, and aggregate pickup centroids
remain visible metadata; remap them before intern release if those identifiers
are restricted.

## Main tables

- `synthetic_competitor_quote_feed_v1`: sanitized irregular observation feed
  used to audit and reproduce the delayed-observation construction.
- `synthetic_intern_forecasting_v1`: primary leakage-safe internship table,
  with one row per target quote and requested lag.
- `synthetic_zones_v1`, `synthetic_split_manifest_v1`, and
  `synthetic_scenario_catalog_v1`: location metadata, frozen evaluation
  assignments, and the normal primary-benchmark regime.
- `synthetic_stress_competitor_quote_feed_v1` and
  `synthetic_stress_forecasting_v1`: optional controlled out-of-distribution
  checks. These rows use `split=stress_test` and never enter the primary
  train/validation/calibration/test benchmark.
- `synthetic_stress_scenario_catalog_v1`: timing and definitions for the
  separate rain-shock, supply-shortage, and demand-spike windows.

The following tables appear only with `--artifact-profile full`:

- `synthetic_market_context_5m_v1`: five-minute weather, synthetic demand,
  synthetic supply, imbalance, and market multiplier context.
- `synthetic_customer_profiles_v1`: synthetic customer profile snapshots.
- `synthetic_quotes_v1`: quote identity, route, fare, multiplier, discount, and
  shown-price fields.
- `synthetic_quote_context_v1`: quote rows joined to market, weather, and
  customer context for internal MoE compatibility. **Do not use this as the
  intern modeling table.**
- `synthetic_data_dictionary_v1`: field definitions and target-time
  availability rules.
- `synthetic_information_availability_v1`: concise leakage boundary.

All tabular data is written as gzip-compressed CSV parts. `manifest.json` uses
paths relative to this directory, matching the Vertex artifact pattern used by
the MoE study.

## Folder layout

- `hexes/<hex-id>/` contains that pickup hex's enabled tables plus its own
  `manifest.json`.
- `shared/` contains scenario definitions, the data dictionary, and
  target-time information-availability rules. Full profile also includes
  synthetic customer profiles.
- `hex_index.json` maps each requested hex ID to its folder.
- With full profile, loading `synthetic_quote_context_v1` from the root
  `manifest.json` concatenates all hex partitions using the existing MoE
  manifest loader.
- Loading `synthetic_intern_forecasting_v1` gives the frozen intern dataset;
  a per-hex manifest loads only that pickup partition.

## Split and stress-test policy

The primary benchmark contains only `scenario_id=normal`. With the default
`split_mode=monthly_calendar_days`, every calendar month is an independent
forecasting fold identified by `evaluation_month`. The first 20 observed UTC
dates in that month are training dates. Remaining dates are divided as evenly
as possible among validation, conformal calibration, and final test, always in
that chronological order. No date is shared by two splits.

Models, hyperparameters, conformal residuals, and test results must remain
inside one `evaluation_month`. Do not train one pooled model on later months and
use it to score an earlier monthly test block. Aggregate metrics may be computed
only after each monthly fold has produced its own untouched test predictions.
Competitor-price histories and lagged market features reset at each monthly
boundary, so a new month's rows cannot inherit the previous month's test data.

Stress scenarios are generated after the primary time range in separate tables.
They are robustness checks, not part of nominal interval calibration or final
coverage reporting. `scenario_id`, `split`, identifiers, and all `target_*`
labels are evaluation-only and must not be model inputs.

## Forecasting target

The primary intern label is `target_shown_price`. `target_price_per_km` is the
normalized label and `target_shown_multiplier` is an optional auxiliary label.

Use `latest_observed_price` as the persistence baseline. The
`actual_observation_age_minutes` may exceed `requested_lag_minutes` because
competitor observations are irregular.

Do not add current base/non-surge fare, discounts, price totals, multipliers,
customer/CDP fields, or contemporaneous demand/supply to the intern table.
Those fields exist only in compatibility and audit tables.

## Interpretation

- Public-data results provide empirical evidence for the Boston source data.
- This sandbox demonstrates pipeline compatibility and controlled stress tests.
- Synthetic results are consequences of the simulator assumptions.
- Aggregate calibration improves structural realism but does not turn
  synthetic results into empirical evidence about production outcomes.
- Do not make causal, production-performance, or customer-behaviour claims.
- Synthetic booking/completion outcomes are intentionally not generated.

## Safe generation summary

```json
{
  "artifact_version": "2.1",
  "artifact_profile": "intern",
  "seed": 42,
  "synthetic_start_utc": "2026-01-01T00:00:00+00:00",
  "synthetic_end_utc_inclusive": "2026-03-30T23:55:00+00:00",
  "frequency": "5min",
  "duration_days": 89.0,
  "inclusive_start_date": "2026-01-01",
  "inclusive_end_date": "2026-03-30",
  "n_zones": 3,
  "hex_ids": [
    "8765b574affffff",
    "8765b574bffffff",
    "8765b5759ffffff"
  ],
  "hex_display_names": {
    "8765b574affffff": "Crescent Mall",
    "8765b574bffffff": "SC Vivo City",
    "8765b5759ffffff": "EcoGreen S\u00e0i G\u00f2n"
  },
  "hex_ids_supplied_by_operator": true,
  "hex_partitioned_storage": true,
  "n_customers": 20000,
  "services": [
    {
      "service_id": "SYN_STANDARD",
      "service_name": "Synthetic Standard Car"
    },
    {
      "service_id": "SYN_PREMIUM",
      "service_name": "Synthetic Premium Car"
    }
  ],
  "currency_code": "VND",
  "competitor_name": "Synthetic Competitor",
  "personalized_wrapper_enabled": false,
  "calibration_source": "aggregate_bigquery_internal",
  "calibration_is_per_hex_service_hour": true,
  "privacy_threshold_min_group_rows": 50,
  "aggregate_group_count_used_in_memory": 504,
  "weather_aggregate_group_count_used_in_memory": 357,
  "aggregate_calibration_parameters_exported": false,
  "intern_forecasting_table": "synthetic_intern_forecasting_v1",
  "primary_benchmark_scenario_policy": "normal_only",
  "stress_test_generated_separately": true,
  "stress_forecasting_table": "synthetic_stress_forecasting_v1",
  "requested_lags_minutes": [
    5,
    10,
    15,
    30
  ],
  "history_window_minutes": 60,
  "weather_observation_minutes": 60,
  "weather_observation_failure_rate": 0.05,
  "split_mode": "monthly_calendar_days",
  "monthly_train_days": 20,
  "split_day_counts": {
    "2026-01": {
      "train": 20,
      "validation": 4,
      "calibration": 3,
      "test": 4
    },
    "2026-02": {
      "train": 20,
      "validation": 3,
      "calibration": 2,
      "test": 3
    },
    "2026-03": {
      "train": 20,
      "validation": 3,
      "calibration": 3,
      "test": 4
    }
  },
  "split_boundaries": {
    "2026-01": {
      "train": {
        "days": 20,
        "start_date_utc": "2026-01-01",
        "end_date_utc_inclusive": "2026-01-20",
        "start_utc": "2026-01-01T00:00:00+00:00",
        "end_utc_inclusive": "2026-01-20T23:55:00+00:00"
      },
      "validation": {
        "days": 4,
        "start_date_utc": "2026-01-21",
        "end_date_utc_inclusive": "2026-01-24",
        "start_utc": "2026-01-21T00:00:00+00:00",
        "end_utc_inclusive": "2026-01-24T23:55:00+00:00"
      },
      "calibration": {
        "days": 3,
        "start_date_utc": "2026-01-25",
        "end_date_utc_inclusive": "2026-01-27",
        "start_utc": "2026-01-25T00:00:00+00:00",
        "end_utc_inclusive": "2026-01-27T23:55:00+00:00"
      },
      "test": {
        "days": 4,
        "start_date_utc": "2026-01-28",
        "end_date_utc_inclusive": "2026-01-31",
        "start_utc": "2026-01-28T00:00:00+00:00",
        "end_utc_inclusive": "2026-01-31T23:55:00+00:00"
      }
    },
    "2026-02": {
      "train": {
        "days": 20,
        "start_date_utc": "2026-02-01",
        "end_date_utc_inclusive": "2026-02-20",
        "start_utc": "2026-02-01T00:00:00+00:00",
        "end_utc_inclusive": "2026-02-20T23:55:00+00:00"
      },
      "validation": {
        "days": 3,
        "start_date_utc": "2026-02-21",
        "end_date_utc_inclusive": "2026-02-23",
        "start_utc": "2026-02-21T00:00:00+00:00",
        "end_utc_inclusive": "2026-02-23T23:55:00+00:00"
      },
      "calibration": {
        "days": 2,
        "start_date_utc": "2026-02-24",
        "end_date_utc_inclusive": "2026-02-25",
        "start_utc": "2026-02-24T00:00:00+00:00",
        "end_utc_inclusive": "2026-02-25T23:55:00+00:00"
      },
      "test": {
        "days": 3,
        "start_date_utc": "2026-02-26",
        "end_date_utc_inclusive": "2026-02-28",
        "start_utc": "2026-02-26T00:00:00+00:00",
        "end_utc_inclusive": "2026-02-28T23:55:00+00:00"
      }
    },
    "2026-03": {
      "train": {
        "days": 20,
        "start_date_utc": "2026-03-01",
        "end_date_utc_inclusive": "2026-03-20",
        "start_utc": "2026-03-01T00:00:00+00:00",
        "end_utc_inclusive": "2026-03-20T23:55:00+00:00"
      },
      "validation": {
        "days": 3,
        "start_date_utc": "2026-03-21",
        "end_date_utc_inclusive": "2026-03-23",
        "start_utc": "2026-03-21T00:00:00+00:00",
        "end_utc_inclusive": "2026-03-23T23:55:00+00:00"
      },
      "calibration": {
        "days": 3,
        "start_date_utc": "2026-03-24",
        "end_date_utc_inclusive": "2026-03-26",
        "start_utc": "2026-03-24T00:00:00+00:00",
        "end_utc_inclusive": "2026-03-26T23:55:00+00:00"
      },
      "test": {
        "days": 4,
        "start_date_utc": "2026-03-27",
        "end_date_utc_inclusive": "2026-03-30",
        "start_utc": "2026-03-27T00:00:00+00:00",
        "end_utc_inclusive": "2026-03-30T23:55:00+00:00"
      }
    }
  },
  "booking_or_completion_outcomes_generated": false,
  "event_level_production_rows_used_in_release": false
}
```

Quality status: `passed`.
Generated folder: `synthetic_quote_context_sandbox_20260727_024458_utc`.
