"""Reusable Streamlit UI helpers."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from Utils.analytics import reply_metrics


def render_reply_metrics(df: pd.DataFrame) -> None:
    """Four-column metric row for application / reply stats."""
    stats = reply_metrics(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Applications", stats["count"])
    c2.metric("Reply rate", f"{stats['reply_rate']}%")
    c3.metric("Avg reply (days)", stats["avg_reply"])
    c4.metric("STD reply (days)", stats["std_reply"])
