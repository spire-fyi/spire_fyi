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
    A viewpoint above Solana data. Insights and on-chain data analytics, inspired by the community and accessible to all. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/), [Helius](https://helius.xyz/) and [SolanaFM APIs](https://docs.solana.fm/).

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi) | Donations: GvvrKbq21eTkknHRt9FGVFN54pLWXSSo4D4hz2i1JCn5
    """
)
c1.image(
    image,
    width=100,
)
st.write("---")
st.header("Program Analysis")
st.write("Explore Program usage across various dimensions!")
with st.expander("Instructions"):
    st.write(
        """
    - Select a date range, and use the slider to choose the number of programs.
    - View the Number of signers for a Program address, or the Transaction Count for each Program.
    - Select the method for determining top Programs: average, total (sum), or max within the date range.
    - Choose `Selected Programs` to pick specific Program addresses from a list if you have one in mind.
    - By default, Solana System Programs and Oracles are exclude. Uncheck these if you want to see their metrics.
    - Interested in what programs new users interact with? Check the `New Users Only` box to view the metrics only for wallet addresses which signed their first transaction on that day.
    - `Shift-Click` on Program Name(s) in the legend to focus on selected programs only.
    ---
    """
    )

c1, c2, c3, c4 = st.columns(4)
metric = c1.radio(
    "Choose a metric",
    utils.metric_dict.keys(),
    format_func=lambda x: utils.metric_dict[x],
    horizontal=True,
    index=1,
    key="program_metric",
)
agg_method = c2.radio(
    "Choose an aggregtion method",
    utils.agg_method_dict.keys(),
    format_func=lambda x: utils.agg_method_dict[x],
    horizontal=True,
    key="program_agg_method",
)
chart_type = c3.radio(
    "Choose how to view data",
    ["Top Programs", "Selected Programs"],
    horizontal=True,
    key="program_chart_type",
)
exclude_solana = c4.checkbox("Exclude Solana System Programs", key="program_exclude_solana", value=True)
exclude_oracle = c4.checkbox("Exclude Oracle Programs", key="program_exclude_oracle", value=True)
new_users_only = c4.checkbox("New Users Only", key="program_new_users")
log_scale = c4.checkbox("Log Scale", key="program_log_scale")
st.write("---")
df = utils.load_labeled_program_data(new_users_only=new_users_only)
df["Date"] = pd.to_datetime(df["Date"])
c1, c2 = st.columns(2)
date_range = c1.radio(
    "Choose a date range:",
    [  # #TODO: not doing more dates until more data is queried
        # "All dates",
        # "Year to Date",
        # "180d",
        "90d",
        "60d",
        "30d",
        "14d",
        "7d",
    ],
    horizontal=True,
    index=2,
    key="program_date_range",
)
if chart_type == "Top Programs":
    programs = c2.slider("Number of Programs", 1, 30, 10, key="program_slider")
else:
    programs = c2.multiselect(
        "Choose which Program IDs to look at (random selections chosen)",
        df.PROGRAM_ID.unique(),
        key="program_multiselect",
    )
    if not programs:
        programs = np.random.choice(df.PROGRAM_ID.unique(), 5)

chart_df = utils.get_program_chart_data(
    df, metric, agg_method, date_range, exclude_solana, exclude_oracle, programs
)
chart_df["Name"] = chart_df.apply(
    utils.apply_program_name,
    axis=1,
)
chart_df["Explorer Site"] = chart_df.PROGRAM_ID.apply(lambda x: f"https://solana.fm/address/{x}")

chart = charts.alt_line_chart(chart_df, metric, log_scale)
st.altair_chart(chart, use_container_width=True)

with st.expander("View and Download Data Table"):
    chart_df = (
        chart_df[
            [
                "Date",
                "Name",
                "TX_COUNT",
                "SIGNERS",
                "PROGRAM_ID",
                "LABEL_TYPE",
                "LABEL_SUBTYPE",
                "LABEL",
                "ADDRESS_NAME",
                "FriendlyName",
                "Abbreviation",
                "Category",
                "LogoURI",
                "Explorer Site",
            ]
        ]
        .sort_values(by=["Date", metric], ascending=False)
        .rename(
            columns={
                "PROGRAM_ID": "Program ID",
                "TX_COUNT": "Transaction Count",
                "SIGNERS": "Signer Count",
                "LABEL_TYPE": "Flipside Label Type",
                "LABEL_SUBTYPE": "Flipside Label Subtype",
                "LABEL": "Flipside Label",
                "ADDRESS_NAME": "Flipside Address Name",
                "FriendlyName": "SolanaFM Address Name",
                "Abbreviation": "SolanaFM Abbreviation",
                "Category": "SolanaFM Category",
            }
        )
        .reset_index(drop=True)
    )
    st.write(chart_df)
    if type(programs) == int:
        chart_type_str = f"top{programs}"
    else:
        chart_type_str = "selected"
    if new_users_only:
        chart_type_str += "_new_users"
    st.download_button(
        "Click to Download",
        chart_df.to_csv(index=False).encode("utf-8"),
        f"program_ids_{chart_type_str}_{agg_method}_{date_range.replace(' ', '')}_{metric}.csv",
        "text/csv",
        key="download-program-ids",
    )
st.write("---")
st.subheader("Deep dive")
st.write("View more details on any Program ID by entering an address below.")
progam_usage_query = """
--sql
select 
    date(block_timestamp) as date,
    count(distinct tx_id) as txs,
    count(distinct signers[0]) as active_wallets, --fee payers
    (txs/active_wallets) as txs_per_user
