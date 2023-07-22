import datetime

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from plotly.subplots import make_subplots
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

with st.expander("Instructions"):
    st.write(
        """
- Liquid Staking Tokens are abbreviated as LSTs. These include popular tokens which represent staked SOL, such as mSOL, stSOL, bSOL and others.
- Use the [Settings](#settings) to filter the data used to chart Top Stakers and Liquid Staking Token Holders.
  - Date range: The date range to use for the charts.
  - Number of top addresses per day: The top addresses each day will be shown; there may be more addresses shown in the chart than this number, as the union of all top addresses is used.
  - Exclude Solana Foundation delegation: The Solana Foundation has a large delegation which can be ignored for this analysis.
  - Exclude labeled addresses: this removes known addresses, such as exchanges, from the analysis.
  - Log Scale: Use a log scale for the y-axis.
  - Choose a Liquid Staking Token: Choose which LST to focus anakys
- Data Description:
    - Data was queried using the [Flipside Crypto](https://flipsidecrypto.xyz/) API with these queries:
        - [Top SOL stakers](https://github.com/spire-fyi/spire_fyi/tree/main/sql/sdk_top_stakers_by_date_sol.sql)
        - [LST holdings ampng top stakers](https://github.com/spire-fyi/spire_fyi/tree/main/sql/sdk_top_liquid_staking_token_holders_delta.sql)
        - [Program interactions by top stakers](https://flipsidecrypto.xyz/edit/queries/2cc62d89-4f67-4197-82cf-8daf9b69ff45)
"""
    )

staker_df = utils.load_staker_data()
staker_interaction_df = utils.load_staker_interaction_data()
token_name_dict = {x[1]: x[0] for x in utils.liquid_staking_tokens.values()}

st.subheader("Settings")
st.write("Use the settings below to filter the data for Top Stakers and Liquid Staking Token Holders.")
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
    index=1,
    key="stakers_date_range",
)
n_addresses = c2.slider("Number of top addresses per day", 1, 50, 15, key="stakers_slider")
exclude_foundation = c3.checkbox(
    "Exclude Solana Foundation delegation", value=True, key="stakers_foundation_check"
)
exclude_labeled = c3.checkbox("Exclude labeled addresses", key="stakers_labeled_check")
log_scale = c3.checkbox("Log Scale", key="stakers_log_scale")

user_type_dict = {
    "top_stakers": f"Holdings by top {n_addresses} stakers",
    "top_holders": f"Top {n_addresses} liquid staking token holders",
}
# lst_user_type = c1.radio(
#     "Liquid Staking Token User Type",
#     user_type_dict.keys(),
#     format_func=lambda x: user_type_dict[x],
#     key="lst_user_type",
# )
lst = c2.selectbox(
    "Choose a Liquid Staking Token",
    token_name_dict.keys(),
    # format_func=lambda x: f"{x} ({token_name_dict[x]})", # Not really useful
    key="lst_token_select",
)

staker_chart_df, token_top_stakers_df, token_top_holders_df = utils.get_stakers_chart_data(
    staker_df, date_range, exclude_foundation, exclude_labeled, n_addresses, lst
)

st.subheader("Top Stakers")
chart = charts.alt_line_chart(
    staker_chart_df,
    "Total Stake",
    legend_title="Staker Address",
    interactive=False,
    chart_title="Top stakers",
    log_scale=log_scale,
)
st.altair_chart(chart, use_container_width=True)

st.subheader(f"Liquid Staking Token Holders from Top SOL Stakers")
if len(token_top_stakers_df) == 0:
    st.write(f"**Liquid Staking Token Holdings**: The selected addresses do not hold {lst} in this date range")
else:
    chart_title_top_stakers = f"Holdings by top {n_addresses} stakers: {lst}"
    chart = charts.alt_line_chart(
        token_top_stakers_df,
        "Amount",
        legend_title="Holder address",
        interactive=False,
        chart_title=chart_title_top_stakers,
        log_scale=log_scale,
        unique_column_name="Name",
    )
    st.altair_chart(chart, use_container_width=True)
