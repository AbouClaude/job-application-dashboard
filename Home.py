import streamlit as st

from Utils.analytics import parse_document_columns, top_n_with_other
from Utils.data_engineering import get_csv_path, load_applications
from Utils.Functions import Draw_bar, Draw_boxplot, Draw_document_combinations_plotly, Draw_pie
from Utils.streamlit_ui import render_reply_metrics


def main():
    st.set_page_config(page_title="Job Application Dashboard", layout="wide")
    st.title("Job Application Dashboard")

    df = load_applications()
    st.markdown(
        f'<p style="font-size:1.15rem; line-height:1.5; margin-top:-0.25rem; '
        f'opacity:0.85;">{len(df)} applications · '
        f"<code>{get_csv_path().name}</code></p>",
        unsafe_allow_html=True,
    )

    render_reply_metrics(df)
    st.divider()

    st.subheader("Distribution")
    col1, col2 = st.columns(2)
    with col1:
        status_count = df["Status"].value_counts()
        st.plotly_chart(
            Draw_pie(status_count.values, status_count.index, "Status of Applications"),
            use_container_width=True,
        )
    with col2:
        position_count = df["Position_Type"].value_counts()
        st.plotly_chart(
            Draw_pie(
                position_count.values,
                position_count.index,
                "Ratio of Application Types",
            ),
            use_container_width=True,
        )

    st.divider()

    col1, col2, col3 = st.columns(3, vertical_alignment="top")
    with col1:
        count_location = top_n_with_other(df["Location"].value_counts())
        st.plotly_chart(
            Draw_bar(
                count_location.values,
                count_location.index,
                "Applications in Cities",
                "Number of Applications",
                "Cities",
            ),
            use_container_width=True,
        )
    with col2:
        company_counts = df["Company_Name"].value_counts().head(15).sort_values(ascending=True)
        fig_bar = Draw_bar(
            company_counts.values,
            company_counts.index,
            "Applications in Companies",
            "Number of Applications",
            "Companies",
        )
        fig_bar.update_layout(margin=dict(l=200))
        st.plotly_chart(fig_bar, use_container_width=True)
    with col3:
        st.markdown("##### Document Combination Frequency")
        st.markdown(
            '<p style="font-size:0.95rem; line-height:1.45; opacity:0.8; margin:0 0 0.5rem 0;">'
            "Shows which documents you submitted together "
            "(CV, cover letter, reference letter, master certificate). "
            "Each bar is one combination; taller bars = more applications with that mix."
            "</p>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            Draw_document_combinations_plotly(parse_document_columns(df), h=540),
            use_container_width=True,
        )

    st.divider()

    st.subheader("Reply Time by Month")
    df_replied = (
        df.loc[df["Action_Period"] != -1, ["Date", "Action_Period", "Month"]]
        .sort_values("Date")
    )
    if df_replied.empty:
        st.info("No replies recorded yet.")
    else:
        st.plotly_chart(
            Draw_boxplot(df_replied, "Action_Period", "Month"),
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
