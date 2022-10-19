import datetime

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from scipy.stats import ttest_ind, ttest_rel

import spire_fyi.utils as utils

alt.data_transformers.disable_max_rows()
image = Image.open("assets/images/spire_background.png")

st.set_page_config(
    page_title="Spire FYI",
    page_icon=image,
    layout="wide",
)
c1, c2 = st.columns([1, 3])

c2.header("Spire FYI")
c2.caption("A viewpoint above Solana data")
c1.image(
    image,
    width=200,
)
st.write("---")
st.header("Overview")
with st.expander("TODO list"):
    st.write(
        """
    TODO: figure out which go here, organize by NFT/DEX/Other
    - NFT
        - NFT tx by marketplace
        - Daily NFT mints by program
        - Daily Avg NFT mints by purchase
        - Eth vs Sol NFT mints / tx
    - Defi
        - Daily active swappers by DEX
        - Swap volume
        ...
    - Programs
        - program_id by date (since 2022-01-01)
        - x: date, y: tx_count or num_signers, color: program ID
        - signers by program_id by date, for top N programs (~100 should be more than enough), use flipside labels if possible
        - for heat map/network
        - maybe get rid of the date aspect?
    - New User Activity
    - new_users by date (past 30 d)
        - use as a list of new users for other info
    - program_id by date (same as above but specifically for new users last 30d)
    - signers by program_id by date, for top N programs (same as above but specifically for new users last 30d)
    - first n transactions for each new user
    - program_count, tx_count per day for each new user, using flipside category labels if possible
        """
    )


df = utils.load_labeled_program_data()
df["Date"] = pd.to_datetime(df["Date"])


def get_program_chart_data(df, metric, num_programs, agg_method, date_range, exclude_solana):
    if date_range == "All dates":
        chart_df = df.copy()
    elif date_range == "Year to Date":
        chart_df = df.copy()[df.Date >= "2022-01-01"]
    else:
        chart_df = df.copy()[df.Date >= (datetime.datetime.today() - pd.Timedelta(date_range))]

    if exclude_solana:
        chart_df = chart_df[chart_df.LABEL != "solana"]
    program_ids = (
        chart_df.groupby("PROGRAM_ID")
        .agg({metric: agg_method})
        .sort_values(by=metric, ascending=False)
        .iloc[:num_programs]
        .index
    )
    chart_df = (
        chart_df[chart_df.PROGRAM_ID.isin(program_ids)]
        .sort_values(by=["Date", metric], ascending=False)
        .reset_index()
    )

    return chart_df


agg_method_dict = {
    "mean": "Average within date range",
    "sum": "Total within date range",
    "max": "Highest daily usage during date range",
}
metric_dict = {"SIGNERS": "Number of signers", "TX_COUNT": "Transaction Count"}

st.subheader("Programs")
c1, c2, c3, c4 = st.columns(4)
metric = c1.radio(
    "Choose a metric",
    metric_dict.keys(),
    format_func=lambda x: metric_dict[x],
    horizontal=True,
    key="program_metric",
)
num_programs = c2.slider("Number of Programs", 1, 25, 10, key="program_slider")
agg_method = c3.radio(
    "Choose an aggregtion method",
    agg_method_dict.keys(),
    format_func=lambda x: agg_method_dict[x],
    horizontal=True,
    key="program_agg_method",
)
exclude_solana = c4.checkbox("Exclude Solana System Programs?", key="program_exclude_solana")
date_range = st.radio(
    "Choose a date range:",
    [  # #TODO: not doing more dates until more data is queried
        # "All dates",
        # "Year to Date",
        # "180d",
        "90d",
        "60d",
        "30d",
        "14d",
        "7d",
    ],
    horizontal=True,
    key="program_date_range",
)

chart_df = get_program_chart_data(df, metric, num_programs, agg_method, date_range, exclude_solana)
chart_df["Name"] = chart_df.apply(
    utils.apply_program_name,
    axis=1,
)

