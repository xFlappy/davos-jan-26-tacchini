# Challenge 3: Energy Market Signal Intelligence Agent

> **Status:** Draft
> **Sponsor:** Volue
> **Contact:** Eduardo Franco Lazzarotto, Karoline Skatteboe
> **Last Updated:** 2026-01-15

## Background

Energy market participants are flooded with time series signals – prices, consumption, weather forecasts, outage, capacity, and other operational signals – spread across regions and granular time steps. Important events (e.g., anomalies, sudden spikes, high volatility, structural breaks, or unusual spreads) are easy to miss and hard to explain quickly.

Analysis and insights review today requires manual charting and ad hoc scripts, slowing reaction time and making it difficult to communicate what changed and why.

## Challenge Goal

Build an AI agent that:

1. **Pulls selected power-market time series** from the Volue Insight API (e.g., day ahead/intraday prices and key fundamentals/forecasts).
2. **Detects and summarizes data features** such as anomalies, high volatility regimes, trend shifts, outliers, and typical statistics (mean, median, rolling averages).
3. **Finds correlations/lead–lag relations** across curves (e.g., linking a price spike to a fundamental driver).
4. **Generates a narrative** ("what happened, where, and likely why") that a non-expert can read, with natural language interaction (ask–answer) to drill down on time windows, regions, or drivers.
5. **Outputs a concise market brief** (text + optional small charts) suitable for a daily note.

Teams will receive direct access to the Volue Insight API; your solution should call the API, interpret the results, and produce a user-facing narrative layer.

## Data & Tools Provided

- **Volue Insight API access** for a curated set of curves (e.g., DA/ID prices and selected fundamentals/forecasts relevant for short-term movements). Final list will be shared at kickoff.
- **API Documentation:** https://api.volueinsight.com/api/static/swagger/index.html
- **API Access:** https://api.volueinsight.com/ (participant list needed for registration ahead of event)

## Technical Approach (Suggested, Not Prescriptive)

### Data Ingestion
- Use the Insight API endpoints to query selected price and fundamentals/forecast curves
- Handle pagination, time windows, and units consistently

### Signal Analysis
- **Anomaly detection:** z-score/robust MAD, STL residuals, isolation forest
- **Volatility & regime shifts:** rolling std, GARCH-lite proxies, change-point detection
- **Correlation/driver exploration:** Pearson/Spearman; rolling windows; simple Granger-style tests if time allows

### Narrative Layer
- Convert findings into plain English insights with an LLM (local or cloud) using a structured prompt and guardrails
- Enable chat Q&A over the computed features
- Optionally implement lightweight RAG by caching your own generated daily briefs for context over time

### UX
- Minimal but clear: a simple web UI or CLI that accepts a question ("What moved in DE tomorrow vs. yesterday?") and returns both a short answer and the evidence (numbers/mini-charts, links to data source, etc.)

## Deliverables

1. **Working agent** that fetches Insight data, computes features, and produces a narrative summary with interactive Q&A.

2. **A concise market brief** for a selected region/day that highlights:
   - Anomalies/outliers
   - Volatility changes
   - Top correlations (with caveats)
   - A short "what likely drove this" paragraph

3. **README** with setup steps, API calls used, rate/latency considerations, and assumptions.

## Judging Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Insight Quality | 40% | Are anomalies/volatility shifts correctly detected and explained? Are correlations sensible and caveated? |
| Narrative Usefulness | 20% | Clarity, accuracy, and composability of the story; good follow-up answers in chat. |
| Technical Robustness | 20% | Clean API integration, reproducible pipeline, basic error handling, and traceable outputs. |
| UX & Presentation | 20% | Simple, intuitive interface; clear visuals that support the text. |

## Constraints & Tips

- **Timebox:** Aim for a thin vertical slice first: one or two regions, a handful of curves, and a week of history – then generalize.
- **Metrics first, LLM second:** Compute your features numerically; feed only summaries/aggregates to the LLM to minimize hallucinations and token cost.
- **Show your work:** Include evidence with numbers and small charts; always state windows (e.g., "7-day rolling").
- **Caveats:** Correlation ≠ causation. Call out uncertainty explicitly.

## Nice to Have (Stretch Goals)

