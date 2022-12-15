import datetime

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from scipy.stats import ttest_ind, ttest_rel

import spire_fyi.charts as charts
import spire_fyi.utils as utils

alt.data_transformers.disable_max_rows()
image = Image.open("assets/images/spire_logo.png")

st.set_page_config(
    page_title="Spire",
    page_icon=image,
    layout="wide",
)
c1, c2 = st.columns([1, 3])

c2.header("Spire")
c2.caption(
    """
    A viewpoint above Solana data. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/) and [Helius](https://helius.xyz/).
    
    Spire is a Solana-focused on-chain data platform that aims to provide in-depth data and insights to add value to the Solana ecosystem.

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi)
    """
)
c1.image(
    image,
    width=200,
)
st.write("---")


st.header("NFT Analytics")
st.write(
    f"""See [NFT Royalties](NFT_Royalties) for more in depth analysis.
    """
)
c1, c2 = st.columns(2)
buyers_sellers, _, mints_by_purchaser, _ = utils.load_nft_data()
chart = (
    alt.Chart(buyers_sellers, title="Unique NFT Marketplace Buyers and Sellers: Weekly")
    .mark_bar(width=3)
    .encode(
        x=alt.X("yearmonthdate(Date)", title="Date"),
        y=alt.Y("value", title="Unique Addresses"),
        color=alt.Color(
            "variable",
            title="User Type",
            scale=alt.Scale(domain=["Buyers", "Sellers"], range=["#4B3D60", "#FD5E53"]),
        ),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            alt.Tooltip("variable", title="User Type"),
            alt.Tooltip("value", title="Unique Addresses", format=","),
            alt.Tooltip("Transaction Count", format=","),
            alt.Tooltip("Unique NFTs Sold", format=","),
            alt.Tooltip("Sale Amount (SOL)", format=",.2f"),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
c1.altair_chart(chart, use_container_width=True)
chart = (
    alt.Chart(mints_by_purchaser, title="Average Mints per Address: Daily")
    .mark_area(
        line={"color": "#4B3D60", "size": 1},
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="#4B3D60", offset=0),
                alt.GradientStop(color="#FD5E53", offset=1),
            ],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
        interpolate="monotone",
    )
    .encode(
        x=alt.X("yearmonthdate(Date)", title="Date"),
        y=alt.Y("Average Mints per Address"),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)"),
            alt.Tooltip("Average Mints per Address", format=",.2f"),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
c2.altair_chart(chart, use_container_width=True)
with st.expander("View and Download Data Table"):
    buyers_sellers = buyers_sellers.rename(columns={"variable": "User Type", "value": "Unique Addresses"})
    st.write(buyers_sellers)
    st.download_button(
        "Click to Download",
        buyers_sellers.to_csv(index=False).encode("utf-8"),
        f"weekly_nft_buyers-sellers.csv",
        "text/csv",
        key="download-weekly-nft-buyers-sellers",
    )
    st.write(mints_by_purchaser)
    st.download_button(
        "Click to Download",
        mints_by_purchaser.to_csv(index=False).encode("utf-8"),
        f"daily_nft_average_mints_per_address.csv",
        "text/csv",
        key="download-daily-mints-per-address",
    )
st.subheader("Cross-chain comparison")
_, _, _, by_chain_data = utils.load_nft_data()
c1, c2 = st.columns(2)
comp_type = c1.radio("Choose a comparison:", ["Sales", "Mints"], horizontal=True, key="nft-comp-type")
metric = c2.selectbox("Choose a metric:", ["Count", "Unique Users"], key="nft-chain-metric")
chart = (
    alt.Chart(by_chain_data[by_chain_data.Type == comp_type], title=f"{comp_type}, {metric} by Chain: Daily")
    .mark_area(
        line={"color": "#4B3D60"},
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="#4B3D60", offset=0),
                alt.GradientStop(color="#FD5E53", offset=1),
            ],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
        interpolate="monotone",
    )
    .encode(
        x=alt.X(
            "yearmonthdate(Date)",
            title="Date",
        ),
        y=alt.Y(
            metric,
        ),
        color=alt.Color(
            "Chain", scale=alt.Scale(domain=["Solana", "Ethereum"], range=["#4B3D60", "#FD5E53"]), sort="-y"
        ),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            "Chain",
            alt.Tooltip(metric, format=","),
            # alt.Tooltip(metric, format=",.2f" if metric == "Sale Amount (SOL)" else ","),
            # alt.Tooltip("Buyers", format=","),
            # alt.Tooltip("Sellers", format=","),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
st.altair_chart(chart, use_container_width=True)

with st.expander("View and Download Data Table"):
    st.write(by_chain_data)
    st.download_button(
        "Click to Download",
        by_chain_data.to_csv(index=False).encode("utf-8"),
        f"daily_nft_by_chain.csv",
        "text/csv",
        key="download-daily-nft-chain",
    )


st.header("Programs")
st.write(
    f"""See the [Program Usage](Program_Usage) for more in depth analysis.
    """
)
weekly_program_data = utils.load_weekly_program_data()
weekly_new_program_data = utils.load_weekly_new_program_data()

c1, c2 = st.columns(2)
unique_program_chart = charts.alt_weekly_unique_chart(
    weekly_program_data[weekly_program_data.WEEK > "2020-10-01"],
    "Unique Programs Used: Weekly",
    "UNIQUE_PROGRAMS",
    "Number of Unique Programs",
)
c1.altair_chart(unique_program_chart, use_container_width=True)

new_program_chart = charts.alt_weekly_cumulative_chart(
    weekly_new_program_data[weekly_new_program_data.WEEK > "2020-10-01"],
    "New Programs: Weekly",
    "New Programs",
    "Cumulative Programs",
)
c2.altair_chart(new_program_chart, use_container_width=True)

with st.expander("View and Download Data Table"):
    combined_program_df = weekly_new_program_data.merge(weekly_program_data, on="WEEK")
    combined_program_df = (
        combined_program_df[["WEEK", "UNIQUE_PROGRAMS", "New Programs", "Cumulative Programs"]]
        .rename(columns={"WEEK": "Week", "UNIQUE_PROGRAMS": "Unique Programs"})
        .sort_values(by="Week", ascending=False)
        .reset_index(drop=True)
    )
    st.write(combined_program_df)
    st.download_button(
        "Click to Download",
        combined_program_df.to_csv(index=False).encode("utf-8"),
        f"weekly_program_counts.csv",
        "text/csv",
        key="download-weekly-program",
    )

st.header("Users")
c1, c2 = st.columns(2)
weekly_user_data = utils.load_weekly_user_data()
weekly_new_user_data = utils.load_weekly_new_user_data()

unique_user_chart = charts.alt_weekly_unique_chart(
    weekly_user_data[weekly_user_data.WEEK > "2020-10-01"],
    "Unique Users: Weekly",
    "UNIQUE_USERS",
    "Unique Fee Payers",
)
c1.altair_chart(unique_user_chart, use_container_width=True)
new_user_chart = charts.alt_weekly_cumulative_chart(
    weekly_new_user_data[weekly_new_user_data.WEEK > "2020-10-01"],
    "New Users: Weekly",
    "New Users",
    "Cumulative Users",
)
c2.altair_chart(new_user_chart, use_container_width=True)

with st.expander("View and Download Data Table"):
    combined_user_df = weekly_new_user_data.merge(weekly_user_data, on="WEEK")
    combined_user_df = (
        combined_user_df[["WEEK", "UNIQUE_USERS", "New Users", "Cumulative Users"]]
        .rename(columns={"WEEK": "Week", "UNIQUE_USERS": "Unique Users"})
        .sort_values(by="Week", ascending=False)
        .reset_index(drop=True)
    )
    st.write(combined_user_df)
    st.download_button(
        "Click to Download",
        combined_user_df.to_csv(index=False).encode("utf-8"),
        f"weekly_user_counts.csv",
        "text/csv",
        key="download-weekly-user",
    )

st.header("DeFi")
defi_data = utils.load_defi_data()
metric = st.radio(
    "Choose a metric:",
    ["Transaction Count", "Unique Users"],
    horizontal=True,
)
chart = (
    alt.Chart(defi_data, title=f"DEX {metric}: Weekly")
    .mark_bar(width=8)
    .encode(
        x=alt.X(
            "yearmonthdate(Date)",
            title="Date",
        ),
        y=alt.Y(metric),
        order=alt.Order(
            metric,
            sort="descending",
        ),
        color=alt.Color(
            "Swap Program",
            scale=alt.Scale(scheme="turbo"),
            sort=alt.EncodingSortField(field=metric, op="max", order="ascending"),
        ),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            alt.Tooltip("Swap Program"),
            alt.Tooltip("Transaction Count", format=","),
            alt.Tooltip("Unique Users", format=","),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
st.altair_chart(chart, use_container_width=True)

with st.expander("View and Download Data Table"):
    st.write(defi_data)
    st.download_button(
        "Click to Download",
        defi_data.to_csv(index=False).encode("utf-8"),
        f"weekly_defi.csv",
        "text/csv",
        key="download-weekly-defi",
    )

# st.header("Additional Figures")
# components.iframe(
#     "https://app.flipsidecrypto.com/dashboard/spireee-wip-NKWJbS",
#     height=1800,
#     scrolling=True,
# )
