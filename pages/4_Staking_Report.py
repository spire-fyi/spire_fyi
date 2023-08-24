import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    A viewpoint above Solana data. Insights and on-chain data analytics, inspired by the community and accessible to all.
    Powered by [Flipside Crypto](https://flipsidecrypto.xyz/), [Helius](https://helius.xyz/),
    [SolanaFM](https://docs.solana.fm/) and [HowRare](https://howrare.is/api).

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi) |
    Donations: GvvrKbq21eTkknHRt9FGVFN54pLWXSSo4D4hz2i1JCn5 , or contribute on [Stockpile](https://www.stockpile.pro/projects/fMqAvbsrWseJji8QyNOf)
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
  - Number of top addresses per day: The top addresses each day will be shown; there may be more addresses shown in the chart than this number,
  as the union of all top addresses is used.
  - Exclude Solana Foundation delegation: The Solana Foundation has a large delegation which can be ignored for this analysis.
  - Exclude labeled addresses: this removes known addresses, such as exchanges, from the analysis.
  - Log Scale: Use a log scale for the y-axis.
  - Choose a Liquid Staking Token: Choose which LST to focus anakys
- Data Description:
    - Data was queried using the [Flipside Crypto](https://flipsidecrypto.xyz/) API with these queries:
        - [Top SOL stakers](https://github.com/spire-fyi/spire_fyi/tree/main/sql/sdk_top_stakers_by_date_sol.sql)
        - [LST holdings among top stakers](https://github.com/spire-fyi/spire_fyi/tree/main/sql/sdk_top_liquid_staking_token_holders_delta.sql)
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
n_addresses = c1.slider("Number of top addresses per day", 1, 50, 15, key="stakers_slider")
lst = c2.selectbox(
    "Choose a Liquid Staking Token",
    token_name_dict.keys(),
    # format_func=lambda x: f"{x} ({token_name_dict[x]})", # Not really useful
    key="lst_token_select",
)
interactive = c2.selectbox(
    "Turn on chart zooming/panning", [None, "both", "x-axis", "y-axis"], key="stakers_interactive"
)
normalize = c3.checkbox("Show proportions instead of Amounts", key="stakers_normalize")
keep_others = c3.checkbox(
    "Include `Other` addresses",
    value=True,
    key="stakers_keep_others",
)
exclude_foundation = c3.checkbox("Exclude Solana Foundation delegation", key="stakers_foundation_check")
exclude_labeled = c3.checkbox("Exclude labeled addresses", key="stakers_labeled_check")


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

lst_symbol = token_name_dict[lst]
staker_chart_df, token_top_stakers_df, token_top_holders_df = utils.get_stakers_chart_data(
    staker_df, date_range, exclude_foundation, exclude_labeled, n_addresses, lst, keep_others=keep_others
)

st.subheader("Top Stakers")
chart = charts.alt_stakers_chart(
    staker_chart_df,
    "Total Stake",
    "Total Stake",
    "Total Stake (SOL)",
    "Name",
    "Staker",
    lst_symbol,
    normalize=normalize,
    interactive=interactive,
)
st.altair_chart(chart, use_container_width=True)

st.subheader("Liquid Staking Token Holders from Top SOL Stakers")
if len(token_top_stakers_df) == 0:
    st.write(f"The selected addresses do not hold `{lst}` in this date range.")
else:
    chart_title_top_stakers = f"Holdings by top {n_addresses} stakers: {lst}"
    chart = charts.alt_stakers_chart(
        staker_chart_df,
        chart_title_top_stakers,
        "Amount",
        f"Amount: {lst}",
        "Name",
        "Holder address",
        lst_symbol,
        normalize=normalize,
        interactive=interactive,
    )
    st.altair_chart(chart, use_container_width=True)
st.write("---")
st.subheader("Top LST Holders among Top SOL Stakers")
if len(token_top_holders_df) == 0:
    st.write(f"None of the top SOL Stakers hold `{lst}` in this date range.")
else:
    chart_title_top_holders = f"Top {n_addresses} liquid staking token holders among all top stakers: {lst}"
    chart = charts.alt_stakers_chart(
        token_top_holders_df,
        chart_title_top_holders,
        "Amount",
        f"Amount: {lst}",
        "Name",
        "Holder address",
        lst_symbol,
        normalize=normalize,
        interactive=interactive,
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


# STAKE VOLUME CATEGORY
def get_stake_volume_category(stake_volume):
    if stake_volume < 5000:
        return "Stake < 5k SOL"
    elif stake_volume < 10000:
        return "a. 5k < Stake < 10k SOL"
    elif stake_volume < 50000:
        return "b. 10k < Stake < 50k SOL"
    elif stake_volume < 100000:
        return "c. 50k < Stake < 100k SOL"
    elif stake_volume < 1000000:
        return "d. 100k < Stake < 1m SOL"
    elif stake_volume < 10000000:
        return "e. 1m < Stake < 10m SOL"
    else:
        return "f. Stake > 10m SOL"


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
    title="Number of Stakers by Amount Staked",
    color="Stake Category",
    color_discrete_sequence=px.colors.qualitative.Prism,
)
fig2.update_layout(xaxis_title="Total Stake (SOL)", yaxis_title="Addresss Count")

fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=True)
st.plotly_chart(fig2, use_container_width=True)
# END --- STAKE VOLUME CATEGORY
st.write("---")

c1, c2 = st.columns(2)
n_addresses = c1.slider("Number of top addresses", 1, 100, 25, key="summary_slider")
lst = c2.selectbox(
    "Choose a Liquid Staking Token",
    ["All LSTs"] + list(token_name_dict.keys()),
    # format_func=lambda x: f"{x} ({token_name_dict[x]})", # Not really useful
    key="summary_token_select",
)
exclude_foundation = c1.checkbox("Exclude Solana Foundation delegation", key="summary_foundation_check")
exclude_labeled = c2.checkbox("Exclude labeled addresses", key="summary_labeled_check")

top_stakers = staker_df[staker_df["Date"] == staker_df["Date"].max()]
if exclude_foundation:
    top_stakers = top_stakers[top_stakers["Name"] != "Solana Foundation Delegation Account"]
if exclude_labeled:
    top_stakers = top_stakers[(top_stakers["Address Name"].isna()) & (top_stakers["Friendlyname"].isna())]


def holds_lst(x):
    if pd.isna(x):
        return 0
    elif x == 0:
        return 0
    else:
        return 1


def lsts_held(x):
    if x.Amount == 0 or pd.isna(x.Amount):
        return ""
    else:
        return x["Token Name"]


def lst_amount(x):
    if x.Amount == 0 or pd.isna(x.Amount):
        return ""
    else:
        return x["Amount"]


top_stakers["Holds LST"] = top_stakers.Amount.apply(holds_lst)
top_stakers["LST Tokens"] = top_stakers.apply(lsts_held, axis=1)
top_stakers["LST Amounts"] = top_stakers.apply(lst_amount, axis=1)
top_stakers = top_stakers.merge(
    (
        top_stakers.groupby("Address")
        .agg(
            LSTs_Held=("Holds LST", "sum"),
            LST_Tokens=(
                "LST Tokens",
                lambda x: "" if all(pd.isna(y) for y in x) else ",".join(z for z in x if z != ""),
            ),
            LST_Amounts=(
                "LST Amounts",
                lambda x: ""
                if all((pd.isna(y) or y == 0.0) for y in x)
                else ",".join(f"{z:.0f}" for z in x if z != ""),
            ),
        )
        .reset_index()
    ),
    on="Address",
    how="left",
)

top_stakers = (
    top_stakers.drop_duplicates(subset=["Date", "Address"], keep="first")
    .sort_values(by="Total Stake", ascending=False)
    .drop(
        columns=[
            "Token Name",
            "Amount",
            "Token",
            "Symbol",
            "Amount Usd",
            "Lst Rank",
            "Holds LST",
            "LST Tokens",
            "LST Amounts",
            "Token",
        ]
    )
)

top_lsts = top_stakers.copy()
top_lsts["Total LST Amount"] = top_lsts["LST_Amounts"].apply(
    lambda x: sum([float(y) for y in x.split(",") if y != ""])
)
if lst == "All LSTs":
    top_lsts = (
        top_lsts[top_lsts.LST_Tokens != ""]
        .sort_values(by="Total LST Amount", ascending=False)
        .reset_index(drop=True)
    )
else:
    top_lsts = (
        top_lsts[top_lsts.LST_Tokens.str.contains(lst.split("(")[0].strip(" "))]
        .assign(
            LST=top_lsts["LST_Tokens"].str.split(","),
            Amount=top_lsts["LST_Amounts"].str.split(","),
        )
        .explode(["LST", "Amount"])
    )
    top_lsts["Amount"] = top_lsts["Amount"].astype(float)
    top_lsts = top_lsts[top_lsts.LST == lst].sort_values(by="Amount", ascending=False).reset_index(drop=True)


chart = (
    alt.Chart(
        top_stakers.sort_values(by="Total Stake", ascending=False).iloc[:n_addresses],
        title=f"Top {n_addresses} Stakers by Stake Amount",
    )
    .mark_bar()
    .encode(
        x=alt.X("Name", title="Address Name", sort="-y", axis=alt.Axis(labelAngle=-70)),
        y=alt.Y("Total Stake", title="Total Stake (SOL)"),
        tooltip=[
            alt.Tooltip("Name", title="Address Name"),
            alt.Tooltip("Address"),
            alt.Tooltip("Total Stake", title="Total Stake (SOL)", format=",.0f"),
            alt.Tooltip("Rank", title="Rank among SOL Stakers"),
            alt.Tooltip("LSTs_Held", title="Number of LSTs held"),
            alt.Tooltip("LST_Tokens", title="LSTs held"),
            alt.Tooltip("LST_Amounts", title="LST Amounts"),
        ],
        href="Explorer Url",
        color=alt.Color(
            "Name",
            sort=alt.EncodingSortField(field="Total Stake", op="max", order="descending"),
            scale=alt.Scale(scheme="turbo"),
            legend=None,
        ),
    )
).properties(height=600, width=600)
st.altair_chart(chart, use_container_width=True)


ycol = "Total LST Amount" if lst == "All LSTs" else "Amount"
chart = (
    alt.Chart(
        top_lsts.iloc[:n_addresses],
        title=f"Top {n_addresses} Liquid Staking Token Holders among Top Stakers, {lst}",
    )
    .mark_bar()
    .encode(
        x=alt.X("Name", title="Address Name", sort="-y", axis=alt.Axis(labelAngle=-70)),
        y=alt.Y(ycol, title="Amount"),
        tooltip=[
            alt.Tooltip("Name", title="Address Name"),
            alt.Tooltip("Address"),
            alt.Tooltip(ycol, title=f"Amount, {lst}", format=",.0f"),
            alt.Tooltip("Rank", title="Rank among SOL Stakers"),
            alt.Tooltip("LSTs_Held", title="Number of LSTs held"),
            alt.Tooltip("LST_Tokens", title="LSTs held"),
            alt.Tooltip("LST_Amounts", title="LST Amounts"),
        ],
        href="Explorer Url",
        color=alt.Color(
            "Name",
            sort=alt.EncodingSortField(field=ycol, op="max", order="descending"),
            scale=alt.Scale(scheme="turbo"),
            legend=None,
        ),
    )
).properties(height=600, width=600)
st.altair_chart(chart, use_container_width=True)
st.write("---")

st.subheader("Total LST Holdings by Top Stakers")
c1, c2 = st.columns([3, 2])
date_range = c1.radio(
    "Choose a date range:",
    [  # #TODO: not doing more dates until more data is queried
        "All dates",
        "Past Year",
        "180d",
        "90d",
        "60d",
        "30d",
        "14d",
        "7d",
    ],
    horizontal=True,
    index=2,
    key="summary_date_range",
)
normalize = c2.checkbox("Show proportions instead of Amounts", key="summary_normalize")
interactive = c2.selectbox(
    "Turn on chart zooming/panning", [None, "both", "x-axis", "y-axis"], key="summary_interactive"
)
chart, lst_summary_df = charts.alt_total_lst(
    staker_df, date_range, normalize=normalize, interactive=interactive
)
st.altair_chart(chart, use_container_width=True)
st.write("---")

base = alt.Chart(
    lst_summary_df[
        (lst_summary_df["Date"] == lst_summary_df["Date"].max()) & (lst_summary_df["Total_LST_Amount"] > 0.1)
    ],
    title="Current LST Holdings by Top Stakers",
).encode(
    x=alt.X(
        "Token Name",
        title=None,
        sort=alt.EncodingSortField(field="Total_LST_Amount", op="max", order="descending"),
        axis=alt.Axis(labelAngle=-70),
    ),
    tooltip=[alt.Tooltip("yearmonthdate(Date):T", title="Date")]
    + [
        alt.Tooltip(
            x,
            title=x.replace("_", " "),
            format=",.1f" if x not in ["Token Name", "Symbol"] else "",
        )
        for x in lst_summary_df.columns.drop("Date")
    ],
)
bar = base.mark_bar().encode(
    y=alt.Y("Total_LST_Amount", title="Total LST Balance"),
    color=alt.Color(
        "Token Name",
        sort=alt.EncodingSortField(field="Total_LST_Amount", op="max", order="descending"),
        scale=alt.Scale(scheme="turbo"),
        legend=None,
    ),
)
line = base.mark_line(
    color="#983832", point=alt.OverlayMarkDef(fill="#983832", color="#FD5E53", size=50)
).encode(y=alt.Y("Total_Holders_NonZero", title="Holders"))
chart = alt.layer(bar, line).resolve_scale(y="independent").properties(height=600, width=600)
st.altair_chart(chart, use_container_width=True)
st.write("---")

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
    slug = "top_stakers"
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
        st.write(
            f"**Liquid Staking Token Holdings**: The selected addresses do not hold {lst} in this date range"
        )
    else:
        st.write(token_top_stakers_df)
        st.write(
            "View the data shown in the [Liquid Staking Token Holders from Top SOL Stakers](#liquid-staking-token-holders-from-top-sol-stakers) chart above."
        )
        slug = "lst_holders_top_stakers"
        st.download_button(
            "Click to Download",
            token_top_stakers_df.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
    st.write("---")
    st.subheader("Top LST Holders among Top SOL Stakers")
    st.write(
        "View the data shown in the [Top LST Holders among Top SOL Stakers](#top-lst-holders-among-top-sol-stakers) chart above."
    )
    st.write(token_top_holders_df)
    slug = "lst_holders_top_holders"
    st.download_button(
        "Click to Download",
        token_top_holders_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("---")
    st.subheader("All data")
    st.write(
        "Download raw data for Top SOL Stakers (unfiltered by anything selected in [Settings](#settings))"
    )
    slug = "all_staker_lst_data"
    st.download_button(
        "Click to Download",
        staker_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