- Alerting heuristics that flag when today "looks unusual" vs. the last N days
- Explainable features: show which inputs contributed most to an anomaly score
- Multi-market views (e.g., linking power price moves to fundamentals or neighbouring areas' signals)

## Submission Requirements

- Repository with `hackmaster-dmi` as read-only collaborator
- `/result/` folder with outputs for example prompts (screenshots, JSON exports, or short screen recordings)
- README with setup instructions (how to run locally, how to demo)

Commits after the submission deadline will not be considered. The default branch must contain the final version.

## Visual Data Exploration

You can explore available data interactively using the Volue Insight application:

- https://app.volueinsight.com/

This UI allows you to search for and inspect curves before implementing your solution.

API endpoint reference:
- https://api.volueinsight.com/

---

## Recommended Scope

To keep the problem tractable:

- Focus on a **single region** (e.g. `CH`)
- Limit the time horizon (e.g. **1 year**)
- Start with a small number of related curves

Different energy sources use different weather models, so weather run naming will vary.

---

## Accessing Data Programmatically

### Python (Recommended)

Use the official Volue Insight Python package:

- Quickstart guide:  
  https://wattsight-wapi-python.readthedocs-hosted.com/en/master/quickstart.html

Most commonly used datatype for this challenge:
- `actual`

Other datatypes are also available.

### REST API (Alternative)

- REST API documentation:  
  https://volueinsight.com/docs/api/api-endpoints.html
- Swagger UI:  
  https://api.volueinsight.com/api/static/swagger/index.html

### Authentication

To extract data, credentials must be established:

- https://volueinsight.com/docs/authentication.html

### Source Code

- Python client source:  
  https://github.com/volueinsight/wapi-python

---

## Available Data

You have access to **historical data starting from 2026-01-01**.

You have access to more curves than listed below. You are encouraged to explore the dataset before starting development.

### Areas
Examples include:
- `np`
- `no`
- `ch`
- `dk`
- `nl`
- `at`
- and others

### Weather Runs
Examples include:
- `EC00`
- `EC01`
- `EC02`
- `EC03`
- `gfs12ens`
- `icon00`
- `ml`

---

## Sample Curves

| Category | Curve Name | Description |
|--------|-----------|-------------|
| CO₂ Price | `co2 pri ets eua 01 €/eua cet m f` | European CO₂ allowance price |
| Gas Price | `gas pri nl ttf intraday fut ice €/mwh cet m ca` | TTF gas spot price |
| Spot Price (Hourly) | `pri (area) (weather run) spot €/mwh cet h a` | Day-ahead price |
| Intraday Price | `pri (area) (weather run) intraday €/mwh cet h a` | Same-day trading price |
| Spot Price (15 min) | `pri (area) (weather run) spot €/mwh cet min15 a` | 15-minute resolution spot price |
| Intraday Price (15 min) | `pri (area) (weather run) intraday €/mwh cet min15 a` | 15-minute intraday price |
| Consumption Forecast | `con (area) (weather run) mwh/h cet min15 f` | Forecasted consumption |
| Residual Load Forecast | `rdl (area) (weather run) mwh/h cet min15 f` | Consumption minus wind and solar |
| SPV Forecast | `pro (area) spv (weather run) mwh/h cet min15 f` | Solar production forecast |
| Wind Forecast | `pro (area) wnd (weather run) mwh/h cet min15 f` | Wind production forecast |
| Observed Consumption | `con (area) (weather run) mwh/h cet min15 a` | Actual TSO data |
| Actual Residual Load | `rdl (area) (weather run) mwh/h cet min15 sa` | Observed residual load |
| Actual SPV Production | `pro (area) spv (weather run) mwh/h cet min15 a` | Observed solar production |
| Actual Wind Production | `pro (area) wnd (weather run) mwh/h cet min15 a` | Observed wind production |
| SPV Normals | `pro (area) spv mwh/h cet min15 n` | 30-year smoothed average |
| Wind Normals | `pro (area) wnd mwh/h cet min15 n` | 30-year smoothed average |
| Installed PV Capacity | `cap (area) spv mw cet min15 a` | Installed and forecasted PV capacity |
| Nuclear Production | `pro (area) nuc mwh/h cet min15 a` | Observed nuclear production |
| Temperature | `tt (country) (town) test °c cet h s` | Backcast temperature |

---
