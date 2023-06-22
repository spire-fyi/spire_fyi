import datetime

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from st_pages import _get_page_hiding_code
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
token_name_dict = {x[1]: x[0] for x in utils.liquid_staking_tokens.values()}

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
n_addresses = c2.slider("Number of top addresses per day", 1, 50, 15, key="stakers_slider")
exclude_foundation = c3.checkbox(
    "Exclude Solana Foundation delegation", value=True, key="stakers_foundation_check"
)
exclude_labeled = c3.checkbox("Exclude labeled addresses", value=True, key="stakers_labeled_check")
log_scale = c3.checkbox("Log Scale", key="stakers_log_scale")

user_type_dict = {
    "top_stakers": f"Holdings by top {n_addresses} stakers",
    "top_holders": f"Top {n_addresses} liquid staking token holders",
}
lst_user_type = c1.radio(
    "Liquid Staking Token User Type",
    user_type_dict.keys(),
    format_func=lambda x: user_type_dict[x],
    key="lst_user_type",
)
lst = c2.selectbox(
    "Choose a Liquid Staking Token",
    token_name_dict.keys(),
    # format_func=lambda x: f"{x} ({token_name_dict[x]})", # Not really useful
    key="lst_token_select",
)

staker_chart_df, token_chart_df = utils.get_stakers_chart_data(
    staker_df, date_range, exclude_foundation, exclude_labeled, n_addresses, lst_user_type, lst
)
chart = charts.alt_line_chart(
    staker_chart_df,
    "Total Stake",
    legend_title="Staker Address",
    interactive=False,
    chart_title="Top stakers",
    log_scale=log_scale,
)
st.altair_chart(chart, use_container_width=True)
if len(token_chart_df) == 0:
    st.write("**Liquid Staking Token Holdings**: Selected addresses do not hold LSTs in this date range")
else:
    if lst_user_type == "top_stakers":
        chart_title = f"Holdings by top {n_addresses} stakers: {lst}"
    elif lst_user_type == "top_holders":
        chart_title = f"Top {n_addresses} liquid staking token holders among all top stakers: {lst}"
    chart = charts.alt_line_chart(
        token_chart_df,
        "Amount",
        legend_title="Holder address",
        interactive=False,
        chart_title=chart_title,
        log_scale=log_scale,
        unique_column_name="Name",
    )
    st.altair_chart(chart, use_container_width=True)

with st.expander("View and Download Data Table"):
    st.subheader("Staker info")
    st.write(staker_chart_df)
    slug = f"top_stakers"
    st.download_button(
        "Click to Download",
        staker_chart_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
        )
    st.write('---')
    st.subheader("Liquid staking token holder info")
    st.write(token_chart_df)
    slug = f"lst_holders"
    st.download_button(
        "Click to Download",
        token_chart_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
        )
    st.write('---')
    st.subheader("All data")
    slug = f"all_top_stakers"
    st.download_button(
        "Click to Download",
        staker_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
        )

lst_delta_df = utils.load_lst(filled=False)
# c1,c2 = st.columns(2)


# lst_chart_df =

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
# chart_copy['Date'] = max_date
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

# TOTAL STAKE VOLUME OVER TIME
daily_stake = staker_df.drop_duplicates(subset=['Date', 'Address'], keep='first')
daily_stake['Address Name'] = daily_stake['Address Name'].fillna('Other')
daily_stake = daily_stake.groupby(['Date', 'Address Name']).sum('Total Stake').reset_index()
daily_stake = daily_stake[(daily_stake['Date'] >= '2022-11-24')]

# selection = alt.selection_multi(fields=['Address Name'], bind='legend')
# chart = alt.Chart(daily_stake).mark_area(opacity=0.3).encode(
#     x="Date:T",
#     y=alt.Y("Total Stake:Q").stack(True),
#     color= alt.Color('Address Name:N', scale=alt.Scale(domain=daily_stake['Address Name'].unique().tolist())),
#     opacity=alt.condition(selection, alt.value(0.5), alt.value(0.1)
#     )
# ).add_selection(
#     selection
# ).transform_filter(
#     selection
# )
# st.altair_chart(chart, use_container_width=True)
fig2 = px.area(daily_stake, x='Date', y='Total Stake', color = 'Address Name', title = 'Stake Volume Over time'
, color_discrete_sequence=px.colors.qualitative.Prism)
fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=True)
fig2.update_xaxes(title_text='Date')
fig2.update_yaxes(title_text='Stake Volume')
st.plotly_chart(fig2, use_container_width=True)
# END --- TOTAL STAKE VOLUME OVER TIME

