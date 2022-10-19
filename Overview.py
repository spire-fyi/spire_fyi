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




st.header("Programs")
st.write('See the [In Depth](In_Depth) page for more details.')
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
