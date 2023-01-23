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

    Spire is currently a beta project and is in active development. Reach out on Twitter with questions and comments!

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi)
    """
)
c1.image(
    image,
    width=150,
)
st.write("---")

st.write("Click a tab below for an overview of a different aspect of the Solana ecosystem:")
ecosystem, nft, programs, defi = st.tabs(["Ecosystem", "NFT", "Programs", "DeFi"])

query_base = "https://next.flipsidecrypto.xyz/edit/queries"
api_base = "https://api.flipsidecrypto.com/api/v2/queries"
overview_query_dict = {
    # Ecosystem
    "Signers and Fee Payers": {
        "query": f"{query_base}/7d69821b-2a72-4a0d-afca-920a20d48a4d",
        "api": f"{api_base}/7d69821b-2a72-4a0d-afca-920a20d48a4d/data/latest",
        "datecols": ["DATE"],
    },
    "Transaction Volume": {
        "query": f"{query_base}/8a0a28fb-36f6-4308-a448-5661c45a1726",
        "api": f"{api_base}/8a0a28fb-36f6-4308-a448-5661c45a1726/data/latest",
        "datecols": ["DATE"],
    },
    "New Wallets": {
        "query": f"{query_base}/7add5aa7-da0a-41a1-9148-c3d49ce1baa4",
        "api": f"{api_base}/7add5aa7-da0a-41a1-9148-c3d49ce1baa4/data/latest",
        "datecols": ["SOLANA_FIRST_TX"],
    },
    "Fees": {
        "query": f"{query_base}/d27a2672-b2bb-4f55-abb0-6ce1ee982fd7",
        "api": f"{api_base}/d27a2672-b2bb-4f55-abb0-6ce1ee982fd7/data/latest",
        "datecols": ["DATE"],
    },
    # NFT
    "NFT Transactions": {
        "query": f"{query_base}/13b11f5b-0b50-498e-afa2-d59e5578e6f3",
        "api": f"{api_base}/13b11f5b-0b50-498e-afa2-d59e5578e6f3/data/latest",
        "datecols": ["DATE"],
    },
    # Defi
    "DeFi Swaps": {
        "query": f"{query_base}/76d039b3-edd1-4c5e-b2b6-014658b98b85",
        "api": f"{api_base}/76d039b3-edd1-4c5e-b2b6-014658b98b85/data/latest",
        "datecols": ["DATE"],
    },
}
overview_data_dict = {}
for k, v in overview_query_dict.items():
    overview_data_dict[k] = utils.load_overview_data(v["api"], v["datecols"])

with ecosystem:
    st.header("Ecosystem Overview")
    # #TODO:
    # st.write(
    #     f"""See the [Health Metrics](Health_Metrics) page for more in depth analysis.
    #     """
    # )
    c1, c2 = st.columns(2)
    # Unique Signers and Fee Payers
    chart = (
        alt.Chart(
            overview_data_dict["Signers and Fee Payers"],
            title=f"Unique Signers and Fee Payers: Daily, Past 60d",
        )
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
            x=alt.X("yearmonthdate(Date)", title="Date"),
            y=alt.Y("Wallets", stack=False),
            color=alt.Color(
                "Type",
                scale=alt.Scale(domain=["Signers", "Fee Payers"], range=["#4B3D60", "#FD5E53"]),
                sort="-y",
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Type"),
                alt.Tooltip("Wallets", format=","),
            ],
        )
        .properties(height=600, width=600)
        .interactive()
    )
    c1.altair_chart(chart, use_container_width=True)

    # Transaction Volume
    base = alt.Chart(
        overview_data_dict["Transaction Volume"],
        title=f"Transaction Volume: Daily, Past 60d (7d Moving Average)",
    ).encode(
        x=alt.X("yearmonthdate(Date):T", title="Date"),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date):T", title="Date"),
            alt.Tooltip("Transactions", format=","),
            alt.Tooltip("Moving Average", format=",.0f"),
        ],
    )
    bar = base.mark_bar(width=5, color="#FD5E53").encode(
        y=alt.Y("Transactions"),
    )
    line = base.mark_line(color="#FFE373").encode(y=alt.Y("Moving Average"))
    chart = (bar + line).interactive().properties(height=600).properties(width=600)
    c2.altair_chart(chart, use_container_width=True)

    # New Solana Wallets
    chart = (
        alt.Chart(overview_data_dict["New Wallets"], title=f"New Solana Wallets: Daily, Past 60d")
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
            x=alt.X("yearmonthdate(Solana First Tx)", title="Date"),
            y=alt.Y("New Wallets"),
            tooltip=[
                alt.Tooltip("yearmonthdate(Solana First Tx)", title="Date"),
                alt.Tooltip("New Wallets", format=","),
            ],
        )
        .properties(height=600, width=600)
        .interactive()
    )
    c1.altair_chart(chart, use_container_width=True)

    # Daily Fee per Tx
    chart = (
        alt.Chart(overview_data_dict["Fees"], title=f"Average Fees per Transaction: Daily, Past 60d")
        .mark_bar(width=5, color="#FD5E53")
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Fee Per Tx"),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Fee Per Tx"),
                alt.Tooltip("Total Fees Paid", format=",.2f"),
            ],
        )
        .properties(height=600, width=600)
        .interactive()
    )
    c2.altair_chart(chart, use_container_width=True)

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
        for k, v in overview_data_dict.items():
            if k.startswith("NFT") or k.startswith("DeFi"):
                continue
            st.subheader(k)
            st.write(v)
            slug = f"ecosystem_overview_{k.replace(' ', '_')}"
            st.download_button(
                "Click to Download",
                v.to_csv(index=False).encode("utf-8"),
                f"{slug}.csv",
                "text/csv",
                key=f"download-{slug}",
            )
            st.write("---")
        st.subheader("Users")
        combined_user_df = weekly_new_user_data.merge(weekly_user_data, on="WEEK")
        combined_user_df = (
            combined_user_df[["WEEK", "UNIQUE_USERS", "New Users", "Cumulative Users"]]
            .rename(columns={"WEEK": "Week", "UNIQUE_USERS": "Unique Users"})
            .sort_values(by="Week", ascending=False)
            .reset_index(drop=True)
        )
        st.write(combined_user_df)
        slug = f"ecosystem_overview_users"
        st.download_button(
            "Click to Download",
            combined_user_df.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )

