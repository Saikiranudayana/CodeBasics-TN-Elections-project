# TN Election Dashboard 2026

A professional multi-page Streamlit dashboard for the 2026 Tamil Nadu Legislative Assembly Election.

## Features

- **Layer 1** — Data Pipeline: automated data cleaning & preprocessing
- **Layer 2** — Core Dashboard: 7-page Streamlit app with rich Plotly charts
- **Layer 3** — AI Intelligence Agent: LangGraph + Tavily for live news & video

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Copy the example env file and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env`:
   ```
   TAVILY_API_KEY=tvly-your-actual-key
   ANTHROPIC_API_KEY=sk-ant-your-actual-key
   ```

## Data Pipeline

Run once before launching the app (or whenever raw data is updated):

```bash
python pipeline/run_pipeline.py
```

This reads raw CSVs from `data/raw/` and writes processed parquet files to `data/processed/`.

## Launch

```bash
streamlit run app.py
```

## Data Sources

- **Election Commission of India** — Official constituency-level results
- Raw files: `tn_2021_results.csv`, `tn_2026_results.csv`, `constituency_master.csv`
- 234 total constituencies (188 GEN, 44 SC, 2 ST)

## Pages

| Page | Description |
|------|-------------|
| 🏠 Overview | Top-level results, KPIs, drastic change alerts |
| 🗺️ Geographic Story | Regional seat distribution and drill-down |
| 🔄 Flip Story | Constituency flips, Sankey diagram |
| 📊 Vote Share Story | Party vote share shifts, TVK analysis |
| 📏 Margin Story | Margin of victory analysis |
| ⚖️ Reserved Seats | SC/ST/GEN constituency breakdown |
| 🤖 AI News Agent | LangGraph agent for live news and Q&A |

## Notes

- 2026 turnout is displayed as 85.1% (state average); per-constituency data is unavailable.
- TVK is a new party that did not exist in 2021.
- The AI News Agent requires valid TAVILY_API_KEY and ANTHROPIC_API_KEY in `.env`.
