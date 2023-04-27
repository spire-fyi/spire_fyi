import ast
import datetime

import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image

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
    A viewpoint above Solana data. Insights and on-chain data analytics, inspired by the community and accessible to all. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/), [Helius](https://helius.xyz/), [SolanaFM](https://docs.solana.fm/) and [HowRare](https://howrare.is/api).

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi) | Donations: GvvrKbq21eTkknHRt9FGVFN54pLWXSSo4D4hz2i1JCn5 , or contribute on [Stockpile](https://www.stockpile.pro/projects/fMqAvbsrWseJji8QyNOf)
    """
)
c1.image(
    image,
    width=100,
)
st.write("---")
c1, c2 = st.columns([1, 8])
image = Image.open("assets/images/Backpack_Logo.png")
c1.image(image, width=60)
c2.header("xNFT Backpack Analysis")
c2.write("Exploring on-chain activity of [Backpack](https://twitter.com/xNFT_Backpack) wallet users")
c2.caption(
    "(Backpack and Mad Lads images sourced from the community image assets page [here](https://www.figma.com/community/file/1205194661079253210))"
)
st.write("---")
st.subheader("xNFT Installs")
st.caption("Highlighting the installation of xNFTs")
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
        x=alt.X("Mint Seed Name", title="xNFT Name", sort="-y", axis=alt.Axis(labelAngle=-70)),
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
        x=alt.X("Mint Seed Name", title="xNFT Name", sort="-y", axis=alt.Axis(labelAngle=-70)),
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


st.subheader("Backpack User Information")
date_range = st.radio(
    "Choose a date range:",
    [
        "60d",
        "30d",
        "14d",
        "7d",
    ],
    horizontal=True,
    index=2,
    key="users_date_range",
)
new_xnft_users = utils.load_xnft_new_users().sort_values(by="First Tx Date", ascending=False)

chart = (
    alt.Chart(
        new_xnft_users[
            new_xnft_users["First Tx Date"]
            >= (pd.to_datetime(datetime.datetime.today()) - pd.Timedelta(f"{int(date_range[:-1])}d"))
        ],
        title="New xNFT Users by Date",
    )
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
        interpolate="monotone",
    )
    .encode(
        x=alt.X("yearmonthdate(First Tx Date)", title="Date"),
        y=alt.Y("New Wallets", title="New Users"),
        tooltip=[
            alt.Tooltip("yearmonthdate(First Tx Date)", title="Date"),
            alt.Tooltip("New Wallets", title="New Users"),
        ],
    )
).properties(height=300, width=600)
st.altair_chart(chart, use_container_width=True)
st.caption("New users based on the date where an address first installed an xNFT")

st.write("---")
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
        x=alt.X("Fee Payer", title="Address", sort="-y", axis=alt.Axis(labelAngle=-70)),
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

with st.expander("View and Download Data Table"):
    st.subheader("xNFT Data")
    st.write("**All xNFT Install Transactions**")
    st.write(createInstall)
    slug = f"xnft_installs_tx"
    st.download_button(
        "Click to Download",
        createInstall.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("**xNFT Installs by Username**")
    st.write(xnft_counts_by_user)
    slug = f"xnft_installs_by_user"
    st.download_button(
        "Click to Download",
        xnft_counts_by_user.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("**Daily xNFT Installation Counts**")
    st.write(chart_df)
    slug = f"xnft_installs_count_daily"
    st.download_button(
        "Click to Download",
        chart_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("**Total xNFT Installation Counts**")
    st.write(totals)
    slug = f"xnft_installs_count_total"
    st.download_button(
        "Click to Download",
        totals.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("**New xNFT Users**")
    st.write(new_xnft_users)
    slug = f"xnft_new_isers"
    st.download_button(
        "Click to Download",
        new_xnft_users.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )


st.write("---")
st.header("Backpack Username Lookup")
address = st.text_input(
    "Enter a Solana address or Backpack username for a summary of activity:",
    value="anatoly",
    key="backpackt-text-input",
)
if len(address) < 32 and address != "":
    _address = utils.get_backpack_addresses([address], "Address").Address.values[0]
    if _address is not None:
        backpack = True
        backpack_username = address
        address = _address
    else:
        st.write("Not a valid Solana address!")
        backpack_username = ""
else:
    backpack_username = utils.get_backpack_usernames([address]).Username.values[0]

if backpack_username == "":
    pass
else:
    if backpack_username is None:
        st.subheader(f"[{address}](https://solana.fm/address/{address})")
        st.caption("This address isn't associated with a Backpack username")
        backpack = False
    else:
        st.subheader(f"[{backpack_username}](https://solana.fm/address/{address})")
        st.caption(address)
        backpack = True
    if st.button("Load data"):
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

        if len(tx_data) > 0:
            try:
                num_programs = f"{len(pd.unique(ast.literal_eval(tx_data.PROGRAMS_USED.values[0])))}"
            except ValueError:
                num_programs = f"{len(pd.unique(tx_data.PROGRAMS_USED.values[0]))}"
            first_tx_date = f"{pd.to_datetime(tx_data.FIRST_TX_DATE.values[0]):%Y-%m-%d}"
            num_tx = f"{tx_data.NUM_TXS.values[0]:,}"
            total_fees = f"{tx_data.TOTAL_FEES.values[0]/utils.LAMPORTS_PER_SOL:,.5f}"
        else:
            num_programs = None
            first_tx_date = None
            num_tx = None
            total_fees = None

        num_swaps = swaps_data.TX_ID.nunique()
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("First Transaction Date", first_tx_date)
        c2.metric("Number of Transactions", num_tx)
        c3.metric("Total Fees Paid (SOL)", total_fees)
        c4.metric("Number of Programs Used", num_programs)
        c5.metric("Number of DEX swaps", num_swaps)
        if backpack:
            c6.metric(
                "Number of xNFTS installed",
                f"{createInstall[createInstall['Fee Payer'] == address].Xnft.nunique()}",
            )
            mad_lad_df = utils.load_mad_lad_data()
            madlist_count = (
                mad_lad_df.groupby("Username")
                .agg(Count=("Mint", "nunique"))
                .reset_index()
                .sort_values(by="Count", ascending=False)
                .reset_index(drop=True)
            )
            madlist_spots = madlist_count[madlist_count.Username == backpack_username]
            if len(madlist_spots) > 0:
                c6.metric("Number of Madlist spots", f"{madlist_spots.Count.values[0]}")

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

        with st.expander("View and Download Data Table"):
            try:
                st.subheader("User Lookup Data")
                st.write("**User Overview**")
                st.write(tx_data)
                slug = f"user_overview"
                st.download_button(
                    "Click to Download",
                    tx_data.to_csv(index=False).encode("utf-8"),
                    f"{slug}.csv",
                    "text/csv",
                    key=f"download-{slug}",
                )
                st.write("**User NFT sales Data**")
                st.write(sales_data)
                slug = f"user_sales"
                st.download_button(
                    "Click to Download",
                    sales_data.to_csv(index=False).encode("utf-8"),
                    f"{slug}.csv",
                    "text/csv",
                    key=f"download-{slug}",
                )
                st.write("**User NFT purchases Data**")
                st.write(purchases_data)
                slug = f"user_purchases"
                st.download_button(
                    "Click to Download",
                    purchases_data.to_csv(index=False).encode("utf-8"),
                    f"{slug}.csv",
                    "text/csv",
                    key=f"download-{slug}",
                )
                st.write("**User NFT Mints data**")
                st.write(mints_data)
                slug = f"user_mints"
                st.download_button(
                    "Click to Download",
                    mints_data.to_csv(index=False).encode("utf-8"),
                    f"{slug}.csv",
                    "text/csv",
                    key=f"download-{slug}",
                )
                st.write("**User Swaps Data**")
                st.write(swaps_data)
                slug = f"user_swaps"
                st.download_button(
                    "Click to Download",
                    swaps_data.to_csv(index=False).encode("utf-8"),
                    f"{slug}.csv",
                    "text/csv",
                    key=f"download-{slug}",
                )
            except NameError:
                st.write("Enter a Backpack username or wallet address for transaction data.")
