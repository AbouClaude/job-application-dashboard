"""Reusable Streamlit UI helpers."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from Utils.analytics import reply_metrics
from Utils.Functions import Draw_document_combinations_plotly, Draw_upset_png


def render_reply_metrics(df: pd.DataFrame) -> None:
    """Four-column metric row for application / reply stats."""
    stats = reply_metrics(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Applications", stats["count"])
    c2.metric("Reply rate", f"{stats['reply_rate']}%")
    c3.metric("Avg reply (days)", stats["avg_reply"])
    c4.metric("STD reply (days)", stats["std_reply"])


@st.cache_data(show_spinner=False)
def _build_document_chart(_cache_version: int, df_docs: pd.DataFrame) -> tuple[str, object]:
    """UpSet PNG locally; Plotly bar chart if Cloud deps fail."""
    try:
        return (
            "image",
            Draw_upset_png(
                df_docs,
                figsize=(7, 5.4),
                tick_fontsize=8,
                set_label_fontsize=5,
                show_title=False,
            ),
        )
    except Exception:
        return ("plotly", Draw_document_combinations_plotly(df_docs, h=540))


def render_document_upset(df_docs: pd.DataFrame) -> None:
    kind, chart = _build_document_chart(10, df_docs)
    if kind == "image":
        st.image(chart, use_container_width=True)
    else:
        st.plotly_chart(chart, use_container_width=True)
