# Greencoat UK Wind (UKW) Stock Pitch

This repository hosts an 18-page investment pitch for **Greencoat UK Wind PLC (UKW)**, alongside the assets and helper scripts used to visualise the financials.

## Contents

- `Greencoat_UKW_StockPitch.pdf` – the full report in PDF format.
- `index.html` – a web-ready version of the report for publishing on GitHub Pages (or any static host).
- `assets/` – supporting figures and data exports, including PNG charts and HTML/CSV files for the interactive Sankey views.
- `sankey_chart_*.py`, `future_revenue_projection_chart.py` – Python helpers used to generate the cash flow and balance sheet Sankey diagrams and other charts.

## Reading the Pitch

- **PDF:** open `Greencoat_UKW_StockPitch.pdf` directly.
- **Website:** the same content is available as a single-page site rendered from `index.html`. Once published, it can be accessed at: `<insert website link here>`.

## Regenerating the Sankey Charts

The Sankey inputs live in the `assets/` directory and are generated via the Python scripts in the project root. To update or regenerate a chart:

```bash
python sankey_chart_cf.py      # cash-flow Sankey
python sankey_chart_bs.py      # balance-sheet Sankey
python future_revenue_projection_chart.py  # revenue vs market cap chart
```

Each script writes its output back into `assets/`, where the HTML page and PDF expect to find the figures.

---
