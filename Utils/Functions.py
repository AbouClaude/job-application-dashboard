"""Chart builders and data-cleaning helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def Clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop unnamed / empty CSV columns."""
    return df.loc[:, ~df.columns.str.contains("^Unnamed")]


def rename_columns(df: pd.DataFrame, cols_dict: dict[str, str]) -> pd.DataFrame:
    return df.rename(columns=cols_dict)


def fill_time_nanvalue(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing application times from the observed hour distribution."""
    if "Time" not in df.columns:
        return df

    df = df.copy()
    # Object dtype — avoids Arrow/string column TypeError on Streamlit Cloud
    df["Time"] = df["Time"].astype(object).where(
        df["Time"].notna() & (df["Time"].astype(str).str.strip() != ""),
        other=None,
    )

    parsed = pd.to_datetime(
        df["Time"].astype(str).str.strip().replace("None", ""),
        format="%H:%M",
        errors="coerce",
    )
    df["hour"] = parsed.dt.hour

    hour_probs = df["hour"].value_counts(normalize=True)
    nan_mask = df["hour"].isna()
    nan_count = int(nan_mask.sum())

    if nan_count and not hour_probs.empty:
        imputed_hours = np.random.choice(
            hour_probs.index,
            size=nan_count,
            p=hour_probs.values,
        )
        df.loc[nan_mask, "hour"] = imputed_hours
        df.loc[nan_mask, "Time"] = [f"{int(h):02d}:00" for h in imputed_hours]

    df.drop(columns=["hour"], inplace=True)
    return df


def Draw_bar(
    values,
    names,
    title: str,
    xaxis: str,
    yaxis: str,
    s: int = 14,
    w: int = 700,
    h: int = 700,
    o: str = "h",
):
    fig = go.Figure(data=[go.Bar(x=values, y=names, orientation=o)])
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=s + 6, family="Arial")),
        xaxis=dict(
            title=dict(text=f"<b>{xaxis}</b>", font=dict(size=s + 4, family="Arial")),
            tickfont=dict(size=s + 2, family="Arial"),
        ),
        yaxis=dict(
            title=dict(text=f"<b>{yaxis}</b>", font=dict(size=s + 4, family="Arial")),
            tickfont=dict(size=s + 2, family="Arial"),
            title_standoff=20,
        ),
        width=w,
        height=h,
    )
    return fig


def Draw_pie(values, names, title: str, s: int = 16, w: int = 700, h: int = 500):
    fig = go.Figure(
        data=[
            go.Pie(
                values=values,
                labels=names,
                textinfo="percent+value",
                textfont=dict(size=s, family="Arial Black"),
                marker=dict(colors=px.colors.qualitative.Plotly),
            )
        ]
    )
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=s + 6, family="Arial Black")),
        legend=dict(font=dict(size=s, family="Arial Black")),
        width=w,
        height=h,
    )
    return fig


STATUS_GROUP_ORDER = ["Waiting", "Not selected", "Others"]
STATUS_GROUP_COLORS = {
    "Waiting": "#636efa",
    "Not selected": "#ef553b",
    "Others": "#00cc96",
}


def _status_group(status) -> str:
    if status == "Waiting":
        return "Waiting"
    if status in ("Rejected", "Not selected"):
        return "Not selected"
    return "Others"


def _full_month_day_range(days: pd.Series) -> pd.DatetimeIndex:
    """Every calendar day for each month present in `days` (incl. zero-application days)."""
    periods = sorted(days.dt.to_period("M").unique())
    full_range = pd.DatetimeIndex([])
    for period in periods:
        month_days = pd.date_range(
            period.start_time.normalize(),
            period.end_time.normalize(),
            freq="D",
        )
        full_range = full_range.union(month_days)
    return full_range.sort_values()


def Draw_daily_applications_by_status(
    df: pd.DataFrame,
    date_col: str = "Date",
    status_col: str = "Status",
    title: str = "Applications per day",
    s: int = 14,
    w: int = 900,
    h: int = 450,
):
    """Stacked daily bar chart colored by job status."""
    plot_df = df[[date_col, status_col]].dropna(subset=[date_col]).copy()
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title=dict(text=f"<b>{title}</b>"))
        return fig

    plot_df["Day"] = plot_df[date_col].dt.normalize()
    plot_df["Status_group"] = plot_df[status_col].map(_status_group)

    counts = plot_df.groupby(["Day", "Status_group"]).size().unstack(fill_value=0)
    all_days = _full_month_day_range(plot_df["Day"])
    counts = counts.reindex(all_days, fill_value=0).sort_index()

    for status in STATUS_GROUP_ORDER:
        if status not in counts.columns:
            counts[status] = 0

    day_labels = counts.index.strftime("%d.%m.%Y")

    fig = go.Figure()
    for status in STATUS_GROUP_ORDER:
        fig.add_trace(
            go.Bar(
                x=day_labels,
                y=counts[status],
                name=status,
                marker_color=STATUS_GROUP_COLORS[status],
            )
        )

    fig.update_layout(
        barmode="stack",
        title=dict(text=f"<b>{title}</b>", font=dict(size=s + 6, family="Arial")),
        xaxis=dict(
            title=dict(text="<b>Date</b>", font=dict(size=s + 2, family="Arial")),
            tickangle=-45,
            tickfont=dict(size=s, family="Arial"),
        ),
        yaxis=dict(
            title=dict(text="<b># Applications</b>", font=dict(size=s + 2, family="Arial")),
            tickfont=dict(size=s, family="Arial"),
            dtick=1,
        ),
        legend=dict(title="Status", font=dict(size=s, family="Arial")),
        width=w,
        height=h,
    )
    return fig


def Draw_boxplot(dfr: pd.DataFrame, v: str, p: str, s: int = 16, w: int = 900, h: int = 500):
    fig = go.Figure()
    for month in dfr[p].unique():
        fig.add_trace(go.Box(y=dfr.loc[dfr[p] == month, v], name=month))

    fig.update_layout(
        title=dict(
            text=(
                "<b>Action Period Distribution per Month</b><br>"
                "<sup>Distribution of days taken to receive a reply per month — "
                "outliers indicate unusually long or fast responses</sup>"
            ),
            font=dict(size=s + 4, family="Arial Black"),
        ),
        xaxis_title="<b>Months</b>",
        xaxis=dict(
            title_font=dict(size=s, family="Arial Black"),
            tickfont=dict(size=s - 4, family="Arial Black"),
        ),
        yaxis_title="<b>Action Period (days)</b>",
        yaxis=dict(
            title_font=dict(size=s, family="Arial Black"),
            tickfont=dict(size=s - 4, family="Arial Black"),
        ),
        showlegend=False,
        width=w,
        height=h,
    )
    return fig


_UPSET_LABELS = {
    "CV": "CV",
    "Cover_Letter": "Cover letter",
    "Reference_Letter": "Ref. Letter",
    "Master_Certificate": "Master cert.",
}

_DEGREE_COLORS = {1: "#636efa", 2: "#ffa15a", 3: "#00cc96", 4: "#d62728"}


def _document_combo_labels(df_docs: pd.DataFrame) -> pd.Series:
    plot_docs = df_docs.rename(columns=_UPSET_LABELS)

    def label_row(row: pd.Series) -> str:
        parts = [col for col in plot_docs.columns if row[col] == 1]
        return " + ".join(parts) if parts else "None"

    return plot_docs.apply(label_row, axis=1)


def Draw_document_combinations_plotly(df_docs: pd.DataFrame, s: int = 14, h: int = 500):
    """Plotly fallback — works on Streamlit Cloud (upsetplot + matplotlib 3.10+ breaks)."""
    labels = _document_combo_labels(df_docs)
    counts = labels.value_counts().sort_values(ascending=True)
    bar_colors = [
        _DEGREE_COLORS.get(label.count("+") + 1, "#888888") for label in counts.index
    ]

    fig = go.Figure(
        go.Bar(
            x=counts.values,
            y=counts.index,
            orientation="h",
            marker=dict(color=bar_colors),
        )
    )
    fig.update_layout(
        title=dict(
            text="<b>Document Combination Frequency</b>",
            font=dict(size=s + 6, family="Arial"),
        ),
        xaxis=dict(
            title=dict(text="<b>Applications</b>", font=dict(size=s + 2, family="Arial")),
            tickfont=dict(size=s, family="Arial"),
        ),
        yaxis=dict(tickfont=dict(size=s - 2, family="Arial")),
        height=h,
        margin=dict(l=120),
    )
    return fig


def draw_document_chart(df_docs: pd.DataFrame, **upset_kwargs) -> tuple[str, object]:
    """
    Return ('pyplot', matplotlib.Figure) or ('plotly', go.Figure).
    UpSet fails on Streamlit Cloud (Python 3.14 + matplotlib 3.10+).
    """
    import sys

    if sys.version_info >= (3, 13):
        return "plotly", Draw_document_combinations_plotly(df_docs)

    try:
        return "pyplot", Draw_upset(df_docs, **upset_kwargs)
    except (ValueError, TypeError):
        return "plotly", Draw_document_combinations_plotly(df_docs)


def Draw_upset(
    df_docs: pd.DataFrame,
    figsize=(7, 3),
    tick_fontsize: int = 10,
    set_label_fontsize: int = 8,
    title_fontsize: int = 6,
    element_size: int = 20,
    show_title: bool = False,
):
    import matplotlib.pyplot as plt
    from upsetplot import UpSet, from_memberships

    plot_docs = df_docs.rename(columns=_UPSET_LABELS)

    memberships = from_memberships(
        plot_docs.apply(
            lambda row: [col for col in plot_docs.columns if row[col] == 1], axis=1
        )
    )
    memberships = memberships.reorder_levels(list(_UPSET_LABELS.values()))

    degree_colors = {1: "#636efa", 2: "#ffa15a", 3: "#00cc96", 4: "#d62728"}

    fig_upset = UpSet(
        memberships,
        sort_by="degree",
        sort_categories_by=None,
        subset_size="count",
        show_counts=False,
        element_size=element_size,
    )

    # Plot with default styles first — custom subset_styles break on Cloud (Py 3.14 + matplotlib)
    fig = plt.figure(figsize=figsize)
    result = fig_upset.plot(fig=fig)
    fig.patch.set_facecolor("#0e1117")

    totals_ax = result.get("totals")
    if totals_ax is not None:
        for patch in totals_ax.patches:
            patch.set_facecolor("#83c9ff")
        totals_ax.set_ylabel("")

    inter_ax = result.get("intersections")
    if inter_ax is not None:
        for patch, subset in zip(inter_ax.patches, fig_upset.intersections.index):
            patch.set_facecolor(degree_colors.get(sum(subset), "#888888"))
            patch.set_edgecolor("#0e1117")

    for ax in fig.axes:
        ax.set_facecolor("#0e1117")
        ax.tick_params(axis="x", colors="white", labelsize=tick_fontsize)
        ax.tick_params(axis="y", colors="white", labelsize=tick_fontsize)
        ax.yaxis.label.set_color("white")
        ax.xaxis.label.set_color("white")
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(tick_fontsize)
            label.set_color("white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444444")

    label_ax = result.get("totals") or result.get("matrix")
    if label_ax is not None:
        label_ax.tick_params(
            axis="y", colors="white", labelsize=set_label_fontsize, pad=12
        )
        for label in label_ax.get_yticklabels():
            text = label.get_text().strip()
            if not text or text.replace(".", "", 1).isdigit():
                continue
            label.set_fontsize(set_label_fontsize)
            label.set_color("white")
            label.set_horizontalalignment("right")
            label.set_clip_on(False)

    if inter_ax is not None:
        inter_ax.tick_params(axis="x", labelsize=tick_fontsize, colors="white")
        inter_ax.tick_params(axis="y", labelsize=tick_fontsize, colors="white")
        for label in inter_ax.get_xticklabels():
            label.set_fontsize(tick_fontsize)

    if show_title:
        fig.suptitle(
            "Document Combination Frequency",
            fontsize=title_fontsize,
            fontweight="bold",
            color="white",
            y=0.98,
        )
        fig.subplots_adjust(left=0.50, right=0.97, top=0.88, bottom=0.18, wspace=0.55)
    else:
        fig.subplots_adjust(left=0.50, right=0.97, top=0.96, bottom=0.18, wspace=0.55)

    return fig
