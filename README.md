# Job Application Dashboard

Streamlit dashboard for tracking and analyzing job applications from a CSV export.

## Architecture

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — module layout & data flow (Mermaid)
- **[architecture.html](architecture.html)** — interactive diagrams in the browser

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/job-application-dashboard.git
cd job-application-dashboard
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

The repo ships with **`data/Jobs_Application.csv`** — first 300 applications after filtering, anonymous company names, no notes column.

## Data

| File | Purpose |
|------|---------|
| `data/Jobs_Application.csv` | Default for clone / deploy (300 rows, anonymous employers) |
| `Jobs Applications - Jobs Applying.csv` | Your private file — **gitignored**, local only |

### Build the public CSV (do this before GitHub push)

The dashboard reads `data/Jobs_Application.csv`. That file is **not** edited by hand — you generate it from your private spreadsheet:

1. Keep your real data in `Jobs Applications - Jobs Applying.csv` (never commit this file).
2. From the project folder, run:

```powershell
cd "C:\Users\hazem\job searching project"
python scripts/build_public_csv.py
```

What the script does:

- Reads the private CSV
- Applies the same filters as the app (e.g. excludes "Normal Work")
- Keeps the **first 300** rows after filtering
- Replaces employer names with `Company 1`, `Company 2`, …
- Removes the **Notes** column (keeps **Time** for time imputation)
- Writes `data/Jobs_Application.csv`

3. Run the app to verify:

```powershell
streamlit run Home.py
```

Open the URL shown in the terminal. Use the sidebar on **Home** to filter by month, status, or position type. Open **Monthly Analysis** from the sidebar for day-by-day breakdowns.

## Data

Default CSV: `Jobs Applications - Jobs Applying.csv` in the project root.

Override with an environment variable:

```powershell
$env:JOB_APPLICATIONS_CSV = "C:\path\to\your\file.csv"
streamlit run Home.py
```

Expected columns: `Date`, `Time`, `Position Name`, `Position Type`, `Company Name`, `Status`, `Location`, `Action Period`, `CV_CL_RL_CR`, `Notes`.

## Tests

```bash
python test_data_engineering.py
```