st.write("---")
st.subheader(f"Top LST Holders among Top SOL Stakers")
chart_title_top_holders = f"Top {n_addresses} liquid staking token holders among all top stakers: {lst}"
chart = charts.alt_line_chart(
    token_top_holders_df,
    "Amount",
    legend_title="Holder address",
    interactive=False,
    chart_title=chart_title_top_holders,
    log_scale=log_scale,
    unique_column_name="Name",
)
st.altair_chart(chart, use_container_width=True)
# #TODO: look at Delta, add some overviews
# lst_delta_df = utils.load_lst(filled=False)
# c1,c2 = st.columns(2)
# name: symbol pairs


# st.subheader("Delta")
# st.write(lst_delta_df)
# st.write("---")
# c1, c2, c3 = st.columns([3, 2, 2])
# date_range = c1.radio(
#     "Choose a date range:",
#     [  # #TODO: not doing more dates until more data is queried
#         # "All dates",
#         # "Year to Date",
#         "180d",
#         "90d",
#         "60d",
#         "30d",
#         "14d",
#         "7d",
#     ],
#     horizontal=True,
#     index=3,
#     key="lst_date_range",
# )

# n_stakers = c2.slider("Top Stakers per day", 1, 50, 15, key="lst_slider")
# exclude_foundation = c3.checkbox(
#     "Exclude Solana Foundation delegation", value=True, key="lst_foundation_check"
# )
# exclude_labeled = c3.checkbox("Exclude labeled addresses", value=False, key="lst_labeled_check")
# log_scale = c3.checkbox("Log Scale", key="lst_log_scale")

# #TODO: re-add the user input features, include token dropdown
# #TODO: need price tables to get accurate value amounts in filled table, as well LST:SOL exchange rate to see total amount of staked sol
# chart_df = staker_df.copy()[
#     (staker_df.Date >= (datetime.datetime.today() - pd.Timedelta(date_range)))
#     & (staker_df["Token Name"] == lst)
# ]
# chart_df = (
#     chart_df[chart_df.Amount > 1]
#     .sort_values("Amount", ascending=False)
#     .groupby(["Date", "Address", "Token"], as_index=False)
#     .head(15)
#     .sort_values(by=["Address", "Date"], ascending=False)
#     .reset_index(drop=True)
# )
# max_date = chart_df.Date.max()
# results = []
# for x in chart_df.Wallet.unique():
#     df = chart_df[chart_df.Wallet == x]
#     for y in df.Token.unique():
#         results.append(df[df.Token == y].Date.idxmax())
# chart_copy = chart_df.iloc[results].copy()
# chart_copy["Date"] = max_date
# chart_df = pd.concat([chart_df, chart_copy])

# chart = (
#     (
#         alt.Chart(chart_df)
#         .mark_line()
#         .encode(
#             x=alt.X("yearmonthdate(Date)", title="Date"),
#             y=alt.Y("Amount"),
#             color=alt.Color("Address"),
#             tooltip=[
#                 alt.Tooltip("yearmonthdate(Date)", title="Date"),
#                 alt.Tooltip("Address"),
#                 alt.Tooltip("Amount", format=".2f"),
#             ],
#         )
#     )
#     .properties(height=600)
#     .interactive()
# )
# st.altair_chart(chart, use_container_width=True)

