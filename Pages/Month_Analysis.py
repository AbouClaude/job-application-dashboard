import streamlit as st

from Utils import data_engineering as de
from Utils.Functions import Draw_boxplot, Draw_daily_applications_by_status, Draw_pie
from Utils.streamlit_ui import render_reply_metrics


def main():
    st.title("Monthly Analysis")

    df = de.load_applications()

    st.sidebar.header("Filters")
    all_months = de.get_months_chronological(df)
    selected_months = st.sidebar.multiselect(
        "Select month(s)",
        options=all_months,
        default=[],
        placeholder="Choose month(s)...",
        help="Months are listed oldest to newest.",
    )

    if not selected_months:
        st.info("Select one or more months from the sidebar to view the analysis.")
        st.stop()

    df_month = df[df["Month"].isin(selected_months)].copy()
    st.caption(
        f"Showing **{len(df_month)}** applications across "
        f"**{len(selected_months)}** month(s)"
    )

    render_reply_metrics(df_month)
    st.divider()

    st.subheader("Applications per day")
    st.plotly_chart(
        Draw_daily_applications_by_status(df_month),
        use_container_width=True,
    )
    st.divider()

    st.subheader("Distribution")
    c1, c2 = st.columns(2)
    with c1:
        status = df_month["Status"].value_counts()
        st.plotly_chart(
            Draw_pie(status.values, status.index, "Status"),
            use_container_width=True,
        )
    with c2:
        pos = df_month["Position_Type"].value_counts()
        st.plotly_chart(
            Draw_pie(pos.values, pos.index, "Position type"),
            use_container_width=True,
        )

    st.divider()

    st.subheader("Reply time by month")
    df_replied = (
        df_month.loc[df_month["Action_Period"] != -1, ["Date", "Action_Period", "Month"]]
        .sort_values("Date")
    )
    if df_replied.empty:
        st.info("No replies in the selected months.")
    else:
        st.plotly_chart(
            Draw_boxplot(df_replied, "Action_Period", "Month"),
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
