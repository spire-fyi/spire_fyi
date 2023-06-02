import json

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
    page_title="Spire: Whale Watcher",
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

query_base = utils.query_base
api_base = utils.api_base
whale_query_dict = {
    "nft": {
        "query": f"{query_base}/bf44cae5-dcf6-41eb-a481-8ec257569533",
        "api": f"{api_base}/bf44cae5-dcf6-41eb-a481-8ec257569533/data/latest",
        "datecols": ["BLOCK_TIMESTAMP"],
    },
    "nft_other": {
        "query": f"{query_base}/8283a6fb-205a-4312-b936-fa792fe1ccc2",
        "api": f"{api_base}/8283a6fb-205a-4312-b936-fa792fe1ccc2/data/latest",
        "datecols": ["DATETIME"],
    },
    "swaps": {
        "query": f"{query_base}/d73d6437-e3b1-48ed-b11b-ce159c876c0e",
        "api": f"{api_base}/d73d6437-e3b1-48ed-b11b-ce159c876c0e/data/latest",
        "datecols": ["BLOCK_TIMESTAMP"],
    },
    "transfers": {
        "query": f"{query_base}/f240ce3b-98a5-4760-9712-f2dae550bdd1",
        "api": f"{api_base}/f240ce3b-98a5-4760-9712-f2dae550bdd1/data/latest",
        "datecols": ["BLOCK_TIMESTAMP"],
    },
}
whale_data_dict = {}
for k, v in whale_query_dict.items():
    whale_data_dict[k] = utils.load_flipside_api_data(v["api"], v["datecols"])
    try:
        whale_data_dict[k]["Explorer URL"] = whale_data_dict[k]["Tx Id"].apply(
            lambda x: f"https://solana.fm/tx/{x}"
        )
    except:
        whale_data_dict[k]["Explorer URL"] = whale_data_dict[k]["Purchaser"].apply(
            lambda x: f"https://solana.fm/address/{x}"
        )

st.header("Whale Watcher")
st.write("Tracking large transfers, swaps and NFT purchases in the past week 🐋.")
with st.expander("Instructions"):
    st.write(
        """
    - Select a tab to choose a 🐋 type.
    - `Ctrl-Click` a point on the scatter plot to open SolanaFM transaction details in a new tab.
    - `Shift-Click` on token names in the legend to focus on those only.
    """
    )

swaps, nft, transfers = st.tabs(["Swaps", "NFT", "Transfers"])

with transfers:
    st.subheader("Whale Tranfers")
    st.write("Any transfer worth over **$1 million**")
    transfer_whales = whale_data_dict["transfers"]
    # #HACK: price table is incorrect for some low volume coins
    transfer_whales = transfer_whales[
        ~(
            transfer_whales["Token Name"].isin(
                [
                    "Buff Samo",
                    "CashCow",
                    "Boo",
                    "Cope Token",
                    "Solminter",
                    "The Xenobots Project",
                    "Starbots GEAR",
                    "Kalisten",
                ]
            )
        )
    ].reset_index(drop=True)
    scale = st.checkbox(
        "Log Scale",
        key="transfer-whale-scale",
    )
    scale_type = "log" if scale else "linear"
    legend_selection = alt.selection_multi(fields=["Token Name"], bind="legend")
    chart = (
        alt.Chart(transfer_whales, title="Transfer 🐋 Transactions, past 7d")
        .mark_circle()
        .encode(
            x=alt.X("yearmonthdatehours(Block Timestamp)", title=""),
            y=alt.Y(
                "Usd Amount",
                title="Transer Amount (USD)",
                scale=alt.Scale(zero=False, type=scale_type),
            ),
            color=alt.Color(
                "Token Name",
                scale=alt.Scale(scheme="sinebow"),
                # sort=alt.EncodingSortField(field="Usd Amount", op="count", order="ascending"),
            ),
            size=alt.Size("Usd Amount", title="Transer Amount (USD)"),
            opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.01)),
            href="Explorer URL",
            tooltip=[
                alt.Tooltip("yearmonthdatehoursminutesseconds(Block Timestamp)"),
                alt.Tooltip("Token Name"),
                alt.Tooltip("Usd Amount", title="Transer Amount (USD)", format=",.2f"),
                alt.Tooltip("Token Amount", format=",.2f"),
                alt.Tooltip("Tx To", title="Transfer to Address"),
                alt.Tooltip("To Label", title="Transfer to Label"),
                alt.Tooltip("Tx From", title="Transfer from Address"),
                alt.Tooltip("From Label", title="Transfer from Label"),
            ],
        )
        .add_selection(legend_selection)
        .properties(height=600, width=600)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("View and Download Data Table"):
        st.write(transfer_whales)
        slug = f"whales_transfer"
        st.download_button(
            "Click to Download",
            transfer_whales.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )

with swaps:
    st.subheader("Whale Swaps")
    st.write("Any DEX Swap worth over **$50,000**")
    swap_whales = whale_data_dict["swaps"]
    scale = st.checkbox(
        "Log Scale",
        key="swap-whale-scale",
    )
    scale_type = "log" if scale else "linear"
    legend_selection = alt.selection_multi(fields=["Swap From"], bind="legend")
    chart = (
        alt.Chart(swap_whales, title="Swap 🐋 Transactions, past 7d")
        .mark_circle()
        .encode(
            x=alt.X("yearmonthdatehours(Block Timestamp)", title=""),
            y=alt.Y(
                "Usd Amount From",
                title="Swapped Amount (USD)",
                scale=alt.Scale(zero=False, type=scale_type),
            ),
            color=alt.Color(
                "Swap From",
                scale=alt.Scale(scheme="sinebow"),
                # sort=alt.EncodingSortField(field="Usd Amount", op="count", order="ascending"),
            ),
            size=alt.Size(
                "Usd Amount From",
                title="Swapped Amount (USD)",
            ),
            opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.01)),
            href="Explorer URL",
            tooltip=[
                alt.Tooltip("yearmonthdatehoursminutesseconds(Block Timestamp)"),
                alt.Tooltip("Swap From"),
                alt.Tooltip("Usd Amount From", title="Swapped Amount (USD) From", format=",.2f"),
                alt.Tooltip("Token Amount From", format=",.2f"),
                alt.Tooltip("Swap To"),
                alt.Tooltip("Usd Amount To", title="Swapped Amount (USD) To", format=",.2f"),
                alt.Tooltip("Token Amount To", format=",.2f"),
                alt.Tooltip(
                    "Swapper",
                ),
            ],
        )
        .add_selection(legend_selection)
        .properties(height=600, width=600)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("View and Download Data Table"):
        st.write(swap_whales)
        slug = f"whales_swaps"
        st.download_button(
            "Click to Download",
            swap_whales.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )

with nft:
    st.subheader("NFT Whales")
    st.write("Any NFT purchase worth over **$5,000**")
    nft_whales = whale_data_dict["nft"]

    # Use Helius to get
    unique_mints = nft_whales.Mint.unique()
    n_splits = np.ceil(len(unique_mints) / 100)
    all_mint_splits = np.array_split(unique_mints, n_splits)
    collection_df = utils.get_nft_mint_data(all_mint_splits)
    nft_whales = nft_whales.merge(collection_df, on="Mint", how="left")

    c1, c2 = st.columns(2)
    currency = c1.radio("Choose a Currency:", ["SOL", "USD"], key="nft-whale-currency", horizontal=True)
    scale = c2.checkbox(
        "Log Scale",
        key="nft-whale-scale",
    )
    scale_type = "log" if scale else "linear"
    legend_selection = alt.selection_multi(fields=["NFT Name"], bind="legend")
    chart = (
        alt.Chart(nft_whales, title="NFT 🐋 Transactions, past 7d")
        .mark_circle()
        .encode(
            x=alt.X("yearmonthdatehours(Block Timestamp)", title=""),
            y=alt.Y(
                "Sales Amount" if currency == "SOL" else "Usd Amount",
                scale=alt.Scale(zero=False, type=scale_type),
                title=f"Sales Amount ({currency})",
            ),
            size=alt.Size(
                "Sales Amount" if currency == "SOL" else "Usd Amount", title=f"Sales Amount ({currency})"
            ),
            color=alt.Color(
                "NFT Name",
                scale=alt.Scale(scheme="sinebow"),
            ),
            href="Explorer URL",
            tooltip=[
                alt.Tooltip("yearmonthdatehoursminutesseconds(Block Timestamp)"),
                alt.Tooltip("Purchaser"),
                alt.Tooltip("NFT Name"),
                alt.Tooltip("Mint"),
                alt.Tooltip("Sales Amount", title="Sales Amount (SOL)", format=",.2f"),
                alt.Tooltip("Usd Amount", title="Sales Amount (USD)", format=",.2f"),
            ],
            opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
        )
        .add_selection(legend_selection)
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

    st.write("---")
    st.subheader("Other NFT whales")
    st.write(
        "Explore 🐋 Addresses that purchase more than 50 NFTs in an hour, or spend more than 1000 SOL in an hour."
    )
    other_nft = whale_data_dict["nft_other"]
    total_sales_whales = (
        other_nft[other_nft.Type == "total_sales_count"]
        .sort_values(by="Value", ascending=False)
        .reset_index(drop=True)
    )
    rank_sales = (
        total_sales_whales.groupby("Purchaser")["Value"].count().sort_values(ascending=False).reset_index()
    )
    total_sales_whales["Purchaser Display"] = total_sales_whales["Purchaser"].apply(
        lambda x: f"{x[:4]}...{x[-4:]}" if x in rank_sales.Purchaser[:9].values else "Other"
    )
    total_amount_whales = (
        other_nft[other_nft.Type == "total_sales_amount"]
        .sort_values(by="Value", ascending=False)
        .reset_index(drop=True)
    )
    rank_amount = (
        total_amount_whales.groupby("Purchaser")["Value"].count().sort_values(ascending=False).reset_index()
    )
    total_amount_whales["Purchaser Display"] = total_amount_whales["Purchaser"].apply(
        lambda x: f"{x[:4]}...{x[-4:]}" if x in rank_amount.Purchaser[:9].values else "Other"
    )

    c1, c2 = st.columns(2)
    whale_type = c1.radio(
        "Choose a whale type:",
        ["More than 50 Purchases in 1 hour", "More than 1,000 SOL worth of purchases in 1 hour"],
        key="nft-whale-type",
        horizontal=False,
    )
    scale = c2.checkbox(
        "Log Scale",
        key="nft-whale-amount",
    )
    scale_type = "log" if scale else "linear"
    if whale_type == "More than 1,000 SOL worth of purchases in 1 hour":
        chart = (
            alt.Chart(total_amount_whales, title="NFT 🐋 Addresses by Total Purchase Amount, past 7d")
            .mark_circle(color="#FD5E53")
            .encode(
                x=alt.X("yearmonthdatehours(Datetime)", title=""),
                y=alt.Y(
                    "Value",
                    title="Total Hourly Purchase Amount (SOL)",
                    scale=alt.Scale(zero=False, type=scale_type),
                ),
                color=alt.Color(
                    "Purchaser Display",
                    title="Purchaser",
                    sort=alt.EncodingSortField(field="Value", op="max", order="descending"),
                    scale=alt.Scale(scheme="turbo"),
                ),
                size=alt.Size("Value", title="Hourly Purchase Amount (SOL)"),
                href="Explorer URL",
                tooltip=[
                    alt.Tooltip("yearmonthdatehoursminutesseconds(Datetime)"),
                    alt.Tooltip("Purchaser"),
                    alt.Tooltip("Value", title="Total Hourly Purchase Amount (SOL)", format=",.2f"),
                ],
            )
            .properties(height=600, width=600)
            .interactive()
        )
    else:
        chart = (
            alt.Chart(total_sales_whales, title="NFT 🐋 Addresses by Total Purchase Count, past 7d")
            .mark_circle(color="#FD5E53")
            .encode(
                x=alt.X("yearmonthdatehours(Datetime)", title=""),
                y=alt.Y(
                    "Value",
                    title="Total Hourly NFT Purchases",
                    scale=alt.Scale(zero=False, type=scale_type),
                ),
                color=alt.Color(
                    "Purchaser Display",
                    title="Purchaser",
                    sort=alt.EncodingSortField(field="Value", op="max", order="descending"),
                    scale=alt.Scale(scheme="turbo"),
                ),
                size=alt.Size("Value", title="Hourly NFT Purchases"),
                href="Explorer URL",
                tooltip=[
                    alt.Tooltip("yearmonthdatehoursminutesseconds(Datetime)"),
                    alt.Tooltip("Purchaser"),
                    alt.Tooltip("Value", title="Total Hourly NFT Purchases", format=","),
                ],
            )
            .properties(height=600, width=600)
            .interactive()
        )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("View and Download Data Table"):
        if whale_type == "More than 1,000 SOL worth of purchases in 1 hour":
            st.subheader("More than 1,000 SOL worth of purchases in 1 hour")
            st.write(total_amount_whales)
            slug = f"whales_nft_sales"
            st.download_button(
                "Click to Download",
                total_amount_whales.to_csv(index=False).encode("utf-8"),
                f"{slug}.csv",
                "text/csv",
                key=f"download-{slug}",
            )
        else:
            st.subheader("More than 50 Purchases in 1 hour")
            st.write(total_sales_whales)
            slug = f"whales_nft_purchases"
            st.download_button(
                "Click to Download",
                total_sales_whales.to_csv(index=False).encode("utf-8"),
                f"{slug}.csv",
                "text/csv",
                key=f"download-{slug}",
            )
