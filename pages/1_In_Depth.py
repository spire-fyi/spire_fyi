import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

import spire_fyi.charts as charts
import spire_fyi.utils as utils

alt.data_transformers.disable_max_rows()
image = Image.open("assets/images/spire_background.png")

st.set_page_config(
    page_title="Spire",
    page_icon=image,
    layout="wide",
)
c1, c2 = st.columns([1, 3])

c2.header("Spire")
c2.caption("A viewpoint above Solana data. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/).")
c1.image(
    image,
    width=200,
)
st.write("---")
st.header("In Depth")

st.subheader("Program Analysis")
c1, c2, c3, c4 = st.columns(4)
metric = c1.radio(
    "Choose a metric",
    utils.metric_dict.keys(),
    format_func=lambda x: utils.metric_dict[x],
    horizontal=True,
    key="program_metric",
)
agg_method = c2.radio(
    "Choose an aggregtion method",
    utils.agg_method_dict.keys(),
    format_func=lambda x: utils.agg_method_dict[x],
    horizontal=True,
    key="program_agg_method",
)
chart_type = c3.radio(
    "Choose how to view data",
    ["Top Programs", "Selected Programs"],
    horizontal=True,
    key="program_chart_type",
)
new_users_only = c4.checkbox("New Users Only?", key="program_new_users")
exclude_solana = c4.checkbox("Exclude Solana System Programs?", key="program_exclude_solana")
log_scale = c4.checkbox("Log Scale?", key="program_log_scale")
st.write("---")
df = utils.load_labeled_program_data(new_users_only=new_users_only)
df["Date"] = pd.to_datetime(df["Date"])
c1, c2 = st.columns(2)
date_range = c1.radio(
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
if chart_type == "Top Programs":
    programs = c2.slider("Number of Programs", 1, 30, 10, key="program_slider")
else:
    programs = c2.multiselect(
        "Choose which Program IDs to look at (random selections chosen)",
        df.PROGRAM_ID.unique(),
        key="program_multiselect",
    )
    if not programs:
        programs = np.random.choice(df.PROGRAM_ID.unique(), 5)

chart_df = utils.get_program_chart_data(df, metric, agg_method, date_range, exclude_solana, programs)
chart_df["Name"] = chart_df.apply(
    utils.apply_program_name,
    axis=1,
)
chart_df["Explorer Site"] = chart_df.PROGRAM_ID.apply(lambda x: f"https://solana.fm/address/{x}")

chart = charts.alt_line_chart(chart_df, metric, log_scale)
st.altair_chart(chart, use_container_width=True)

with st.expander("View and Download Data Table"):
    chart_df = (
        chart_df[
            [
                "Date",
                "Name",
                "TX_COUNT",
                "SIGNERS",
                "PROGRAM_ID",
                "LABEL_TYPE",
                "LABEL_SUBTYPE",
                "LABEL",
                "ADDRESS_NAME",
                "FriendlyName",
                "Abbreviation",
                "Category",
                "LogoURI",
                "Explorer Site",
            ]
        ]
        .sort_values(by=["Date", metric], ascending=False)
        .rename(
            columns={
                "PROGRAM_ID": "Program ID",
                "TX_COUNT": "Transaction Count",
                "SIGNERS": "Signer Count",
                "LABEL_TYPE": "Flipside Label Type",
                "LABEL_SUBTYPE": "Flipside Label Subtype",
                "LABEL": "Flipside Label",
                "ADDRESS_NAME": "Flipside Address Name",
                "FriendlyName": "SolanaFM Address Name",
                "Abbreviation": "SolanaFM Abbreviation",
                "Category": "SolanaFM Category",
            }
        )
        .reset_index(drop=True)
    )
    st.write(chart_df)
    if type(programs) == int:
        chart_type_str = f"top{programs}"
    else:
        chart_type_str = "selected"
    if new_users_only:
        chart_type_str += "_new_users"
    st.download_button(
        "Click to Download",
        chart_df.to_csv(index=False).encode("utf-8"),
        f"program_ids_{chart_type_str}_{agg_method}_{date_range.replace(' ', '')}_{metric}.csv",
        "text/csv",
        key="download-program-ids",
    )


# #TODO: days since last user
weekly_user_last_user = utils.load_weekly_days_since_last_use_data()
base = alt.Chart(weekly_user_last_user, title="New Programs: Weekly").encode(
    x=alt.X("yearmonthdate(CREATION_DATE):T", title="Date"),
    tooltip=[
        alt.Tooltip("yearmonthdate(CREATION_DATE):T", title="Date (start of week)"),
        alt.Tooltip("Days since last use", title="Average days since last use", format=".0f"),
        alt.Tooltip("Days since creation", title="Days since creation", format=".0f"),
    ],
)
bar = base.mark_bar(width=3, color="#4B3D60").encode(
    y=alt.Y("Days since last use"),
)
line = base.mark_line(color="#FFE373").encode(
    y="Days since creation",
)
chart = (bar + line).interactive().properties(height=600, width=800)
chart
