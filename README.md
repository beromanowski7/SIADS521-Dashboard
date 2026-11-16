# SIADS 521: Four Views of the U.S. Economy

An interactive dashboard for the University of Michigan **SIADS 521: Visual Exploration** course, exploring how inflation, unemployment, and real GDP growth differed across U.S. decades from **1959 Q1 through 2009 Q3**.

The dashboard combines four linked Plotly visualizations, shared year filters, and a decade comparison panel in a self-contained HTML file. Users can explore historical economic conditions in a browser without installing Python or connecting to the internet.

## Video Walkthrough

Link: https://beromanowski7.github.io/SIADS521-Dashboard/Dashboard_Walkthrough.mp4

The walkthrough demonstrates the linked filtering controls, explores differences between the 1970s and 1990s, and highlights the Compare Decades feature.

The recording is hosted directly through GitHub Pages and is accessible without authentication.

## Visualizations and linked filtering

| Visualization | Purpose |
| --- | --- |
| Line chart | Compare inflation and unemployment over time on a shared percentage scale. |
| Scatterplot | Explore inflation versus unemployment, with color indicating quarter-over-quarter real GDP growth and guides at the 6% thresholds. |
| Histogram | Examine the inflation distribution using fixed 2-percentage-point bins. |
| Sunburst | Explore the nested breakdown of quarters by high/low inflation and unemployment, using a 6% cutoff for each indicator. |

A **decade preset** and a **dual-handle year-range slider** update all four charts and the summary counters together. Moving either handle selects a custom range. GDP growth uses a consistent color scale across selections so colors remain comparable.

## Compare Decades

The collapsible **Compare Decades** panel defaults to the **1970s (Period A)** and **1990s (Period B)**. Its dropdowns use the full underlying dataset independently of the main chart filters.

Three compact cards show each period's average inflation, average unemployment, and percentage of quarters with both indicators at least 6%. Deltas are calculated as **Period B − Period A in percentage points**, using unrounded values. Colors and signs indicate direction without assigning a positive or negative judgment.

A dynamic **“What changed between these decades?”** summary explains the changes in plain language and identifies partial coverage. Available comparison decades have at least 36 of 40 quarters: the 1960s through the 1990s are complete, and the 2000s contain 39 quarters through 2009 Q3. The four quarters from 1959 are excluded from the comparison dropdowns.

## Key exploration findings

Filtering by decade reveals a difference in the frequency of simultaneously elevated inflation and unemployment:

| Measure | 1970s | 1990s | Change: 1990s − 1970s |
| --- | --- | --- | --- |
| Average inflation | 7.22% | 2.83% | −4.38 percentage points |
| Average unemployment | 6.22% | 5.76% | −0.45 percentage points |
| Quarters with both indicators ≥6% | 11/40 (27.50%) | 0/40 (0.00%) | −27.50 percentage points |

Changes are calculated before rounding, so subtracting the displayed averages may produce slightly different results. Linked filtering isolates each decade across the four views, making this difference easier to explore than in the full 203-quarter view.

These findings are descriptive. The 6% threshold is an exploratory assumption, and the data describe historical conditions rather than current economic activity or causal relationships.

## Repository contents

| File | Purpose |
| --- | --- |
| [index.html](index.html) | Self-contained interactive dashboard and GitHub Pages entry file. |
| [Narrative_Notebook.ipynb](Narrative_Notebook.ipynb) | Library rationale, data preparation, chart construction, exploration, AI disclosure, and deployment documentation. |
| [build_dashboard.py](build_dashboard.py) | Data preparation and HTML/CSV generation. |
| [macrodata_clean.csv](macrodata_clean.csv) | Cleaned data and derived fields for inspection and reproducibility. |
| [requirements.txt](requirements.txt) | Minimum Python package requirements for rebuilding. |

## Technology stack

- **Python, pandas, and statsmodels** for loading, cleaning, and summarizing quarterly data.
- **Plotly.py and Plotly.js** for notebook figures and interactive browser charts.
- **HTML, CSS, and JavaScript** for the standalone layout, shared filters, and comparison panel.
- **Jupyter Notebook** for the narrative and reproducible analysis.
- **GitHub Pages** as a static hosting option for `index.html`.

Recorded local environment on November 15, 2026: Python 3.13.1, pandas 3.1.1, plotly 7.1.0, statsmodels 0.15.0, nbformat 5.11.1, and notebook 7.6.5. `requirements.txt` specifies minimum versions rather than a locked environment; pandas 2.2 or later is required for `PeriodIndex.from_fields`.

## Run locally

Download the repository and open **`index.html`** in a web browser. Only that file is needed to use the dashboard: Plotly.js and the chart data are embedded, and no Python process, server, or internet connection is required.

To rebuild from the repository root:

```bash
python -m pip install -r requirements.txt
python build_dashboard.py
```

The build script writes `macrodata_clean.csv` and refreshes `index.html` directly.

To run the narrative notebook:

```bash
jupyter notebook Narrative_Notebook.ipynb
```

Run its cells in order with `build_dashboard.py` in the same directory. The notebook's export calls the same builder and refreshes `index.html` directly. Both build paths export dates as `YYYY-MM-DD`. The first quarter has no prior GDP observation, so its derived growth is missing and that quarter is omitted only from the GDP-colored scatterplot.

## Deploy with GitHub Pages

Live Dashboard: https://beromanowski7.github.io/SIADS521-Dashboard/

This project is currently hosted using GitHub Pages. The following steps explain how to reproduce the deployment:

1. Commit and push the project to a public GitHub repository, with index.html at the repository root.
2. Open the repository's Settings → Pages.
3. Under Build and deployment, set Source to Deploy from a branch.
4. Select the main branch and choose /(root), then save.
5. Once GitHub reports a successful deployment, open the published URL and verify that the filters, charts, and comparison panel work correctly.

GitHub Pages serves the committed HTML file; it does not execute the Python build script. To publish future dashboard changes, regenerate index.html locally, commit the updated file, and push it to GitHub.

For additional information, see GitHub's publishing-source documentation: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## Data source, licensing, and attribution

The dashboard uses **`statsmodels.datasets.macrodata`**, containing **203 quarterly observations and 14 original variables**. Skipper Seabold compiled the dataset from Federal Reserve Bank of St. Louis FRED and U.S. Bureau of Labor Statistics sources. The dataset is identified as **public domain** in the [statsmodels documentation](https://www.statsmodels.org/stable/datasets/generated/macrodata.html).

Inflation is the source dataset's annualized log CPI rate. Real GDP growth is derived as `100 * pct_change(realgdp)` and is quarter-over-quarter, **not annualized**. Unemployment is expressed as a percentage.

[Plotly.py and Plotly.js](https://github.com/plotly/plotly.py) are MIT licensed. Dataset and dependency licenses apply to their respective materials. Code, dashboard design, and narrative development received ChatGPT assistance; the narrative notebook documents AI use.
