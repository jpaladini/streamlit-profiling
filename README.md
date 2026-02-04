# Snowflake Data Profiler

A **Streamlit in Snowflake (SiS)** application that generates detailed statistical profiles of tables and views, with PDF export.

Uses `snowflake.snowpark.context.get_active_session()` — no credentials or connection setup needed.

## Features

- **Browse Snowflake objects** — databases, schemas, tables, and views via the sidebar
- **Comprehensive profiling** — per-column statistics including nulls, distinct counts, distributions, percentiles, and more
- **Type-aware analysis** — numeric stats (min/max/mean/median/stddev/percentiles/histogram), string stats (lengths, empty strings), date stats (range), boolean stats (true/false split)
- **Data quality scoring** — overall quality score with completeness and uniqueness metrics
- **Interactive visualizations** — histograms, donut charts, scatter plots, and bar charts via Plotly
- **PDF export** — professional dark-themed PDF report with cover page, overview table, quality section, and per-column detail pages
- **Sampling** — optional row sampling for faster profiling on large tables
- **Warnings** — automatic detection of data quality issues (high nulls, zero variance, single values, etc.)

## Deploying to Streamlit in Snowflake

1. In Snowsight, go to **Streamlit** and create a new app
2. Upload all `.py` files (`app.py`, `profiler.py`, `pdf_export.py`, `styles.py`)
3. Add the required packages in the app settings: `plotly`, `fpdf2`
4. Set `app.py` as the main file

The app automatically uses the active Snowpark session — no connection configuration required.

## Dependencies

Only two external packages (beyond what SiS provides):

- `plotly` — interactive charts
- `fpdf2` — PDF report generation

Both are available in the Snowflake Anaconda channel.

## Project Structure

```
app.py              # Main Streamlit application (SiS entry point)
profiler.py         # Snowflake profiling engine (Snowpark Session)
pdf_export.py       # PDF report generator (fpdf2)
styles.py           # Custom CSS styles
environment.yml     # SiS package dependencies
.streamlit/         # Streamlit theme configuration
```
