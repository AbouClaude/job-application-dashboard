# Architecture — Job Application Dashboard

This project is organized in **layers**: storage → data pipeline → business logic & charts → shared UI → Streamlit pages.

> **Sankey vs flowchart:** A **Sankey diagram** is best when link *thickness* shows *how much* flows between stages (e.g. row counts through cleaning). A **layered flowchart** is better for *code structure* — which modules exist and what imports what. Both are included below.

Open **`architecture.html`** in a browser for an interactive rendered version of these diagrams.

---

## Module structure (code layout)

```mermaid
flowchart TB
    subgraph Storage
        CSV["Jobs Applications - Jobs Applying.csv"]
        ENV["JOB_APPLICATIONS_CSV (optional)"]
    end

    subgraph Data["Data layer"]
        DE["Utils/data_engineering.py<br/>load · clean · cache"]
    end

    subgraph Logic["Logic & visualization"]
        AN["Utils/analytics.py<br/>metrics · filters · doc flags"]
        FN["Utils/Functions.py<br/>Plotly · UpSet · cleaning helpers"]
    end

    subgraph UI["Shared UI"]
        SU["Utils/streamlit_ui.py<br/>metrics row · sidebar filters"]
    end

    subgraph Pages["Streamlit pages"]
        HOME["Home.py<br/>overview dashboard"]
        MONTH["Pages/Month_Analysis.py<br/>monthly drill-down"]
    end

    ENV -.-> DE
    CSV --> DE
    DE --> FN
    DE --> HOME
    DE --> MONTH
    AN --> SU
    AN --> HOME
    FN --> HOME
    FN --> MONTH
    SU --> HOME
    SU --> MONTH
```

---

## Data flow (runtime — Sankey)

How application rows move through the pipeline (503 applications after filtering out **Normal Work**):

```mermaid
sankey-beta
    Raw CSV,Cleaned applications,503
    Raw CSV,Excluded Normal Work,39
    Cleaned applications,Replied,335
    Cleaned applications,Awaiting reply,168
```

---

## What each page renders

| Page | Filters | Charts / outputs |
|------|---------|------------------|
| **Home** | Month, status, position type (sidebar) | Reply metrics · status & type pies · top cities & companies · UpSet (documents) · reply-time box plot |
| **Monthly Analysis** | Month multiselect | Reply metrics · daily stacked bars by status · status & type pies · reply-time box plot |

---

## File tree

```
job searching project/
├── Home.py                      # Entry point — overview dashboard
├── Pages/
│   └── Month_Analysis.py        # Per-month drill-down
├── Utils/
│   ├── data_engineering.py      # CSV path, load, clean, @st.cache_data
│   ├── analytics.py             # reply_metrics, filters, document parsing
│   ├── Functions.py             # Draw_bar, Draw_pie, Draw_boxplot, Draw_upset, …
│   └── streamlit_ui.py          # render_reply_metrics, render_home_filters
├── ARCHITECTURE.md              # This file (Mermaid source)
├── architecture.html            # Browser-rendered diagrams
├── test_data_engineering.py     # Pipeline smoke tests
├── requirements.txt
└── Jobs Applications - Jobs Applying.csv
```

---

## Dependency summary

| Module | Imports from | Used by |
|--------|--------------|---------|
| `data_engineering.py` | `Functions` (cleaning) | `Home`, `Month_Analysis`, `streamlit_ui`, tests |
| `analytics.py` | — | `Home`, `streamlit_ui`, tests |
| `Functions.py` | plotly, matplotlib, upsetplot | `Home`, `Month_Analysis`, `data_engineering` |
| `streamlit_ui.py` | `data_engineering`, `analytics` | `Home`, `Month_Analysis` |
