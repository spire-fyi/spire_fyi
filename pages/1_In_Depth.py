import streamlit as st
import altair as alt
import pandas as pd
from PIL import Image

import spire_fyi.utils as utils
import spire_fyi.charts as charts

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
st.header("In Depth")

st.subheader("Program Analysis")
df = utils.load_labeled_program_data()
df["Date"] = pd.to_datetime(df["Date"])

# #TODO: implement program search
# chart_type = st.radio("Choose how to view data", ['Top Programs', 'Select Programs'], horizontal=True, key='program_chart_type')
# if chart_type == 'Top Programs':
# ...
# else:
#     selections = st.multiselect("Choose which Programs to look at", df.PROGRAM_ID.unique())
# #---
c1, c2, c3, c4 = st.columns(4)
metric = c1.radio(
    "Choose a metric",
    utils.metric_dict.keys(),
    format_func=lambda x: utils.metric_dict[x],
    horizontal=True,
    key="program_metric",
)
num_programs = c2.slider("Number of Programs", 1, 25, 10, key="program_slider")
agg_method = c3.radio(
    "Choose an aggregtion method",
    utils.agg_method_dict.keys(),
    format_func=lambda x: utils.agg_method_dict[x],
    horizontal=True,
    key="program_agg_method",
)
exclude_solana = c4.checkbox("Exclude Solana System Programs?", key="program_exclude_solana")
log_scale = c4.checkbox("Log Scale?", key="program_log_scale")
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

chart_df = utils.get_program_chart_data(df, metric, num_programs, agg_method, date_range, exclude_solana)
chart_df["Name"] = chart_df.apply(
    utils.apply_program_name,
    axis=1,
)

chart = charts.alt_line_chart(chart_df, metric,log_scale)
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

