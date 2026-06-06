# Job Application Dashboard

An interactive **Streamlit** dashboard for analyzing job applications from a CSV export. Track reply rates, explore status and location patterns, compare document combinations, and drill down by month.

## Features

**Home — overview**
- Key metrics: total applications, reply rate, average & standard deviation of reply time (days)
- Status and position-type distribution (pie charts)
- Applications by city and top employers (bar charts)
- Document combination analysis ([UpSet plot](https://upset.app/)) — CV, cover letter, reference letter, master certificate
- Reply time distribution by month (box plot)

**Monthly Analysis**
- Filter by one or more months
- Daily application timeline stacked by status
- Status & position breakdown for the selected period

## Tech stack

| Tool | Role |
|------|------|
| [Streamlit](https://streamlit.io/) | Multipage web app |
| [Pandas](https://pandas.pydata.org/) | Data loading, cleaning, aggregation |
| [NumPy](https://numpy.org/) | Metrics & time imputation |
| [Plotly](https://plotly.com/python/) | Interactive charts |
| [Matplotlib](https://matplotlib.org/) + [UpSetPlot](https://upsetplot.readthedocs.io/) | Document combination chart |

## Sample data & privacy

This repo is **safe to share publicly**. The bundled file `data/Jobs_Application.csv` is a prepared sample — not raw personal data:

- **300 applications** (first rows after the same filters used in the app)
- **Anonymous employer names** — real companies are replaced with `Company 1`, `Company 2`, … so application counts stay correct without exposing who you applied to
- **No notes column** — personal comments are omitted
- **Missing times preserved** — some rows keep an empty `Time` field so the app’s time-imputation step still runs when you launch it

Status labels use user-friendly wording (e.g. `Not selected` instead of `Rejected`).

## Data pipeline

Raw CSV → clean column names → filter irrelevant rows → parse dates → **impute missing application times** from the observed hour distribution → derive monthly labels → cache for the UI.

## Quick start

```bash
git clone https://github.com/Abou_Claude/job-application-dashboard.git
cd job-application-dashboard
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run Home.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Dashboard preview (no install)

A static snapshot of the app is included as **[Jobs_Applications_Dashboard.mhtml](Jobs_Applications_Dashboard.mhtml)**.

- **Download** the file from this repo (or clone the repo and open it locally)
- **Open** it in **Chrome** or **Edge** (File → Open, or double-click)
- View charts and layout **without** running Python or Streamlit

> MHTML is a saved web page export. Interactivity may be limited compared to the live app; for the full experience, use `streamlit run Home.py` or deploy on Streamlit Cloud.

## Project structure

```
Home.py                    # Overview dashboard (entry point)
Pages/
  Month_Analysis.py        # Monthly drill-down
Utils/
  data_engineering.py      # CSV load, clean, cache
  analytics.py             # Metrics & helpers
  Functions.py             # Chart builders
  streamlit_ui.py          # Shared UI components
data/
  Jobs_Application.csv              # Sample dataset (committed)
Jobs_Applications_Dashboard.mhtml   # Static dashboard preview
ARCHITECTURE.md                     # Module layout & data flow
architecture.html          # Interactive architecture diagrams
```

## Architecture

- [ARCHITECTURE.md](ARCHITECTURE.md) — Mermaid diagrams (structure & data flow)
- [architecture.html](architecture.html) — open in a browser for rendered diagrams

## Tests

```bash
python test_data_engineering.py
```

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **New app** → select this repository → main file: `Home.py` → **Deploy**.

No secrets required — the app uses `data/Jobs_Application.csv` by default.

## CSV schema

Expected columns: `Date`, `Time`, `Position Name`, `Position Type`, `Company Name`, `Status`, `Location`, `Action Period`, `CV_CL_RL_CR`

Optional override via environment variable:

```powershell
$env:JOB_APPLICATIONS_CSV = "C:\path\to\your\file.csv"
streamlit run Home.py
```
