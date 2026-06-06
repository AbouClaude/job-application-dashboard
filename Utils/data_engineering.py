"""
Shared data loading and cleaning for the Job Application Dashboard.

CSV path (first match wins):
  1. Environment variable JOB_APPLICATIONS_CSV
  2. Default: <project_root>/Jobs Applications - Jobs Applying.csv
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from Utils.Functions import Clean_data, fill_time_nanvalue, rename_columns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = PROJECT_ROOT / "Jobs Applications - Jobs Applying.csv"
ENV_CSV_KEY = "JOB_APPLICATIONS_CSV"

COLUMN_RENAMES = {
    "Position Name": "Position_Name",
    "Position Type": "Position_Type",
    "Company Name": "Company_Name",
    "Action Period": "Action_Period",
}


def get_csv_path() -> Path:
    """Resolve CSV path from env or project default."""
    env_path = os.getenv(ENV_CSV_KEY)
    path = Path(env_path).expanduser() if env_path else DEFAULT_CSV
    path = path.resolve()

    if not path.is_file():
        hint = (
            f"Set {ENV_CSV_KEY} to your CSV file, e.g.\n"
            f'  set {ENV_CSV_KEY}=C:\\path\\to\\file.csv'
        )
        raise FileNotFoundError(f"CSV not found: {path}\n{hint}")

    return path


def read_raw_applications() -> pd.DataFrame:
    """Read CSV only — no cleaning."""
    return pd.read_csv(get_csv_path())


def prepare_applications(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich raw application rows."""
    df = Clean_data(df)
    df = rename_columns(df, COLUMN_RENAMES)
    df = df.loc[df["Position_Type"] != "Normal Work"]

    df["Date"] = pd.to_datetime(
        df["Date"].str.replace(",", "."), format="%d.%m.%Y", errors="coerce"
    )
    df.dropna(how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)

    df = fill_time_nanvalue(df)
    df["Action_Period"].fillna(-1, inplace=True)
    df["Notes"].fillna("No note", inplace=True)
    df["Month"] = df["Date"].dt.strftime("%b %Y")

    return df


def ensure_month_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add Month if missing (e.g. old Streamlit cache)."""
    if "Month" not in df.columns:
        df = df.copy()
        df["Month"] = df["Date"].dt.strftime("%b %Y")
    return df


def get_months_chronological(df: pd.DataFrame) -> list[str]:
    """Month labels ('Jan 2025', ...) sorted oldest → newest."""
    if "Month" not in df.columns:
        df = df.copy()
        df["Month"] = df["Date"].dt.strftime("%b %Y")
    month_order = (
        df.dropna(subset=["Date"])
        .groupby("Month")["Date"]
        .min()
        .sort_values()
    )
    return month_order.index.tolist()


@st.cache_data
def load_applications(_cache_version: int = 2) -> pd.DataFrame:
    """Read CSV + clean. Cached for Streamlit pages."""
    df = read_raw_applications()
    return ensure_month_column(prepare_applications(df))


__all__ = [
    "COLUMN_RENAMES",
    "DEFAULT_CSV",
    "ENV_CSV_KEY",
    "PROJECT_ROOT",
    "ensure_month_column",
    "get_csv_path",
    "get_months_chronological",
    "load_applications",
    "prepare_applications",
    "read_raw_applications",
]
