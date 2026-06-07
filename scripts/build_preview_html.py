"""Build a standalone interactive HTML preview (works on GitHub + HTML Preview)."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import plotly.io as pio

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from Utils.analytics import parse_document_columns, reply_metrics, top_n_with_other
from Utils.data_engineering import get_csv_path, prepare_applications, read_raw_applications
from Utils.Functions import Draw_bar, Draw_boxplot, Draw_document_combinations_plotly, Draw_pie, Draw_upset_png

OUTPUT = ROOT / "dashboard-preview.html"

PLOTLY_CONFIG = '{"displayModeBar": true, "responsive": true, "scrollZoom": true}'
ROW3_CHART_HEIGHT = 640


def _style_fig(fig, height: int = 480):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        autosize=True,
        width=None,
        height=height,
    )
    return fig


def _fig_script(div_id: str, fig, height: int = 480, chart_class: str = "chart") -> str:
    fig = _style_fig(fig, height=height)
    return (
        f'<div id="{div_id}" class="{chart_class}"></div>\n'
        f"<script>Plotly.newPlot('{div_id}', {pio.to_json(fig)}, {PLOTLY_CONFIG});</script>"
    )


def main() -> None:
    df = prepare_applications(read_raw_applications())
    stats = reply_metrics(df)
    docs = parse_document_columns(df)

    charts: list[str] = []

    status = df["Status"].value_counts()
    charts.append(_fig_script("chart_status", Draw_pie(status.values, status.index, "Status of Applications")))

    pos = df["Position_Type"].value_counts()
    charts.append(_fig_script("chart_position", Draw_pie(pos.values, pos.index, "Ratio of Application Types")))

    loc = top_n_with_other(df["Location"].value_counts())
    charts.append(
        _fig_script(
            "chart_cities",
            Draw_bar(loc.values, loc.index, "Applications in Cities", "Number of Applications", "Cities"),
            height=ROW3_CHART_HEIGHT,
            chart_class="chart chart-row3",
        )
    )

    companies = df["Company_Name"].value_counts().head(15).sort_values(ascending=True)
    fig_co = Draw_bar(
        companies.values,
        companies.index,
        "Applications in Companies",
        "Number of Applications",
        "Companies",
    )
    fig_co.update_layout(margin=dict(l=200))
    charts.append(
        _fig_script("chart_companies", fig_co, height=ROW3_CHART_HEIGHT, chart_class="chart chart-row3")
    )

    try:
        upset_png = Draw_upset_png(
            docs,
            figsize=(7, 5.4),
            tick_fontsize=8,
            set_label_fontsize=5,
            show_title=False,
            dpi=140,
        )
        upset_b64 = base64.b64encode(upset_png).decode("ascii")
        docs_chart = (
            f'<div class="upset-wrap">'
            f'<img class="upset" src="data:image/png;base64,{upset_b64}" '
            f'alt="Document combination UpSet plot" />'
            f"</div>"
        )
    except Exception:
        docs_chart = _fig_script("chart_docs", Draw_document_combinations_plotly(docs, h=480))

    df_replied = df.loc[df["Action_Period"] != -1, ["Date", "Action_Period", "Month"]].sort_values("Date")
    reply_chart = ""
    if not df_replied.empty:
        reply_chart = "<h2>Reply Time by Month</h2>" + _fig_script(
            "chart_reply", Draw_boxplot(df_replied, "Action_Period", "Month")
        )

    import plotly

    plotly_js = (Path(plotly.__file__).parent / "package_data" / "plotly.min.js").read_text(
        encoding="utf-8"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Job Application Dashboard — Preview</title>
  <script>{plotly_js}</script>
  <style>
    body {{ background: #0e1117; color: #fafafa; font-family: Arial, sans-serif; margin: 0; padding: 24px; }}
    h1 {{ margin: 0 0 8px; }}
    .sub {{ opacity: 0.85; margin-bottom: 24px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
    .metric {{ background: #262730; border-radius: 8px; padding: 16px; }}
    .metric label {{ display: block; font-size: 0.85rem; opacity: 0.8; }}
    .metric strong {{ font-size: 1.6rem; }}
    h2 {{ border-top: 1px solid #333; padding-top: 20px; margin-top: 28px; }}
    .row2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .row3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; align-items: stretch; }}
    .row3-col {{ display: flex; flex-direction: column; }}
    .row3-header {{ min-height: 72px; margin-bottom: 0.5rem; }}
    .row3-header h3 {{ margin: 0 0 0.35rem; font-size: 1.05rem; }}
    .chart {{ min-height: 460px; width: 100%; }}
    .chart-row3 {{ flex: 1; min-height: {ROW3_CHART_HEIGHT}px; width: 100%; }}
    .upset-wrap {{ flex: 1; min-height: {ROW3_CHART_HEIGHT}px; display: flex; align-items: flex-end; justify-content: center; }}
    .upset {{ width: 100%; max-width: 100%; height: auto; border-radius: 8px; }}
    .note {{ opacity: 0.75; font-size: 0.9rem; margin-top: 8px; }}
    @media (max-width: 900px) {{ .metrics, .row2, .row3 {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <h1>Job Application Dashboard</h1>
  <p class="sub">{len(df)} applications · {get_csv_path().name}</p>
  <div class="metrics">
    <div class="metric"><label>Applications</label><strong>{stats["count"]}</strong></div>
    <div class="metric"><label>Reply rate</label><strong>{stats["reply_rate"]}%</strong></div>
    <div class="metric"><label>Avg reply (days)</label><strong>{stats["avg_reply"]}</strong></div>
    <div class="metric"><label>STD reply (days)</label><strong>{stats["std_reply"]}</strong></div>
  </div>
  <h2>Distribution</h2>
  <div class="row2">
    {charts[0]}
    {charts[1]}
  </div>
  <div class="row3">
    <div class="row3-col">
      <div class="row3-header" aria-hidden="true"><h3>&nbsp;</h3><p class="note">&nbsp;</p></div>
      {charts[2]}
    </div>
    <div class="row3-col">
      <div class="row3-header" aria-hidden="true"><h3>&nbsp;</h3><p class="note">&nbsp;</p></div>
      {charts[3]}
    </div>
    <div class="row3-col">
      <div class="row3-header">
        <h3>Document Combination Frequency</h3>
        <p class="note">Shows which documents you submitted together (CV, cover letter, reference letter, master certificate). Each bar is one combination; taller bars = more applications with that mix.</p>
      </div>
      {docs_chart}
    </div>
  </div>
  {reply_chart}
</body>
</html>
"""

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
