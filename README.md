# Snowflake Data Profiler

A Streamlit application that generates detailed statistical profiles of Snowflake tables and views, with PDF export.

## Features

- **Connect to Snowflake** — enter credentials and browse databases, schemas, tables/views
- **Comprehensive profiling** — per-column statistics including nulls, distinct counts, distributions, percentiles, and more
- **Type-aware analysis** — numeric stats (min/max/mean/median/stddev/percentiles), string stats (lengths, empty strings), date stats (range), boolean stats (true/false split)
- **Data quality scoring** — overall quality score with completeness and uniqueness metrics
- **Interactive visualizations** — histograms, donut charts, scatter plots, and bar charts via Plotly
- **PDF export** — professional dark-themed PDF report with cover page, overview table, quality section, and per-column detail pages
- **Sampling** — optional row sampling for faster profiling on large tables
- **Warnings** — automatic detection of data quality issues (high nulls, zero variance, single values, etc.)

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Requirements

- Python 3.9+
- A Snowflake account with appropriate permissions

## Project Structure

```
app.py            # Main Streamlit application
profiler.py       # Snowflake profiling engine
pdf_export.py     # PDF report generator (fpdf2)
styles.py         # Custom CSS styles
.streamlit/       # Streamlit theme configuration
```