# TOP 15 STAKERS
filter = staker_df['Date'] == staker_df['Date'].max()
top_staker = staker_df.where(filter).dropna(subset=['Date'])
top_staker = top_staker.drop_duplicates(subset=['Date', 'Address'], keep='first')
if exclude_foundation:
    top_staker = top_staker[top_staker["Address Name"] != "Solana Foundation Delegation Account"]
if exclude_labeled:
    top_staker = top_staker[(top_staker["Address Name"].isna()) & (top_staker["Friendlyname"].isna())]
top_staker = top_staker.nlargest(15,'Total Stake')
# st.write(top_staker)
fig2 = px.histogram(top_staker, x='Address', y='Total Stake', log_y= False,
            title='Top 15 Staker by Volume', color='Address', color_discrete_sequence=px.colors.qualitative.Prism)
fig2.update_layout(xaxis_title='Staked Volume',
                yaxis_title='Address')

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

filter = staker_df['Date'] == staker_df['Date'].max()
stake_category = staker_df.where(filter).dropna(subset=['Date'])
stake_category['stake_category'] = stake_category['Total Stake'].apply(get_stake_volume_category)
stake_cateogry_count_df = stake_category.groupby(['stake_category']).agg(TOTAL_ADDRESS=('Address', 'nunique')).reset_index()
# st.write(stake_cateogry_count_df)
fig2 = px.histogram(stake_cateogry_count_df, x='stake_category', y='TOTAL_ADDRESS', log_y= False,
            title='Stake Category by Volume', color='stake_category', color_discrete_sequence=px.colors.qualitative.Prism)
fig2.update_layout(xaxis_title='Staked Volume',
                yaxis_title='Wallet Count')

fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=True)
st.plotly_chart(fig2, use_container_width=True)
# END --- STAKE VOLUME CATEGORY

# LSDs Holding Over time
LSD_df = staker_df.groupby(['Date', 'Symbol']).sum('amount').reset_index()
fig2 = px.area(LSD_df, x='Date', y='Amount', color = 'Symbol', title = 'Total LSDs Holding by Top SOL Stakers'
, color_discrete_sequence=px.colors.qualitative.Prism)
fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=True)
fig2.update_xaxes(title_text='Date')
fig2.update_yaxes(title_text='Total LSD Holding Balance')
st.plotly_chart(fig2, use_container_width=True)
# END --- LSDs Holding Over time

# LSDs Current Balance and Holders
filter = staker_df['Date'] == staker_df['Date'].max()
LSDs_curr = staker_df.where(filter).dropna(subset=['Date'])
LSDs_curr = LSDs_curr.where(LSDs_curr['Amount'] > 0)
LSDs_curr = LSDs_curr.groupby("Symbol").agg(
    {"Amount": np.sum, "Address": pd.Series.nunique}).reset_index()
LSDs_curr = LSDs_curr.sort_values(by=["Amount"], ascending=False)
fig = go.Figure(
    data=go.Bar(
        x=LSDs_curr['Symbol'],
        y=LSDs_curr['Amount'],
        name="LSD Balance",
        marker=dict(color='teal')
    )
)
fig.add_trace(
    go.Scatter(
        x=LSDs_curr['Symbol'],
        y=LSDs_curr['Address'],
        yaxis="y2",
        name="Holder",
        marker=dict(color="crimson"),
    )
)
fig.update_layout(
    
    title="Current LSDs Balance/Holders from Top Stakers",
    legend=dict(orientation="h"),
    yaxis=dict(
        title=dict(text="LSD Balance"),
        side="left"
    ),
    yaxis2=dict(
        title=dict(text="Holder"),
        side="right",
        overlaying="y",
        tickmode="sync",
    ),
)
st.plotly_chart(fig , use_container_width=True)
# END -- LSDs Current Balance and Holders
