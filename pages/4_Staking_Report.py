import datetime

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from st_pages import _get_page_hiding_code

import spire_fyi.charts as charts
import spire_fyi.utils as utils

alt.data_transformers.disable_max_rows()
image = Image.open("assets/images/spire_logo.png")

st.set_page_config(
    page_title="Spire: Staking Report",
    page_icon=image,
    layout="wide",
)
st.write(
    _get_page_hiding_code(st.secrets["hide_pages"]["pages_to_hide"]),
    unsafe_allow_html=True,
)
c1, c2 = st.columns([1, 3])

c2.header("Spire")
c2.caption(
    """
    A viewpoint above Solana data. Insights and on-chain data analytics, inspired by the community and accessible to all. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/), [Helius](https://helius.xyz/), [SolanaFM](https://docs.solana.fm/) and [HowRare](https://howrare.is/api).

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi) | Donations: GvvrKbq21eTkknHRt9FGVFN54pLWXSSo4D4hz2i1JCn5 , or contribute on [Stockpile](https://www.stockpile.pro/projects/fMqAvbsrWseJji8QyNOf)
    """
)
c1.image(
    image,
    width=100,
)
st.write("---")
st.header("Staking Report (Guest Analysis)")
st.write(
    """
Exploring SOL stakers and liquid staking token holders.
    
Analysis performed by [@h4wk10](https://twitter.com/h4wk10), [@banbannard](https://twitter.com/banbannard) and the Spire Team.
    """
)

staker_df = utils.load_staker_data()
st.write(staker_df)

c1, c2, c3 = st.columns([3, 2, 2])
date_range = c1.radio(
    "Choose a date range:",
    [  # #TODO: not doing more dates until more data is queried
        # "All dates",
        # "Year to Date",
        "180d",
        "90d",
        "60d",
        "30d",
        "14d",
        "7d",
    ],
    horizontal=True,
    index=3,
    key="stakers_date_range",
)
n_stakers = c2.slider("Top Stakers per day", 1, 50, 15, key="stakers_slider")
exclude_foundation = c3.checkbox(
    "Exclude Solana Foundation delegation", value=True, key="stakers_foundation_check"
)
exclude_labeled = c3.checkbox("Exclude labeled addresses", value=False, key="stakers_labeled_check")
log_scale = c3.checkbox("Log Scale", key="stakers_log_scale")

chart_df = utils.get_stakers_chart_data(staker_df, date_range, exclude_foundation, exclude_labeled, n_stakers)
st.write(chart_df)

chart = charts.alt_line_chart(chart_df, "Total Stake", legend_title="Staker", interactive=False)
st.altair_chart(chart.properties(height=1000), use_container_width=True)

st.header("Liquid staking tokens")

# lst_filled_df = utils.load_lst()
lst_delta_df = utils.load_lst(filled=False)

# st.subheader("Filled")
# st.write(lst_filled_df)

st.subheader("Delta")
st.write(lst_delta_df)
st.write("---")
c1, c2, c3 = st.columns([3, 2, 2])
date_range = c1.radio(
    "Choose a date range:",
    [  # #TODO: not doing more dates until more data is queried
        # "All dates",
        # "Year to Date",
        "180d",
        "90d",
        "60d",
        "30d",
        "14d",
        "7d",
    ],
    horizontal=True,
    index=3,
    key="lst_date_range",
)
lst = c2.selectbox("Choose a token", staker_df["Token Name"].dropna().unique(), key="lst_token_select")
# n_stakers = c2.slider("Top Stakers per day", 1, 50, 15, key="lst_slider")
# exclude_foundation = c3.checkbox(
#     "Exclude Solana Foundation delegation", value=True, key="lst_foundation_check"
# )
# exclude_labeled = c3.checkbox("Exclude labeled addresses", value=False, key="lst_labeled_check")
# log_scale = c3.checkbox("Log Scale", key="lst_log_scale")

# #TODO: re-add the user input features, include token dropdown
# #TODO: need price tables to get accurate value amounts in filled table, as well LST:SOL exchange rate to see total amount of staked sol
chart_df = staker_df.copy()[
    (staker_df.Date >= (datetime.datetime.today() - pd.Timedelta(date_range)))
    & (staker_df["Token Name"] == lst)
]
chart_df = (
    chart_df[chart_df.Amount > 1]
    .sort_values("Amount", ascending=False)
    .groupby(["Date", "Address", "Token"], as_index=False)
    .head(15)
    .sort_values(by=["Address", "Date"], ascending=False)
    .reset_index(drop=True)
)
# max_date = chart_df.Date.max()
# results = []
# for x in chart_df.Wallet.unique():
#     df = chart_df[chart_df.Wallet == x]
#     for y in df.Token.unique():
#         results.append(df[df.Token == y].Date.idxmax())
# chart_copy = chart_df.iloc[results].copy()
# chart_copy['Date'] = max_date
# chart_df = pd.concat([chart_df, chart_copy])

st.write(chart_df)
chart = (
    (
        alt.Chart(chart_df)
        .mark_line()
        .encode(
            x=alt.X("yearmonthdate(Date)", title="Date"),
            y=alt.Y("Amount"),
            color=alt.Color("Address"),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Address"),
                alt.Tooltip("Amount", format=".2f"),
            ],
        )
    )
    .properties(height=600)
    .interactive()
)
st.altair_chart(chart, use_container_width=True)
