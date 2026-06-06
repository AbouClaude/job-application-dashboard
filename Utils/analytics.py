"""Shared metrics and aggregations for dashboard pages."""

from __future__ import annotations

import pandas as pd

DOCUMENT_COLUMNS = ["CV", "Cover_Letter", "Reference_Letter", "Master_Certificate"]


def reply_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    """Summary stats for applications with a known reply time (Action_Period != -1)."""
    n = len(df)
    if n == 0:
        return {"count": 0, "reply_rate": 0.0, "avg_reply": 0.0, "std_reply": 0.0}

    replied = df.loc[df["Action_Period"] != -1, "Action_Period"]
    return {
        "count": n,
        "reply_rate": round(replied.count() / n * 100, 3),
        "avg_reply": round(replied.mean(), 2) if len(replied) else 0.0,
        "std_reply": round(replied.std(), 2) if len(replied) else 0.0,
    }


def parse_document_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Expand CV_CL_RL_CR (e.g. '1100') into one column per document flag."""
    codes = df["CV_CL_RL_CR"].astype(str)
    return pd.DataFrame(
        {col: codes.str[i].astype(int) for i, col in enumerate(DOCUMENT_COLUMNS)},
        index=df.index,
    )


def top_n_with_other(counts: pd.Series, n: int = 6, other_label: str = "Other Cities") -> pd.Series:
    """Top *n* categories plus a rolled-up 'other' bucket, sorted ascending for bar charts."""
    top = counts.head(n)
    others = counts.iloc[n:].sum()
    if others > 0:
        top = pd.concat([top, pd.Series({other_label: others})])
    return top.sort_values(ascending=True)
