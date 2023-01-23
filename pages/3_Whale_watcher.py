import altair as alt
import numpy as np
import pandas as pd
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
    A viewpoint above Solana data. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/) and [Helius](https://helius.xyz/).

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi)
    """
)
c1.image(
    image,
    width=100,
)
st.write("---")

query_base = "https://next.flipsidecrypto.xyz/edit/queries"
api_base = "https://api.flipsidecrypto.com/api/v2/queries"
whale_query_dict = {
    "nft": {
        "query": f"{query_base}/bf44cae5-dcf6-41eb-a481-8ec257569533",
        "api": f"{api_base}/bf44cae5-dcf6-41eb-a481-8ec257569533/data/latest",
        "datecols": ["BLOCK_TIMESTAMP"],
    },
    # "Bonk Leaderboard": {
    #     "query": f"{query_base}/5de2aadc-622c-4500-bc70-9e0fd4bfbca4",
    #     "api": f"{api_base}/5de2aadc-622c-4500-bc70-9e0fd4bfbca4/data/latest",
    #     "datecols": None,
    # },
    # "Buyers vs Sellers": {
    #     "query": f"{query_base}/ac7933e1-8e70-4858-a243-8e8e494a40b1",
    #     "api": f"{api_base}/ac7933e1-8e70-4858-a243-8e8e494a40b1/data/latest",
    #     "datecols": ["DATE"],
    # },
}
whale_data_dict = {}
for k, v in whale_query_dict.items():
    whale_data_dict[k] = utils.load_overview_data(v["api"], v["datecols"])

st.header("Whale Watcher")

st.subheader("NFT Whales")
nft_whales = whale_data_dict["nft"]
nft_whales["Explorer URL"] = nft_whales["Tx Id"].apply(lambda x: f"https://solana.fm/tx/{x}")

c1, c2 = st.columns(2)
currency = c1.radio("Choose a Currency:", ["SOL", "USD"], key="nft-whale-currency", horizontal=True)
scale = c2.checkbox(
    "Log Scale?",
    key="nft-whale-scale",
)
scale_type = "log" if scale else "linear"
chart = (
    alt.Chart(nft_whales)
    .mark_circle(color="#FD5E53", size=50)
    .encode(
        x=alt.X("yearmonthdatehours(Block Timestamp)", title=""),
        y=alt.Y(
            "Sales Amount" if currency == "SOL" else "Usd Amount",
            scale=alt.Scale(zero=False, type=scale_type),
        ),
        href="Explorer URL",
        tooltip=[
            alt.Tooltip("yearmonthdatehoursminutesseconds(Block Timestamp)"),
            alt.Tooltip("Purchaser"),
            alt.Tooltip("Mint"),
            alt.Tooltip("Sales Amount", title="Sales Amount (SOL)", format=".2f"),
            alt.Tooltip("Usd Amount", title="Sales Amount (USD)", format=".2f"),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
st.altair_chart(chart, use_container_width=True)
with st.expander("View and Download Data Table"):
    st.write(nft_whales)
    slug = f"whales_nft"
    st.download_button(
        "Click to Download",
        nft_whales.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