# Guest analysis by h4wk
st.subheader("Summary")
st.write("The [Settings](#settings) do **not** apply to the charts below.")
# TOTAL STAKE OVER TIME
c1, c2 = st.columns(2)
daily_stake = staker_df.drop_duplicates(subset=["Date", "Address"], keep="first")
daily_stake["Address Name"] = daily_stake["Address Name"].fillna("Other")
daily_stake = daily_stake.groupby(["Date", "Address Name"])["Total Stake"].sum().reset_index()
daily_stake = daily_stake[(daily_stake["Date"] >= "2022-11-24")]
fig2 = px.area(
    daily_stake,
    x="Date",
    y="Total Stake",
    color="Address Name",
    title="Total Stake Over time",
    color_discrete_sequence=px.colors.qualitative.Prism,
)
fig2.update_xaxes(title_text="Date", showgrid=False)
fig2.update_yaxes(title_text="Total Stake (SOL)", showgrid=True)
st.plotly_chart(fig2, use_container_width=True)
# END --- TOTAL STAKE OVER TIME
# LSTs Holding Over time
LST_df = staker_df.groupby(["Date", "Symbol"])["Amount"].sum().reset_index()
fig2 = px.area(
    LST_df,
    x="Date",
    y="Amount",
    color="Symbol",
    title="Total LST Balance by Top SOL Stakers",
    color_discrete_sequence=px.colors.qualitative.Prism_r,
)
fig2.update_xaxes(title_text="Date", showgrid=False)
fig2.update_yaxes(title_text="Total LST Balance", showgrid=True)
st.plotly_chart(fig2, use_container_width=True)
# END --- LSTs Holding Over timeload_staker


# TOP 15 STAKERS
filter = staker_df["Date"] == staker_df["Date"].max()
top_staker = staker_df.where(filter).dropna(subset=["Date"])
top_staker = top_staker.drop_duplicates(subset=["Date", "Address"], keep="first")
if exclude_foundation:
    top_staker = top_staker[top_staker["Address Name"] != "Solana Foundation Delegation Account"]
if exclude_labeled:
    top_staker = top_staker[(top_staker["Address Name"].isna()) & (top_staker["Friendlyname"].isna())]
top_staker = top_staker.nlargest(n_addresses, "Total Stake")
# st.write(top_staker)
fig2 = px.histogram(
    top_staker,
    x="Address",
    y="Total Stake",
    title=f"Top {n_addresses} Stakers by Stake Amount",
    color="Address",
    color_discrete_sequence=px.colors.qualitative.Prism,
)
fig2.update_layout(xaxis_title="Address", yaxis_title="Total Stake (SOL)")

fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=True)
st.plotly_chart(fig2, use_container_width=True)
# END --- TOP 15 STAKERS


# STAKE VOLUME CATEGORY
def get_stake_volume_category(stake_volume):
    if stake_volume < 1000:
        return "Stake < 1k SOL"
    elif stake_volume < 10000:
        return "a. 1k < Stake < 10k SOL"
    elif stake_volume < 100000:
        return "b. 10k < Stake < 100k SOL"
    elif stake_volume < 1000000:
        return "c. 100k < Stake < 1m SOL"
    else:
        return "d. Stake > 1m SOL"


filter = staker_df["Date"] == staker_df["Date"].max()
stake_category = staker_df.where(filter).dropna(subset=["Date"])
stake_category["Stake Category"] = stake_category["Total Stake"].apply(get_stake_volume_category)
stake_cateogry_count_df = (
    stake_category.groupby(["Stake Category"]).agg(TOTAL_ADDRESS=("Address", "nunique")).reset_index()
)
# st.write(stake_cateogry_count_df)
fig2 = px.histogram(
    stake_cateogry_count_df,
    x="Stake Category",
    y="TOTAL_ADDRESS",
    log_y=False,
    title="Top Stakers by Staking Amount Category",
    color="Stake Category",
    color_discrete_sequence=px.colors.qualitative.Prism,
)
fig2.update_layout(xaxis_title="Total Stake (SOL)", yaxis_title="Addresss Count")

fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=True)
st.plotly_chart(fig2, use_container_width=True)
# END --- STAKE VOLUME CATEGORY

