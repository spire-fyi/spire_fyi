import ast
import asyncio
import datetime

import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st
from PIL import Image

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
    A viewpoint above Solana data. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/), [Helius](https://helius.xyz/) and [SolanaFM APIs](https://docs.solana.fm/).

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi) | Donations: GvvrKbq21eTkknHRt9FGVFN54pLWXSSo4D4hz2i1JCn5
    """
)
c1.image(
    image,
    width=100,
)
st.write("---")
st.header("xNFT Usage Analysis")


st.subheader("xNFT Installs")
xnft_df = utils.load_xnft_data()
createInstall = xnft_df[xnft_df["Instruction Type"] == "createInstall"]

xnft_counts_by_user = (
    createInstall.groupby("Fee Payer")
    .Xnft.nunique()
    .reset_index()
    .sort_values(by="Xnft", ascending=False)
    .reset_index(drop=True)
)
xnft_counts_by_user["url"] = xnft_counts_by_user["Fee Payer"].apply(
    lambda x: f"https://solana.fm/address/{x}"
)
# xnft_counts_by_user['username'] = utils.get_backpack_usernames(xnft_counts_by_user)

c1, c2 = st.columns(2)
date_range = c1.radio(
    "Choose a date range:",
    [
        "60d",
        "30d",
        "14d",
        "7d",
    ],
    horizontal=True,
    index=2,
    key="installs_date_range",
)
xnfts = c2.slider("Top xNFTs to view", 1, createInstall.Xnft.nunique(), 10, key="installs_slider")

chart_df = createInstall.copy()[
    createInstall["Block Timestamp"]
    >= (pd.to_datetime(datetime.datetime.today()) - pd.Timedelta(f"{int(date_range[:-1])}d"))
]
chart_df, totals = utils.aggregate_xnft_data(chart_df, xnfts)

chart = (
    (
        alt.Chart(chart_df, title="xNFT Install Counts by Date")
        .mark_bar()
        .encode(
            x=alt.X(
                "yearmonthdate(Block Timestamp)",
                title="Date",
            ),
            y=alt.Y(
                "Count",
                title="Installs",
            ),
            color=alt.Color(
                "Display Name",
                title="xNFT Name",
                sort=alt.EncodingSortField(field="Count", op="max", order="descending"),
                scale=alt.Scale(scheme="turbo"),
            ),
            order=alt.Order("Count", sort="ascending"),
            tooltip=[
                alt.Tooltip("yearmonthdate(Block Timestamp)", title="Date"),
                alt.Tooltip("Display Name", title="xNFT Name"),
                alt.Tooltip("Count", title="Number of Installs"),
                alt.Tooltip("xNFT", title="Address"),
            ],
            href="url",
        )
    )
    .properties(height=600, width=600)
    .interactive(bind_x=False)
)
st.altair_chart(chart, use_container_width=True)
c1, c2, c3, c4 = st.columns(4)
# TODO: update based on date range?
c1.metric("Total number of xNFTs", f"{createInstall.Xnft.nunique():,}")
c2.metric("Total xNFTs installed", f"{len(createInstall):,}")
c3.metric("Average xNFTs installed per user (overall)", f"{xnft_counts_by_user.Xnft.mean():.1f}")
c4.metric(
    "Average daily xNFTs installed (in date range)",
    f"{chart_df.groupby('Block Timestamp').Count.sum().reset_index().Count.mean():,.1f}",
)
st.write("---")

c1, c2 = st.columns(2)
chart = (
    alt.Chart(
        totals.sort_values(by="Count", ascending=False).iloc[:xnfts],
        title=f"Top {xnfts} xNFTs by Install Count",
    )
    .mark_bar()
    .encode(
        x=alt.X("Mint Seed Name", title="xNFT Name", sort="-y"),
        y=alt.Y("Count", title="Installs"),
        # url="url",
        tooltip=[
            alt.Tooltip("Mint Seed Name", title="xNFT Name"),
            alt.Tooltip("Count", title="Number of Installs", format=","),
            alt.Tooltip("Rating", format=".2f"),
            alt.Tooltip("Num Ratings", title="Number of Ratings"),
            alt.Tooltip("xNFT", title="Address"),
        ],
        href="url",
        color=alt.Color(
            "Mint Seed Name",
            sort=alt.EncodingSortField(field="Count", op="max", order="descending"),
            scale=alt.Scale(scheme="turbo"),
            legend=None,
        ),
    )
).properties(height=600, width=600)
c1.altair_chart(chart, use_container_width=True)
chart = (
    alt.Chart(
        totals.sort_values(by=["Rating", "Count"], ascending=False).iloc[:xnfts],
        title=f"Top {xnfts} xNFTs by Average Rating",
    )
    .mark_bar()
    .encode(
        x=alt.X("Mint Seed Name", title="xNFT Name", sort="-y"),
        y=alt.Y("Rating"),
        tooltip=[
            alt.Tooltip("Mint Seed Name", title="xNFT Name"),
            alt.Tooltip("Rating", format=".2f"),
            alt.Tooltip("Num Ratings", title="Number of Ratings"),
            alt.Tooltip("Count", title="Number of Installs", format=","),
            alt.Tooltip("xNFT", title="Address"),
        ],
        href="url",
        color=alt.Color(
            "Mint Seed Name",
            sort=alt.EncodingSortField(field="Count", op="max", order="descending"),
            scale=alt.Scale(scheme="turbo"),
            legend=None,
        ),
    )
).properties(height=600, width=600)
c2.altair_chart(chart, use_container_width=True)


st.subheader("xNFT Backpack User Information")

c1, c2 = st.columns(2)

chart = (
    alt.Chart(xnft_counts_by_user, title="xNFTs Installed: User Count")
    .mark_bar(
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
    )
    .encode(
        x=alt.X("Xnft", title="xNFTs Installed", bin=alt.Bin(maxbins=25)),
        y=alt.Y("count()", title="User Count"),
    )
    .properties(height=600, width=600)
)
c1.altair_chart(chart, use_container_width=True)

chart = (
    alt.Chart(xnft_counts_by_user.iloc[:xnfts], title=f"Top {xnfts} Users by Number of Installs")
    .mark_bar()
    .encode(
        x=alt.X("Fee Payer", title="Address", sort="-y"),
        y=alt.Y("Xnft", title="xNFTs Installed"),
        color=alt.Color(
            "Fee Payer",
            sort=alt.EncodingSortField(field="Xnft", op="max", order="descending"),
            scale=alt.Scale(scheme="turbo"),
            legend=None,
        ),
        tooltip=[alt.Tooltip("Fee Payer", title="Address"), alt.Tooltip("Xnft", title="xNFTs Installed")],
        href="url",
    )
    .properties(height=600, width=600)
)
c2.altair_chart(chart, use_container_width=True)

st.write("---")
address = st.text_input("Enter a Solana address to get its Backpack Username", key="backpackt-text-input")
backpack_username = utils.get_backpack_username(address)
if backpack_username == "":
    pass
else:
    if backpack_username is None:
        st.subheader(address)
        st.caption("This address isn't associated with a backpack username")
        backpack = False
    else:
        st.subheader(backpack_username)
        st.caption(address)
        backpack = True

    tx_info = """
    --sql
    select
        *
    from
        solana.core.ez_signers
    where
        signer = '{param}'
    ;
    """
    nft_purchases = """
    --sql
    select
        *
    from
        solana.core.fact_nft_sales
    where
        purchaser = '{param}'
        and succeeded = 'TRUE'
    ;
    """
    nft_sales = """
    --sql
    select
        *
    from
        solana.core.fact_nft_sales
    where
        seller = '{param}'
        and succeeded = 'TRUE'
    ;
    """
    nft_mints = """
    --sql
    select
        *
    from
        solana.core.fact_nft_mints
    where
        purchaser = '{param}'
        and succeeded = 'TRUE'
    ;
    """
    swaps = """
    --sql
    select
        *
    from
        solana.core.fact_swaps
    where
        swapper = '{param}'
        and succeeded = 'TRUE'
    ;
    """
    data_load_state = st.text(f"Querying data for {address}...")
    tx_data = utils.run_query_and_cache("backpack_tx_info", tx_info, address)
    sales_data = utils.run_query_and_cache("backpack_sales_info", nft_sales, address)
    purchases_data = utils.run_query_and_cache("backpack_purchase_info", nft_purchases, address)
    mints_data = utils.run_query_and_cache("backpack_mints_info", nft_mints, address)
    swaps_data = utils.run_query_and_cache("backpack_swaps_info", swaps, address)
    data_load_state.text("")

    try:
        num_programs = len(pd.unique(ast.literal_eval(tx_data.PROGRAMS_USED.values[0])))
    except ValueError:
        num_programs = len(pd.unique(tx_data.PROGRAMS_USED.values[0]))
    num_swaps = swaps_data.TX_ID.nunique()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("First Transaction Date", f"{pd.to_datetime(tx_data.FIRST_TX_DATE.values[0]):%d %b %Y}")
    c2.metric("Number of Transactions", f"{tx_data.NUM_TXS.values[0]:,}")
    c3.metric("Total Fees Paid", f"{tx_data.TOTAL_FEES.values[0]/utils.LAMPORTS_PER_SOL:,.5f} SOL")
    c4.metric("Number of Programs Used", f"{num_programs}")
    c5.metric("Number of DEX swaps", num_swaps)
    if backpack:
        c6.metric(
            "Number of xNFTS installed",
            f"{createInstall[createInstall['Fee Payer'] == address].Xnft.nunique()}",
        )

    num_sales = len(sales_data)
    c1.metric("Number of NFT sales", num_sales)
    if num_sales != 0:
        total_sales_amount = sales_data.SALES_AMOUNT.sum()
        c2.metric("Total amount of NFT Sales", f"{total_sales_amount:,.2f} SOL")

    num_purchases = len(purchases_data)
    c3.metric("Number of NFT purchases", num_purchases)
    if num_purchases != 0:
        total_purchases_amount = purchases_data.SALES_AMOUNT.sum()
        c4.metric("Total amount of NFT purchases", f"{total_purchases_amount:,.2f} SOL")

    num_mints = mints_data.TX_ID.nunique()
    c5.metric("Number of NFT mints", num_mints)