chart = (
    alt.Chart(chart_df)
    .mark_line()
    .encode(
        x=alt.X("yearmonthdatehours(Date)", title=None),
        y=alt.Y(metric, title=metric_dict[metric], sort="-y"),
        color=alt.Color(
            "Name",
            title="Program Name",
            scale=alt.Scale(scheme="turbo"),
            sort=alt.EncodingSortField(metric, op=agg_method, order="descending"),
        ),
        tooltip=[
            alt.Tooltip("yearmonthdatehours(Date)", title="Date"),
            alt.Tooltip("TX_COUNT", title=metric_dict["TX_COUNT"], format=","),
            alt.Tooltip("SIGNERS", title=metric_dict["SIGNERS"], format=","),
            alt.Tooltip("PROGRAM_ID", title="Program ID"),
            alt.Tooltip("LABEL_TYPE", title="Label Type"),
            alt.Tooltip("LABEL_SUBTYPE", title="Label Subtype"),
            alt.Tooltip("LABEL", title="Label"),
            alt.Tooltip("ADDRESS_NAME", title="Address Name"),
        ],
    )
    .properties(height=800, width=800)
    .interactive()
)
st.altair_chart(chart, use_container_width=True)
with st.expander("View and Download Data Table"):
    st.write(chart_df)
    st.download_button(
        "Press to Download",
        chart_df.to_csv().encode("utf-8"),
        f"program_ids_top{num_programs}_{agg_method}_{date_range.replace(' ', '')}_{metric}.csv",
        "text/csv",
        key="download-program-ids",
    )

# #%ODO: melt, multiline tooltip
# df = df.melt(
#     id_vars=["Date", "CREATOR", "LABEL_TYPE", "LABEL_SUBTYPE", "LABEL", "ADDRESS_NAME"]
# )
# df


st.header("Programs by date")
weekly_program_data = utils.load_weekly_program_data()
weekly_new_program_data = utils.load_weekly_new_program_data()

c1, c2 = st.columns(2)
chart = (
    alt.Chart(weekly_program_data, title="Unique Program Count: Weekly")
    .mark_area(
        line={"color": "#4B3D60"},
        color=alt.Gradient(
            gradient="linear",
            stops=[alt.GradientStop(color="#4B3D60", offset=0), alt.GradientStop(color="#FD5E53", offset=1)],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
        interpolate="monotone",
    )
    .encode(
        x=alt.X("yearmonthdate(WEEK)", title="Date"),
        y=alt.Y("UNIQUE_PROGRAMS", title="Number of Programs"),
        tooltip=[
            alt.Tooltip("yearmonthdate(WEEK)", title="Date (start of week)"),
            alt.Tooltip("UNIQUE_PROGRAMS", title="Number of Programs"),
        ],
    )
    .interactive()
    .properties(height=600)
)
c1.altair_chart(chart, use_container_width=True)

base = alt.Chart(weekly_new_program_data, title="New Programs: Weekly").encode(
    x=alt.X("yearmonthdate(WEEK):T", title="Date"),
    tooltip=[
        alt.Tooltip("yearmonthdate(WEEK):T", title="Date (start of week)"),
        alt.Tooltip("New Programs"),
        alt.Tooltip("Cumulative Programs"),
    ],
)
bar = base.mark_bar(width=5, color="#4B3D60").encode(
    y=alt.Y("New Programs"),
)
line = base.mark_line(color="#FFE373").encode(
    y="Cumulative Programs",
)
chart = (bar + line).interactive().properties(height=600).resolve_scale(y="independent")
c2.altair_chart(chart, use_container_width=True)
with st.expander("View and Download Data Table"):
    combined_program_df = weekly_new_program_data.merge(weekly_program_data, on="WEEK")
    st.write(combined_program_df)
    st.download_button(
        "Press to Download",
        combined_program_df.to_csv().encode("utf-8"),
        f"weekly_program_counts.csv",
        "text/csv",
        key="download-weekly-program",
    )


st.header("Figures to create")
components.iframe(
    "https://app.flipsidecrypto.com/dashboard/spireee-wip-NKWJbS",
    height=1800,
    scrolling=True,
)
