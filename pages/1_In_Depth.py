import streamlit as st
import altair as alt
import pandas as pd
from PIL import Image

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
st.header("In Depth")

st.subheader("Program Analysis")
df = utils.load_labeled_program_data()
df["Date"] = pd.to_datetime(df["Date"])

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

chart = (
    alt.Chart(chart_df)
    .mark_line()
    .encode(
        x=alt.X("yearmonthdatehours(Date)", title=None),
        y=alt.Y(metric, title=utils.metric_dict[metric], sort="-y"),
        color=alt.Color(
            "Name",
            title="Program Name",
            scale=alt.Scale(scheme="turbo"),
            sort=alt.EncodingSortField(metric, op=agg_method, order="descending"),
        ),
        tooltip=[
            alt.Tooltip("yearmonthdatehours(Date)", title="Date"),
            alt.Tooltip("TX_COUNT", title=utils.metric_dict["TX_COUNT"], format=","),
            alt.Tooltip("SIGNERS", title=utils.metric_dict["SIGNERS"], format=","),
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
