"""Reusable Streamlit UI helpers."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from Utils.analytics import reply_metrics
from Utils.Functions import Draw_upset_png


def render_reply_metrics(df: pd.DataFrame) -> None:
    """Four-column metric row for application / reply stats."""
    stats = reply_metrics(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Applications", stats["count"])
    c2.metric("Reply rate", f"{stats['reply_rate']}%")
    c3.metric("Avg reply (days)", stats["avg_reply"])
    c4.metric("STD reply (days)", stats["std_reply"])


@st.cache_data(show_spinner=False)
def _build_upset_image(_cache_version: int, df_docs: pd.DataFrame) -> bytes:
    return Draw_upset_png(
        df_docs,
        figsize=(7, 5.4),
        tick_fontsize=8,
        set_label_fontsize=5,
        show_title=False,
    )


def render_document_upset(df_docs: pd.DataFrame) -> None:
    st.image(_build_upset_image(9, df_docs), use_container_width=True)