# LSTs Current Balance and Holders
filter = staker_df["Date"] == staker_df["Date"].max()
LSTs_curr = staker_df.where(filter).dropna(subset=["Date"])
LSTs_curr = LSTs_curr.where(LSTs_curr["Amount"] > 0)
LSTs_curr = LSTs_curr.groupby("Symbol").agg({"Amount": np.sum, "Address": pd.Series.nunique}).reset_index()
LSTs_curr = LSTs_curr.sort_values(by=["Amount"], ascending=False)
fig = go.Figure(
    data=go.Bar(x=LSTs_curr["Symbol"], y=LSTs_curr["Amount"], name="LST Balance", marker=dict(color="teal"))
)
fig.add_trace(
    go.Scatter(
        x=LSTs_curr["Symbol"],
        y=LSTs_curr["Address"],
        yaxis="y2",
        name="Holder",
        marker=dict(color="crimson"),
    )
)
fig.update_layout(
    title="Current LST Holding Balance and Holders from Top SOL Stakers",
    legend=dict(orientation="h"),
    yaxis=dict(title=dict(text="LST Balance"), side="left"),
    yaxis2=dict(
        title=dict(text="Holder"),
        side="right",
        overlaying="y",
        # tickmode="sync",
    ),
)
fig.update_yaxes(showgrid=False)
st.plotly_chart(fig, use_container_width=True)
# END --- LSTs Current Balance and Holders

# Protocol Interaction Total
staker_interaction_df = staker_interaction_df.rename(columns={"Cap Label": "Protocol"})
staker_interaction_df = (
    staker_interaction_df.groupby("Protocol")
    .agg({"Interact": np.sum, "Address": pd.Series.nunique})
    .reset_index()
)
staker_interaction_df = staker_interaction_df.sort_values(by="Interact", ascending=False)

fig = go.Figure(
    data=go.Bar(
        x=staker_interaction_df["Protocol"],
        y=staker_interaction_df["Interact"],
        name="Program interactions",
        marker=dict(color=px.colors.qualitative.Prism[0]),
    )
)
fig.add_trace(
    go.Scatter(
        x=staker_interaction_df["Protocol"],
        y=staker_interaction_df["Address"],
        yaxis="y2",
        name="Stakers",
        marker=dict(color="orange"),
    )
)
fig.update_layout(
    title="Program Usage by Top Stakers, Past 90d",
    # legend=dict(orientation="h"),
    yaxis=dict(title=dict(text="Program Interactions"), side="left", type="log"),
    yaxis2=dict(
        title=dict(text="Addresses"),
        side="right",
        overlaying="y",
        # tickmode="sync",
    ),
)
fig.update_yaxes(showgrid=False)
st.plotly_chart(fig, use_container_width=True)
st.caption("Note: Only interactions with a subset of labeled program addresses are counted")

# END --- Protocol Interaction Total

# view and download data tables
with st.expander("View and Download Data Table"):
    st.subheader("Top Staker info")
    st.write("View the data shown in the [Top Stakers](#top-stakers) chart above.")
    st.write(staker_chart_df)
    slug = f"top_stakers"
    st.download_button(
        "Click to Download",
        staker_chart_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("---")
    st.subheader("Liquid Staking Token Holders from Top SOL Stakers")
    if len(token_top_stakers_df) == 0:
        st.write(f"**Liquid Staking Token Holdings**: The selected addresses do not hold {lst} in this date range")
    else:
        st.write(token_top_stakers_df)
        st.write("View the data shown in the [Liquid Staking Token Holders from Top SOL Stakers](#liquid-staking-token-holders-from-top-sol-stakers) chart above.")
        slug = f"lst_holders_top_stakers"
        st.download_button(
            "Click to Download",
            token_top_stakers_df.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
    st.write("---")
    st.subheader("Top LST Holders among Top SOL Stakers")
    st.write("View the data shown in the [Top LST Holders among Top SOL Stakers](#top-lst-holders-among-top-sol-stakers) chart above.")
    st.write(token_top_holders_df)
    slug = f"lst_holders_top_holders"
    st.download_button(
        "Click to Download",
        token_top_holders_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("---")
    st.subheader("All data")
    st.write("Download raw data for Top SOL Stakers (unfiltered by anything selected in [Settings](#settings))")
    slug=f"all_staker_lst_data"
    st.download_button(
        "Click to Download",
        staker_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
