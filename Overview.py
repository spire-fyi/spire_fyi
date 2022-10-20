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

st.write(
    f"""A view from the top of the tower.
    See the [In Depth](In_Depth) or topic-specific pages for more details.
    """
)

st.subheader("Programs")

weekly_program_data = utils.load_weekly_program_data()
weekly_new_program_data = utils.load_weekly_new_program_data()
weekly_user_data = utils.load_weekly_program_data()

c1, c2 = st.columns(2)
chart = (
    alt.Chart(weekly_program_data, title="Unique Programs Used: Weekly")
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
            alt.Tooltip(
                "yearmonthdate(WEEK)",
                title="Date (start of week)",
            ),
            alt.Tooltip("UNIQUE_PROGRAMS", title="Number of Programs", format=","),
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
        alt.Tooltip("New Programs", format=","),
        alt.Tooltip("Cumulative Programs", format=","),
    ],
)
bar = base.mark_bar(width=3, color="#4B3D60").encode(
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

st.subheader("Users")
c1, c2 = st.columns(2)
weekly_user_data = utils.load_weekly_user_data()
weekly_user_last_user = utils.load_weekly_days_since_last_use_data()

chart = (
    alt.Chart(weekly_user_data, title="New Wallets: Weekly")
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
        x=alt.X("yearmonthdate(CREATION_DATE)", title="Date"),
        y=alt.Y("ADDRESS", title="Number of New Wallets"),
        tooltip=[
            alt.Tooltip("yearmonthdate(CREATION_DATE)", title="Date (start of week)"),
            alt.Tooltip("ADDRESS", title="Number of New Wallets"),
        ],
    )
    .interactive()
    .properties(height=600, width=800)
)
c1.altair_chart(chart, use_container_width=True)
base = alt.Chart(weekly_user_last_user, title="New Programs: Weekly").encode(
    x=alt.X("yearmonthdate(CREATION_DATE):T", title="Date"),
    tooltip=[
        alt.Tooltip("yearmonthdate(CREATION_DATE):T", title="Date (start of week)"),
        alt.Tooltip("Days since last use", title="Average days since last use", format='.0f'),
        alt.Tooltip("Days since creation", title="Days since creation", format='.0f'),
    ],
)
bar = base.mark_bar(width=3, color="#4B3D60").encode(
    y=alt.Y("Days since last use"),
)
line = base.mark_line(color="#FFE373").encode(
    y="Days since creation",
)
chart = (bar + line).interactive().properties(height=600,width=800)
c2.altair_chart(chart, use_container_width=True)
st.header("Figures to create")
components.iframe(
    "https://app.flipsidecrypto.com/dashboard/spireee-wip-NKWJbS",
    height=1800,
    scrolling=True,
)
