import datetime

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from st_pages import _get_page_hiding_code

import spire_fyi.charts as charts
import spire_fyi.utils as utils

alt.data_transformers.disable_max_rows()
image = Image.open("assets/images/spire_logo.png")

st.set_page_config(
    page_title="Spire | A viewpoint above Solana data",
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
    
    Spire is a Solana-focused on-chain data platform that aims to provide in-depth data and insights to add value to the Solana ecosystem.

    Spire is currently a beta project and is in active development. Reach out on Twitter with questions and comments!

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi) | Donations: GvvrKbq21eTkknHRt9FGVFN54pLWXSSo4D4hz2i1JCn5 , or contribute on [Stockpile](https://www.stockpile.pro/projects/fMqAvbsrWseJji8QyNOf)
    """
)
c1.image(
    image,
    width=150,
)
st.write("---")

with st.expander("Instructions"):
    st.write(
        """
    - Click a tab below for an overview of a different aspect of the Solana ecosystem.
    - Go to a page on the Sidebar for more in depth analyses.
    """
    )
ecosystem, nft, programs, defi = st.tabs(["Ecosystem", "NFT", "Programs", "DeFi"])

query_base = utils.query_base
api_base = utils.api_base
overview_query_dict = {
    # Ecosystem
    "Signers and Fee Payers": {
        "query": f"{query_base}/7d69821b-2a72-4a0d-afca-920a20d48a4d",
        "api": f"{api_base}/7d69821b-2a72-4a0d-afca-920a20d48a4d/data/latest",
        "datecols": ["DATE"],
    },
    "Signers and Fee Payers: Successful Transactions only": {
        "query": f"{query_base}/31cc9e11-9c2a-468e-8e63-cea1460fc19b",
        "api": f"{api_base}/31cc9e11-9c2a-468e-8e63-cea1460fc19b/data/latest",
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
        "query": f"{query_base}/e70e50fb-3a78-40b9-adc4-debb1888967f",
        "api": f"{api_base}/e70e50fb-3a78-40b9-adc4-debb1888967f/data/latest",
        "datecols": ["DATE"],
    },
    # NFT
    "NFT Transactions": {
        "query": f"{query_base}/13b11f5b-0b50-498e-afa2-d59e5578e6f3",
        "api": f"{api_base}/13b11f5b-0b50-498e-afa2-d59e5578e6f3/data/latest",
        "datecols": ["DATE"],
    },
    # Crosschain
    "Crosschain measures": {
        "query": f"{query_base}/0f67a62d-5d50-43b9-a7d1-7826cc78571c",
        "api": f"{api_base}/0f67a62d-5d50-43b9-a7d1-7826cc78571c/data/latest",
        "datecols": ["DATE"],
    },
    # Defi
    # NOTE: using self-maintained queries
    # "DeFi Swaps": {
    #     "query": f"{query_base}/76d039b3-edd1-4c5e-b2b6-014658b98b85",
    #     "api": f"{api_base}/76d039b3-edd1-4c5e-b2b6-014658b98b85/data/latest",
    #     "datecols": ["DATE"],
    # },
}
overview_data_dict = {}
for k, v in overview_query_dict.items():
    overview_data_dict[k] = utils.load_flipside_api_data(v["api"], v["datecols"])
overview_data_dict["Fees"] = (
    overview_data_dict["Fees"]
    .copy()
    .rename(
        columns={
            "99Th Percentile": "99th Percentile",
            "95Th Percentile": "95th Percentile",
            "Average": "Mean",
        }
    )
)

with ecosystem:
    st.header("Ecosystem Overview")
    succeeded_only = st.checkbox("Successful transactions only", key="succeeded_tx")
    if succeeded_only:
        signers_data = overview_data_dict["Signers and Fee Payers: Successful Transactions only"]
        title = "Unique Signers and Fee Payers, Successful transactions only: Daily, Past 60d"
    else:
        signers_data = overview_data_dict["Signers and Fee Payers"]
        title = f"Unique Signers and Fee Payers: Daily, Past 60d"
    # #TODO:
    # st.write(
    #     f"""See the [Health Metrics](Health_Metrics) page for more in depth analysis.
    #     """
    # )
    c1, c2 = st.columns(2)
    # Unique Signers and Fee Payers
    chart = (
        alt.Chart(signers_data, title=title)
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
    )
    c1.altair_chart(chart, use_container_width=True)
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
    )
    c2.altair_chart(chart, use_container_width=True)
    st.write("---")
    c1, c2 = st.columns(2)
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
    chart = (bar + line).properties(height=600).properties(width=600)
    c1.altair_chart(chart, use_container_width=True)

    # Daily Fee per Tx
    scale = c2.checkbox(
        "Log Scale",
        key="fee-per-tx-scale",
    )
    scale_type = "log" if scale else "linear"
    melted_fees = overview_data_dict["Fees"].melt(id_vars=["Date", "Txs", "Total Fees Paid"])
    columns = sorted(melted_fees["variable"].unique())
    base = alt.Chart(melted_fees, title=f"Fees per Transaction: Daily, Past 60d").encode(
        x=alt.X("yearmonthdate(Date):T", title=None)
    )
    selection = alt.selection_point(
        fields=["Date"],
        nearest=True,
        on="mouseover",
        empty=False,
        clear="mouseout",
    )
    legend_selection = alt.selection_point(fields=["variable"], bind="legend")
    lines = base.mark_line().encode(
        y=alt.Y(
            f"value",
            title="Fee per Transaction",
            scale=alt.Scale(type=scale_type),
        ),
        color=alt.Color(
            "variable:N",
            title="Metric",
            scale=alt.Scale(
                domain=columns,
                range=[
                    "#FC9C54",
                    "#FD5E53",
                    "#FFE373",
                    "#4B3D60",
                ],
            ),
            # sort=alt.EncodingSortField("value", op="count", order="descending"),
        ),
        opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
    )
    points = lines.mark_point(size=1).transform_filter(selection)
    rule = (
        base.transform_pivot("variable", value="value", groupby=["Date"])
        .mark_rule(color="#983832")
        .encode(
            opacity=alt.condition(selection, alt.value(0.3), alt.value(0)),
            tooltip=[alt.Tooltip("yearmonthdate(Date)", title="Date")]
            + [
                alt.Tooltip(
                    c,
                    type="quantitative",
                    format=".6f",
                )
                for c in columns
            ],
        )
        .add_params(selection)
    )
    chart = (lines + points + rule).add_params(legend_selection).properties(height=550, width=600)
    c2.altair_chart(chart, use_container_width=True)
    st.write("---")

    fees = utils.load_fee_data()
    c1, c2 = st.columns(2)
    fee_date_range = c2.radio(
        "Date range:",
        ["60d", "30d", "14d", "7d", "1d"],
        key="fees_burned",
        horizontal=True,
        index=1,
    )

    # Total Fee and Burns
    chart = (
        alt.Chart(
            fees[
                fees.Date >= (pd.to_datetime(fees.Date.max(), utc=True) - pd.Timedelta(fee_date_range))
            ].melt(id_vars="Date"),
            title=f"Total Fees and Fees Burned, Past {fee_date_range}",
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
            y=alt.Y("value", stack=False, title="Transaction Fees (SOL)"),
            color=alt.Color(
                "variable",
                scale=alt.Scale(domain=["Fees", "Burn"], range=["#4B3D60", "#FD5E53"]),
                sort="-y",
                title="Type",
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("variable", title="Type"),
                alt.Tooltip("value", format=",.2f"),
            ],
        )
        .properties(height=600, width=600)
    )
    c1.altair_chart(chart, use_container_width=True)

    price = utils.load_sol_daily_price()
    most_recent_price = price.iloc[-1]["Price (USD)"]
    fees_in_range = fees[
        fees.Date >= (pd.to_datetime(fees.Date.max(), utc=True) - pd.Timedelta(fee_date_range))
    ].copy()
    c2.metric(
        f"Total Fees in Past {fee_date_range[:-1]} days",
        f"{fees_in_range.Fees.sum():,.0f} SOL (${fees_in_range.Fees.sum() * most_recent_price:,.0f})",
    )
    c2.metric(
        f"Fees Burned in Past {fee_date_range[:-1]} days 🔥🔥🔥",
        f"{fees_in_range.Burn.sum():,.0f} SOL (${fees_in_range.Burn.sum() * most_recent_price:,.0f})",
    )
    c2.caption(
        "Fees shown here are from both **vote and non-vote transactions**. Currently, 50% of each transaction fee is burned, while the rest goes to validators. See [here](https://docs.solana.com/transaction_fees) for more details."
    )
    st.write("---")
    user_type = st.radio(
        "Choose a user type", ["Fee Payers", "Signers"], key="weekly_user_type", horizontal=True
    )
    c1, c2 = st.columns(2)
    # TODO: add in option for success/fail?
    weekly_user_data = utils.load_weekly_user_data(user_type)
    weekly_new_user_data = utils.load_weekly_new_user_data(user_type)
    unique_user_chart = charts.alt_weekly_unique_chart(
        weekly_user_data[weekly_user_data.WEEK > "2020-10-01"],
        f"Unique {user_type}: Weekly",
        "UNIQUE_USERS",
        f"Unique {user_type}",
    )
    c1.altair_chart(unique_user_chart, use_container_width=True)
    new_user_chart = charts.alt_weekly_cumulative_chart(
        weekly_new_user_data[weekly_new_user_data.WEEK > "2020-10-01"],
        f"New {user_type}: Weekly",
        "New Users",
        "Cumulative Users",
    )
    c2.altair_chart(new_user_chart, use_container_width=True)

    st.subheader("Crosschain Comparison")

    c1, c2 = st.columns(2)
    date_range = c1.radio(
        "Date range:",
        ["90d", "60d", "30d", "14d", "7d"],
        key="crosschain_date_range",
        horizontal=True,
        index=2,
    )
    metric = c2.radio(
        "Choose a metric:",
        ["Wallets", "Txs"],
        format_func=lambda x: utils.metric_dict[x],
        horizontal=True,
        index=1,
        key="program_metric",
    )
    log_scale = c2.checkbox("Log Scale", key="crosschain_log_scale")

    chart_df = overview_data_dict["Crosschain measures"].copy()
    chart_df = chart_df[
        chart_df.Date >= (pd.to_datetime(datetime.datetime.today(), utc=True) - pd.Timedelta(date_range))
    ]
    chart = charts.alt_line_chart(
        chart_df,
        metric=metric,
        log_scale=log_scale,
        unique_column_name="Label",
        interactive=False,
        legend_title=utils.metric_dict[metric],
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("View and Download Data Table"):
        for k, v in overview_data_dict.items():
            if k.startswith("NFT") or k.startswith("DeFi"):
                continue
            elif k.startswith("Fees"):
                st.subheader(k)
                fee_df = v.copy().merge(fees, on="Date")
                fee_df = fee_df.rename(
                    columns={
                        "Total Fees Paid": "Fees from Transactions",
                        "Fees": "Total Fees",
                        "Burn": "Fees Burned",
                    }
                )
                fee_df = fee_df[
                    [
                        "Date",
                        "Txs",
                        "Fees from Transactions",
                        "Total Fees",
                        "Fees Burned",
                        "Mean",
                        "99th Percentile",
                        "95th Percentile",
                        "Median",
                    ]
                ]
                st.write(fee_df)
                slug = f"ecosystem_overview_{k.replace(' ', '_')}"
                st.download_button(
                    "Click to Download",
                    fee_df.to_csv(index=False).encode("utf-8"),
                    f"{slug}.csv",
                    "text/csv",
                    key=f"download-{slug}",
                )
            else:
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
        st.subheader(f"Users: {user_type}")
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
    st.header("DeFi")
    dex_info, dex_new_user, dex_signers_fee_payers = utils.load_defi_data()
    with st.expander("Expand to see DeFi protocols and their Program IDs"):
        for k, v in utils.dex_programs.items():
            progs = ""
            for x in v:
                progs += f"- [{x}](https://solana.fm/address/{x})\n"
            st.write(f"**{k}**\n{progs}")
    st.subheader("Transaction and User Overview")
    date_range = st.radio(
        "Choose a date range:",
        [
            "180d",
            "90d",
            "60d",
            "30d",
            "14d",
            "7d",
        ],
        horizontal=True,
        index=2,
        key="defi_date_range",
    )
    tx_data, user_data = utils.agg_defi_data(dex_info, date_range)
    c1, c2 = st.columns(2)
    chart = (
        alt.Chart(tx_data, title=f"DeFi Transactions by Protocol: Daily, Past {date_range}")
        .mark_area(
            interpolate="monotone",
        )
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Txs", title="Transaction Count"),
            order=alt.Order("Rank", sort="descending"),
            color=alt.Color(
                "Dex Grouped by Tx",
                title="DeFi Protocol",
                scale=alt.Scale(scheme="turbo"),
                sort=alt.EncodingSortField(field="Txs", op="mean", order="descending"),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Dex Grouped by Tx", title="DeFi Protocol"),
                alt.Tooltip("Txs", title="Transaction Count", format=","),
                alt.Tooltip("Fee Payers", title="Unique Users", format=","),
                alt.Tooltip("Normalized", title="Transaction Count Percentage", format=".1%"),
            ],
        )
        .properties(height=600, width=600)
        .interactive(bind_x=False)
    )
    c1.altair_chart(chart, use_container_width=True)
    chart = (
        alt.Chart(user_data, title=f"DeFi Unique Fee Payers by Protocol: Daily, Past {date_range}")
        .mark_area(
            interpolate="monotone",
        )
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Fee Payers", title="Unique Fee Payers"),
            order=alt.Order("Rank", sort="descending"),
            color=alt.Color(
                "Dex Grouped by Fee Payer",
                title="DeFi Protocol",
                scale=alt.Scale(scheme="turbo"),
                sort=alt.EncodingSortField(field="Fee Payers", op="mean", order="descending"),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Dex Grouped by Fee Payer", title="DeFi Protocol"),
                alt.Tooltip("Txs", title="Transaction Count", format=","),
                alt.Tooltip("Fee Payers", title="Unique Fee Payers", format=","),
                alt.Tooltip("Normalized", title="Unique Fee Payers Percentage", format=".1%"),
            ],
        )
        .properties(height=600, width=600)
        .interactive(bind_x=False)
    )
    c2.altair_chart(chart, use_container_width=True)

    chart = (
        alt.Chart(tx_data)
        .mark_area(
            interpolate="monotone",
        )
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Txs", title="Transaction Count", stack="normalize"),
            order=alt.Order("Rank", sort="descending"),
            color=alt.Color(
                "Dex Grouped by Tx",
                title="DeFi Protocol",
                scale=alt.Scale(scheme="turbo"),
                sort=alt.EncodingSortField(field="Txs", op="mean", order="descending"),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Dex Grouped by Tx", title="DeFi Protocol"),
                alt.Tooltip("Txs", title="Transaction Count", format=","),
                alt.Tooltip("Fee Payers", title="Unique Users", format=","),
                alt.Tooltip("Normalized", title="Transaction Count Percentage", format=".1%"),
            ],
        )
        .properties(height=600, width=600)
        .interactive(bind_x=False)
    )
    c1.altair_chart(chart, use_container_width=True)
    chart = (
        alt.Chart(user_data)
        .mark_area(
            interpolate="monotone",
        )
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Fee Payers", title="Unique Fee Payers", stack="normalize"),
            order=alt.Order("Rank", sort="descending"),
            color=alt.Color(
                "Dex Grouped by Fee Payer",
                title="DeFi Protocol",
                scale=alt.Scale(scheme="turbo"),
                sort=alt.EncodingSortField(field="Fee Payers", op="mean", order="descending"),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Dex Grouped by Fee Payer", title="DeFi Protocol"),
                alt.Tooltip("Txs", title="Transaction Count", format=","),
                alt.Tooltip("Fee Payers", title="Unique Fee Payers", format=","),
                alt.Tooltip("Normalized", title="Unique Fee Payers Percentage", format=".1%"),
            ],
        )
        .properties(height=600, width=600)
        .interactive(bind_x=False)
    )
    c2.altair_chart(chart, use_container_width=True)

    st.subheader("Detailed User Information")
    c1, c2 = st.columns(2)
    date_range = c1.radio(
        "Choose a date range:",
        [
            "180d",
            "90d",
            "60d",
            "30d",
            "14d",
            "7d",
        ],
        horizontal=True,
        index=2,
        key="defi_users_date_range",
    )
    protocol = c2.selectbox(
        "Choose a Protocol:",
        sorted(dex_signers_fee_payers.Dex.unique()),
        index=5,
        key="signers_fee_payers_select",
    )
    defi_signers = utils.agg_defi_signers_data(dex_signers_fee_payers, date_range, protocol)
    chart = (
        alt.Chart(defi_signers, title=f"Total Signers vs Fee Payers, {protocol}: Daily, Past {date_range}")
        .mark_area()
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Wallets", title="Unique Wallet Addresses"),
            color=alt.Color(
                "Type",
                title="User Type",
                scale=alt.Scale(domain=["Fee Payers", "Signers"], range=["#4B3D60", "#FD5E53"]),
                sort="-y",
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Wallets", title="Unique Wallet Addresses", format=","),
                alt.Tooltip("Type", title="User Type"),
                alt.Tooltip("Normalized", title="Unique Wallet Addresses Percentage", format=".1%"),
            ],
        )
        .properties(height=600, width=600)
    )
    c1.altair_chart(chart, use_container_width=True)
    chart = (
        alt.Chart(
            defi_signers,
            title=f"Total Signers vs Fee Payers Percentage, {protocol}: Daily, Past {date_range}",
        )
        .mark_area()
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y("Wallets", title="Unique Wallet Addresses", stack="normalize"),
            color=alt.Color(
                "Type",
                title="User Type",
                scale=alt.Scale(domain=["Fee Payers", "Signers"], range=["#4B3D60", "#FD5E53"]),
                sort="-y",
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("Wallets", title="Unique Wallet Addresses", format=","),
                alt.Tooltip("Type", title="User Type"),
                alt.Tooltip("Normalized", title="Unique Wallet Addresses Percentage", format=".1%"),
            ],
        )
        .properties(height=600, width=600)
    )
    c2.altair_chart(chart, use_container_width=True)

    new_defi_users = utils.agg_new_defi_users_data(dex_new_user, date_range, protocol)
    chart = (
        alt.Chart(
            new_defi_users,
            title=f"New Users of {protocol}: Daily, Past {date_range}",
        )
        .mark_bar(color="#FD5E53")
        .encode(
            x=alt.X("yearmonthdate(First Tx Date)", title="Date"),
            y=alt.Y("New Wallets", title="Wallets"),
            tooltip=[
                alt.Tooltip("yearmonthdate(First Tx Date)", title="Date"),
                alt.Tooltip("New Wallets", title="Wallets", format=","),
                alt.Tooltip("Program Id"),
            ],
            color="Program Id",
            href="url",
        )
        .properties(height=600, width=600)
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("View and Download Data Table"):
        st.subheader("Defi Data - Raw")
        st.write("**Protocol Info**")
        st.write(dex_info)
        slug = f"ecosystem_overview_defi_protocol_info"
        st.download_button(
            "Click to Download",
            dex_info.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
        st.write("**Signers and Fee Payers by Protocol**")
        st.write(dex_signers_fee_payers)
        slug = f"ecosystem_overview_defi_signers_fee_payers"
        st.download_button(
            "Click to Download",
            dex_signers_fee_payers.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
        st.write("**New Users by Protocol**")
        st.write(dex_new_user)
        slug = f"ecosystem_overview_defi_new_users"
        st.download_button(
            "Click to Download",
            dex_new_user.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
        st.write("---")

        st.subheader("Defi Data - Aggregated")
        st.write("**Protocol Info -- Transaction data**")
        st.write(tx_data)
        slug = f"ecosystem_overview_defi_protocol_info_tx"
        st.download_button(
            "Click to Download",
            tx_data.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
        st.write("**Protocol Info -- User data**")
        st.write(user_data)
        slug = f"ecosystem_overview_defi_protocol_info_user"
        st.download_button(
            "Click to Download",
            user_data.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
        st.write(f"**Signers and Fee Payers for {protocol}, past {date_range}**")
        st.write(defi_signers)
        slug = f"ecosystem_overview_defi_signers_fee_payers_{protocol}_{date_range}"
        st.download_button(
            "Click to Download",
            defi_signers.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
        st.write(f"**New Users for {protocol}, past {date_range}**")
        st.write(new_defi_users)
        slug = f"ecosystem_overview_defi_new_users_{protocol}_{date_range}"
        st.download_button(
            "Click to Download",
            new_defi_users.to_csv(index=False).encode("utf-8"),
            f"{slug}.csv",
            "text/csv",
            key=f"download-{slug}",
        )
