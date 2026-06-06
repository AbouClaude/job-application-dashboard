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
git clone https://github.com/AbouClaude/job-application-dashboard.git
cd job-application-dashboard
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run Home.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Dashboard preview (no install)

A static snapshot is included: **Jobs_Applications_Dashboard.mhtml**

**GitHub cannot display `.mhtml` in the browser** — clicking the filename shows source code, not the dashboard. Download the file first:

**Option A — Download button (easiest)**  
1. Open [Jobs_Applications_Dashboard.mhtml](https://github.com/AbouClaude/job-application-dashboard/blob/main/Jobs_Applications_Dashboard.mhtml) on GitHub.  
2. Click the **↓ Download** button (top-right of the file view).  
3. Open the downloaded file in **Chrome** or **Edge**.

**Option B — Raw + Save As**  
1. Open the file on GitHub → click **Raw** (top-right).  
2. Press **Ctrl+S** → save as `Jobs_Applications_Dashboard.mhtml` (keep the `.mhtml` extension).

**Option C — Clone the repo**  
```bash
git clone https://github.com/AbouClaude/job-application-dashboard.git
```
Open `Jobs_Applications_Dashboard.mhtml` from the cloned folder.

- Use **Chrome** or **Edge** only — Firefox/Safari do not render MHTML reliably.  
- If the page is blank on Windows: right-click the file → **Properties** → check **Unblock** → OK → open again.

To **regenerate** the preview after UI changes: run `streamlit run Home.py`, open the app in Chrome/Edge, then **Ctrl+S** → save as **Webpage, Single File (*.mhtml)** and replace `Jobs_Applications_Dashboard.mhtml` in the repo root.

> MHTML is a saved web page export. Interactivity may be limited compared to the live app; for the full experience, run `streamlit run Home.py` locally.

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

## CSV schema

Expected columns: `Date`, `Time`, `Position Name`, `Position Type`, `Company Name`, `Status`, `Location`, `Action Period`, `CV_CL_RL_CR`

Optional override via environment variable:

```powershell
$env:JOB_APPLICATIONS_CSV = "C:\path\to\your\file.csv"
streamlit run Home.py
```