from solana.core.fact_events
where 
    date between current_date() - 61 and current_date() - 1
    and program_id = '{param}'
group by 1 
;
"""

new_wallets_for_program = """
--sql
with first_tx as (
    select 
        signers[0] as wallet,
        min(date(block_timestamp)) as first_tx_date
    from
        solana.core.fact_events 
    where 
        program_id = '{param}'
    group by 
        1
),
new_wallets AS (
    SELECT
        first_tx_date,
        count(distinct wallet) as new_wallets
    FROM
        first_tx 
    WHERE
        first_tx_date between CURRENT_DATE() - 61 and current_date() - 1
    GROUP BY
    1 
)
select
    *
from
    new_wallets
;
"""
program_id = st.text_input("Enter a program address", chart_df.iloc[0]["Program ID"])
data_load_state = st.text("Querying data for program address...")
program_usage_data = utils.run_query_and_cache("program_usage", progam_usage_query, program_id)
new_wallet_data = utils.run_query_and_cache("new_wallet", new_wallets_for_program, program_id)
data_load_state.text("")

program_usage_data = utils.reformat_columns(program_usage_data, datecols=["DATE"])
new_wallet_data = utils.reformat_columns(new_wallet_data, datecols=["FIRST_TX_DATE"])
c1, c2 = st.columns(2)
# Daily Active Users
chart = (
    alt.Chart(
        program_usage_data,
        title=f"Daily Active Wallets for {utils.get_short_address(program_id)}: Daily, Past 60d",
    )
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
        y=alt.Y("Active Wallets", title="Wallets", scale=alt.Scale(nice=False)),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            alt.Tooltip("Active Wallets", title="Wallets", format=","),
            alt.Tooltip("Txs", title="Transactions", format=","),
            alt.Tooltip("Txs Per User", title="Transactions per User", format=",.2f"),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
c1.altair_chart(chart, use_container_width=True)
# New Wallets
chart = (
    alt.Chart(
        new_wallet_data,
        title=f"New Wallets Interacting with {utils.get_short_address(program_id)}: Daily, Past 60d",
    )
    .mark_area(
        line={"color": "#4B3D60", "size": 1},
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="#4B3D60", offset=1),
                alt.GradientStop(color="#FD5E53", offset=0),
            ],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
        interpolate="monotone",
    )
    .encode(
        x=alt.X("yearmonthdate(First Tx Date)", title="Date"),
        y=alt.Y("New Wallets", scale=alt.Scale(domain=[0, program_usage_data["Active Wallets"].max()])),
        tooltip=[
            alt.Tooltip("yearmonthdate(First Tx Date)", title="Date"),
            alt.Tooltip("New Wallets", title="Wallets", format=","),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
# Transaction Count
c2.altair_chart(chart, use_container_width=True)
st.write("---")
chart = (
    alt.Chart(
        program_usage_data,
        title=f"Transaction Count for {utils.get_short_address(program_id)}: Daily, Past 60d",
    )
    .mark_line(width=5, color="#FD5E53")
    .encode(
        x=alt.X("yearmonthdate(Date)", title="Date"),
        y=alt.Y("Txs", title="Transaction Count"),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            alt.Tooltip("Active Wallets", title="Wallets", format=","),
            alt.Tooltip("Txs", title="Transactions", format=","),
            alt.Tooltip("Txs Per User", title="Transactions per User", format=",.2f"),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
c1.altair_chart(chart, use_container_width=True)
# Tx to User Ratio
chart = (
    alt.Chart(
        program_usage_data,
        title=f"Transaction to User Ratio for {utils.get_short_address(program_id)}: Daily, Past 60d",
    )
    .mark_line(width=5, color="#FFE373")
    .encode(
        x=alt.X("yearmonthdate(Date)", title="Date"),
        y=alt.Y("Txs Per User", title="Transactions per User"),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            alt.Tooltip("Active Wallets", title="Wallets", format=","),
            alt.Tooltip("Txs", title="Transactions", format=","),
            alt.Tooltip("Txs Per User", title="Transactions per User", format=",.2f"),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
c2.altair_chart(chart, use_container_width=True)