with nft:
    st.header("NFT Ecosystem")

    st.write(
        f"""See the [NFT Royalties](NFT_Royalties) page for more in depth analysis.
        """
    )
    # Sales and Mints
    currency = st.radio("Choose a Currency:", ["SOL", "USD"], key="nft-currency", horizontal=True)
    chart = (
        alt.Chart(overview_data_dict["NFT Transactions"], title="NFT Sales and Mints Volume: Daily, Past 60d")
        .mark_bar(width=10)
        .encode(
            x=alt.X("yearmonthdate(Date)", title="Date"),
            y=alt.Y(f"Nft Volume {currency.title()}", title=f"NFT Volume ({currency})"),
            color=alt.Color(
                "Type",
                title="Purchase Type",
                scale=alt.Scale(domain=["NFT Mints", "NFT Sales"], range=["#4B3D60", "#FD5E53"]),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Type", title="Purchase Type"),
                alt.Tooltip("Nft Volume Sol", title=f"NFT Volume (SOL)", format=",.2f"),
                alt.Tooltip("Nft Volume Usd", title=f"NFT Volume (USD)", format=",.2f"),
                alt.Tooltip("Nft Txs", title="Transaction Count", format=","),
                alt.Tooltip("Nft Buyers", title="NFT Buyers", format=","),
            ],
        )
        .properties(height=600, width=600)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
    st.write("---")
    c1, c2 = st.columns(2)
    # Unique Purchasers
    chart = (
        alt.Chart(
            overview_data_dict["NFT Transactions"], title=f"Unique NFT Purchasing Addresses: Daily, Past 60d"
        )
        .mark_line()
        .encode(
            x=alt.X("yearmonthdate(Date)", title="Date"),
            y=alt.Y("Nft Buyers", title="NFT Buyers"),
            color=alt.Color(
                "Type",
                title="Purchase Type",
                scale=alt.Scale(domain=["NFT Mints", "NFT Sales"], range=["#4B3D60", "#FD5E53"]),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Type", title="Purchase Type"),
                alt.Tooltip("Nft Buyers", title="NFT Buyers", format=","),
                alt.Tooltip("Nft Volume Sol", title=f"NFT Volume (SOL)", format=",.2f"),
                alt.Tooltip("Nft Volume Usd", title=f"NFT Volume (USD)", format=",.2f"),
                alt.Tooltip("Nft Txs", title="Transaction Count", format=","),
            ],
        )
        .properties(height=600, width=600)
        .interactive()
    )
    c1.altair_chart(chart, use_container_width=True)
    # Sales and Mints: Tx Volume
    chart = (
        alt.Chart(
            overview_data_dict["NFT Transactions"],
            title="NFT Sales and Mints Transaction Count: Daily, Past 60d",
        )
        .mark_bar(width=5)
        .encode(
            x=alt.X("yearmonthdate(Date)", title="Date"),
            y=alt.Y("Nft Txs", title="Transaction Count"),
            color=alt.Color(
                "Type",
                title="Purchase Type",
                scale=alt.Scale(domain=["NFT Mints", "NFT Sales"], range=["#4B3D60", "#FD5E53"]),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Type", title="Purchase Type"),
                alt.Tooltip("Nft Txs", title="Transaction Count", format=","),
                alt.Tooltip("Nft Volume Sol", title=f"NFT Volume (SOL)", format=",.2f"),
                alt.Tooltip("Nft Volume Usd", title=f"NFT Volume (USD)", format=",.2f"),
                alt.Tooltip("Nft Buyers", title="NFT Buyers", format=","),
            ],
        )
        .properties(height=600, width=600)
        .interactive()
    )
    c2.altair_chart(chart, use_container_width=True)
    with st.expander("View and Download Data Table"):
        for k, v in overview_data_dict.items():
            if k.startswith("NFT"):
                st.subheader(k)
                st.write(v)
                slug = f"ecosystem_overview_nft"
                st.download_button(
                    "Click to Download",
                    v.to_csv(index=False).encode("utf-8"),
                    f"{slug}.csv",
                    "text/csv",
                    key=f"download-{slug}",
                )

with programs:
    st.header("Programs")
    st.write(
        f"""See the [Program Activity](Program_Activity) page for more in depth analysis.
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
        st.subheader("Programs")
        st.write(combined_program_df)
        slug = f"ecosystem_overview_programs"
        st.download_button(
            "Click to Download",
            combined_program_df.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )

with defi:

    def combine_swap_program_names(val):
        if val.lower().startswith("raydium"):
            return "Raydium"
        elif val.lower().startswith("orca"):
            if "whirlpool" in val.lower():
                return "Orca Whirlpool"
            else:
                return "Orca"
        elif val.lower().startswith("jupiter"):
            return "Jupiter"
        elif val.lower().startswith("saber"):
            return "Saber"
        else:
            return val.title()

    defi_data = overview_data_dict["DeFi Swaps"].copy()
    defi_data["Swap Program Normalized"] = defi_data["Swap Program"].apply(combine_swap_program_names)
    defi_data_grouped = (
        defi_data.groupby(["Date", "Swap Program Normalized"])[["Daily Txs", "Swapper"]].sum().reset_index()
    )

    c1, c2 = st.columns(2)
    # Swap Tx
    chart = (
        alt.Chart(defi_data_grouped, title=f"DeFi Swap Transactions by Program: Daily, Past 60d")
        .mark_bar(width=4)
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Daily Txs", title="Transaction Count"),
            order=alt.Order("Daily Txs", sort="descending"),
            color=alt.Color(
                "Swap Program Normalized",
                title="Swap Program",
                scale=alt.Scale(scheme="sinebow"),
                sort=alt.EncodingSortField(field="Daily Txs", op="max", order="ascending"),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Swap Program Normalized", title="Swap Program"),
                alt.Tooltip("Daily Txs", title="Transaction Count", format=","),
                alt.Tooltip("Swapper", title="Unique Users", format=","),
            ],
        )
        .properties(height=600, width=600)
        .interactive()
    )
    c1.altair_chart(chart, use_container_width=True)
    # Unique addresses
    chart = (
        alt.Chart(defi_data_grouped, title=f"DeFi Unique Wallet Addresses by Program: Daily, Past 60d")
        .mark_bar(width=4)
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Swapper", title="Unique Wallet Addresses"),
            order=alt.Order("Swapper", sort="descending"),
            color=alt.Color(
                "Swap Program Normalized",
                title="Swap Program",
                scale=alt.Scale(scheme="sinebow"),
                sort=alt.EncodingSortField(field="Swapper", op="max", order="ascending"),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Swap Program Normalized", title="Swap Program"),
                alt.Tooltip("Daily Txs", title="Transaction Count", format=","),
                alt.Tooltip("Swapper", title="Unique Users", format=","),
            ],
        )
        .properties(height=600, width=600)
        .interactive()
    )
    c2.altair_chart(chart, use_container_width=True)

    with st.expander("View and Download Data Table"):
        st.subheader("DeFi Swaps - Grouped")
        st.write(defi_data_grouped)
        slug = f"ecosystem_overview_defi_grouped"
        st.download_button(
            "Click to Download",
            defi_data_grouped.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
        st.write("---")
        st.subheader("DeFi Swaps - Raw")
        st.write(defi_data)
        slug = f"ecosystem_overview_defi_raw"
        st.download_button(
            "Click to Download",
            defi_data.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
