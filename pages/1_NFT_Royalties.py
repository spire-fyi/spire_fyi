import altair as alt
import streamlit as st
from PIL import Image
import pandas as pd

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
    width=200,
)
top_nft_info = utils.load_top_nft_info()
sol_price = utils.load_sol_daily_price()
post_royalty_df = top_nft_info.copy()[top_nft_info.BLOCK_TIMESTAMP >= "2022-10-15"]

tab1, tab2 = st.tabs(["Overview", "NFT Royalty Tool"])
with tab1:
    rules = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Date": ["2022-10-14"],
                    "color": ["gray"],
                    "Description": ["Magic Eden announces optional fees"],
                }
            )
        )
        .mark_rule(size=3)
        .encode(x="yearmonthdate(Date)", color=alt.Color("color:N", scale=None), tooltip=["Description"])
    )

    st.header("Overview")
    st.write("The charts below highlight NFT marketplace activity and royalties trends on Solana.")
    _, marketplace_info, _, _ = utils.load_nft_data()

    totals = (
        marketplace_info.groupby("Date")
        .agg(
            total_transactions=("Transaction Count", "sum"),
            total_sales_amount=("Sale Amount (SOL)", "sum"),
            total_unique_NFTS=("Unique NFTs Sold", "sum"),
        )
        .reset_index()
    )
    marketplace_info = marketplace_info.merge(totals, on="Date")

    marketplace_info["Transaction Count (%)"] = (
        marketplace_info["Transaction Count"] / marketplace_info.total_transactions
    )
    marketplace_info["Sale Amount (SOL) (%)"] = (
        marketplace_info["Sale Amount (SOL)"] / marketplace_info.total_sales_amount
    )
    marketplace_info["Unique NFTs Sold (%)"] = (
        marketplace_info["Unique NFTs Sold"] / marketplace_info.total_unique_NFTS
    )

    metric = st.selectbox(
        "Choose a metric:",
        ["Transaction Count", "Unique NFTs Sold", "Sale Amount (SOL)"],
        key="nft-marketplace-metric",
        index=2,
    )
    base = (
        alt.Chart(marketplace_info, title=f"{metric} by Marketplace: Weekly")
        .mark_bar(width=8)
        .encode(
            x=alt.X(
                "yearmonthdate(Date)",
                title="Date",
            ),
            y=alt.Y(metric, stack="normalize", title=f"{metric} - Proportion"),
            # order=alt.Order(
            #     metric,
            #     sort="ascending",
            # ),
            color=alt.Color(
                "value",
                title="Marketplace",
                scale=alt.Scale(scheme="turbo"),
                sort=alt.EncodingSortField(field=metric, op="max", order="ascending"),
            ),
            tooltip=[
                alt.Tooltip("yearmonthdate(Date)", title="Date"),
                alt.Tooltip("value", title="Marketplace"),
                alt.Tooltip(f"{metric} (%)", format=",.2%"),
                alt.Tooltip(metric, format=",.2f" if metric == "Sale Amount (SOL)" else ","),
                alt.Tooltip("Buyers", format=","),
                alt.Tooltip("Sellers", format=","),
            ],
        )
    )
    chart = (base + rules).interactive().properties(height=600, width=800)
    st.altair_chart(chart, use_container_width=True)
    with st.expander("View and Download Data Table"):
        marketplace_info = (
            marketplace_info.rename(columns={"value": "Marketplace"})
            .drop(columns="variable")
            .drop(columns=["total_transactions", "total_sales_amount", "total_unique_NFTS"])
        )
        st.write(marketplace_info)
        st.download_button(
            "Click to Download",
            marketplace_info.to_csv(index=False).encode("utf-8"),
            f"weekly_nft_by_marketplace.csv",
            "text/csv",
            key="download-weekly-nft-marketplace",
        )
    st.write("---")

    royalty_df = utils.load_royalty_data()
    base = alt.Chart(royalty_df, title="Royalty Payment Percentage: Monthly").encode(
        x=alt.X("yearmonthdate(Date):T", title="Date"),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date):T", title="Date"),
            alt.Tooltip("Percent of Sales with Royalty Payments", format=".1f"),
            alt.Tooltip("Royalty Fee Percentage", format=".1f", title="Average Royalty Fee Percentage"),
        ],
    )
    area = base.mark_area(
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
    ).encode(
        y=alt.Y("Percent of Sales with Royalty Payments"),
    )
    line = base.mark_line(color="#FFE373", interpolate="monotone").encode(
        y=alt.Y("Royalty Fee Percentage", title="Average Royalty Fee Percentage")
    )
    chart = (
        (area + line + rules).interactive().properties(height=600, width=800).resolve_scale(y="independent")
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(
        f"Credit to [@kblum](https://twitter.com/BlumbergKellen/status/1601245496789463045) for insights used for this chart."
    )

    with st.expander("View and Download Data Table"):
        st.write(royalty_df)
        st.download_button(
            "Click to Download",
            royalty_df.to_csv(index=False).encode("utf-8"),
            f"monthly_nft_royalty.csv",
            "text/csv",
            key="download-monthly-nft-royalty",
        )
    st.write("---")

    st.header("Leaderboard")
    st.write(
        f"""
        We examined the percentage of users who pay royalties since they have been optional on Magic Eden for each project.

        Below is the leaderboard; check out the `NFT Royalty Tool` using the tab at the top of the page for more information on these projects!
        """
    )
    leader_board_df = post_royalty_df[post_royalty_df.royalty_percentage > 0]
    leader_board_df = (
        leader_board_df.groupby(["Name", "PURCHASER"])[["paid_royalty", "paid_no_royalty"]]
        .agg("sum")
        .reset_index()
    )
    leader_board_df["Royalty Payment Rate"] = leader_board_df.paid_royalty / (
        leader_board_df.paid_royalty + leader_board_df.paid_no_royalty
    )
    leader_board_df = leader_board_df.groupby(["Name"])["Royalty Payment Rate"].mean().reset_index()
    leader_board_df = leader_board_df.sort_values(by="Royalty Payment Rate", ascending=False).reset_index(
        drop=True
    )
    leader_board_df["Royalty Payment Rate"] = leader_board_df["Royalty Payment Rate"].apply(
        lambda x: f"{x:.2%}"
    )
    # #TODO: this works for some, not all projects
    # leader_board_df["Magic Eden Link"] = leader_board_df["Name"].apply(
    #     lambda x: f"https://magiceden.io/marketplace/{x.replace(' ', '_').replace(':', '').lower()}"
    # )
    st.write(leader_board_df)

with tab2:
    st.header("NFT Royalty Tool")
    st.write(
        """ 
        The purpose of this tool is to provide key royalty and user metrics for a collection. You can also download a list of royalty paying users

        Metrics are for **sales on Magic Eden** since October 15, 2022 (when royalty payment became optional).
        """
    )

    project_names = top_nft_info.groupby("Name").SALES_AMOUNT.sum().sort_values(ascending=False)
    top_project_names = [
        "y00ts",
        "DeGods",
        "Claynosaurz",
        "LILY",
        "y00ts: mint t00b",
        "ABC",
        "Okay Bears",
        "Solana Monkey Business: SMB Gen2",
        "Elixer: Ovols",
        "Famous Fox Federation",
        "Blocksmith Labs: Smyths",
        "Cets on Creck",
        "Degen Ape",
    ]
    top_project_names += project_names.index.drop(top_project_names).tolist()

    nft_collection = st.selectbox("Choose an NFT Collection:", top_project_names, key="top_project_names")
    nft_collection_df = top_nft_info.copy()[top_nft_info.Name == nft_collection].reset_index()

    nft_collection_df = nft_collection_df.merge(sol_price, on="Date")
    nft_collection_df = nft_collection_df.rename(columns={"Price (USD)": "SOL Price (USD)"}).drop(
        columns="SYMBOL"
    )
    nft_collection_df["SALES_AMOUNT_USD"] = (
        nft_collection_df["SALES_AMOUNT"] * nft_collection_df["SOL Price (USD)"]
    )
    nft_collection_df["total_royalty_amount_usd"] = (
        nft_collection_df["total_royalty_amount"] * nft_collection_df["SOL Price (USD)"]
    )
    nft_collection_df["expected_royalty_usd"] = (
        nft_collection_df["expected_royalty"] * nft_collection_df["SOL Price (USD)"]
    )
    nft_collection_df["royalty_diff_usd"] = (
        nft_collection_df["royalty_diff"] * nft_collection_df["SOL Price (USD)"]
    )

    collection_post_royalty_df = nft_collection_df[nft_collection_df.BLOCK_TIMESTAMP >= "2022-10-15"]

    st.subheader(f"Project Name: {nft_collection}")
    num, img = utils.get_random_image(nft_collection_df)
    currency = st.radio("Choose a currency unit", ["Solana", "USD"], key="currency", horizontal=True)

    c1, c2 = st.columns(2)
    c1.image(img, caption=nft_collection_df.iloc[num]["name"], use_column_width=True)

    total_sales_count = collection_post_royalty_df.TX_ID.nunique()

    total_sales_sol = collection_post_royalty_df.SALES_AMOUNT.sum()
    total_royalties_sol = collection_post_royalty_df.total_royalty_amount.sum()
    avg_royalties_sol = collection_post_royalty_df.total_royalty_amount.mean()
    expected_royalties_sol = collection_post_royalty_df.expected_royalty.sum()

    total_sales_usd = collection_post_royalty_df.SALES_AMOUNT_USD.sum()
    total_royalties_usd = collection_post_royalty_df.total_royalty_amount_usd.sum()
    avg_royalties_usd = collection_post_royalty_df.total_royalty_amount_usd.mean()
    expected_royalties_usd = collection_post_royalty_df.expected_royalty_usd.sum()

    c2.metric("Total Sales", f"{total_sales_count:,}")
    c2.metric(
        "Proportion paying royalties",
        f"{collection_post_royalty_df.paid_royalty.sum()/len(collection_post_royalty_df):.2%}",
    )
    if currency == "USD":
        c2.metric("Total Sales Volume", f"${total_sales_usd:,.2f}")
        c2.metric("Total Royalties Earned", f"${total_royalties_usd:,.2f}")
        c2.metric(
            "Expected Royalties",
            f"${expected_royalties_usd:,.2f}",
            f"{total_royalties_usd- expected_royalties_usd:,.2f} dollar difference",
        )
        c2.metric("Average Royalties Earned", f"${avg_royalties_usd:,.2f}")
    if currency == "Solana":
        c2.metric("Total Sales Volume", f"{total_sales_sol:,.2f} SOL")
        c2.metric("Total Royalties Earned", f"{total_royalties_sol:,.2f} SOL")
        c2.metric(
            "Expected Royalties",
            f"{expected_royalties_sol:,.2f} SOL",
            f"{total_royalties_sol - expected_royalties_sol:,.2f} SOL difference",
        )
        c2.metric("Average Royalties Earned", f"{avg_royalties_sol:,.2f} SOL")
    c2.metric(
        "Average Royalty Percentage Paid",
        f"{collection_post_royalty_df.royalty_percent_paid.mean():.2%} (expected: {collection_post_royalty_df.royalty_percentage.mean():.2%})",
    )
    st.write("---")
    if collection_post_royalty_df.royalty_percentage.mean() == 0:
        st.write("This collection has no royalty fees!")
    else:
        metric = st.radio(
            "Choose a metric",
            ["mean", "sum"],
            format_func=lambda x: "Average" if x == "mean" else "Total",
            horizontal=True,
            key="metric",
        )
        c1, c2 = st.columns(2)
        if currency == "USD":
            val = "total_royalty_amount_usd"
        else:
            val = "total_royalty_amount"
        x = nft_collection_df.groupby(["Date"])[val].agg(metric).reset_index()
        base = (
            alt.Chart(x, title="Daily Royalties Paid")
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
                y=alt.Y(val, title=f' {"Average" if metric == "mean" else "Total"} Royalty ({currency})'),
                tooltip=[
                    alt.Tooltip("yearmonthdate(Date)", title="Date"),
                    alt.Tooltip(
                        val,
                        title=f' {"Average" if metric == "mean" else "Total"} Royalty ({currency})',
                        format=",.2f",
                    ),
                ],
            )
        )
        chart = (base + rules).interactive().properties(height=600, width=800)
        c1.altair_chart(chart, use_container_width=True)

        x = (
            nft_collection_df[["Date", "paid_full_royalty", "paid_half_royalty", "paid_no_royalty"]]
            .rename(
                columns={"paid_full_royalty": "Full", "paid_half_royalty": "Half", "paid_no_royalty": "None"}
            )
            .melt(id_vars="Date")
            .groupby(["Date", "variable"])["value"]
            .sum()
            .reset_index()
        )
        base = (
            alt.Chart(x, title="Daily Sales Count for Royalty Amounts")
            .mark_line(width=3)
            .encode(
                x=alt.X("yearmonthdate(Date)", title="Date"),
                y=alt.Y("value", title="Sales"),
                color=alt.Color(
                    "variable",
                    title="Royalty Amount",
                    scale=alt.Scale(domain=["Full", "Half", "None"], range=["#4B3D60", "#FFE373", "#FD5E53"]),
                ),
            )
        )
        chart = (base + rules).interactive().properties(height=600, width=800)
        c2.altair_chart(chart, use_container_width=True)
        st.write("---")
        c1, c2 = st.columns(2)
        if currency == "USD":
            vals = [expected_royalties_usd, total_royalties_usd]
        else:
            vals = [expected_royalties_sol, total_royalties_sol]
        chart = (
            alt.Chart(
                pd.DataFrame({"Royalty Amount": ["Expected", "Earned"], "value": vals}),
                title="Royalty Amounts: Earned vs. Expected",
            )
            .mark_arc()
            .encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color=alt.Color(field="Royalty Amount", type="nominal"),
                tooltip=["Royalty Amount", alt.Tooltip("value", title=f"Value ({currency})", format=",.2f")],
            )
        ).properties(height=300)
        c1.altair_chart(chart, use_container_width=True)

        vals = nft_collection_df[["paid_full_royalty", "paid_half_royalty", "paid_no_royalty"]].sum().values
        chart = (
            alt.Chart(
                pd.DataFrame({"Royalties Paid": ["Full", "Half", "None"], "value": vals}),
                title="Proportion of Royalty Fees Paid in Sales",
            )
            .mark_arc()
            .encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color=alt.Color(field="Royalties Paid", type="nominal"),
                tooltip=["Royalties Paid", alt.Tooltip("value", title=f"Sales", format=",.0f")],
            )
        ).properties(height=300)
        c2.altair_chart(chart, use_container_width=True)
    st.write("---")
    st.subheader("Royalty paying users (since fees became optional)")
    user_type = st.radio(
        "Which type of user?",
        ["All", "Paid any royalty", "Paid Full Royalty", "Paid Half Royalty", "Paid No Royalty"],
        horizontal=True,
        key="user_type",
    )
    royalty_paying_users = collection_post_royalty_df[
        [
            "Date",
            "PURCHASER",
            "MINT",
            "SALES_AMOUNT",
            "total_royalty_amount",
            "royalty_percent_paid",
            "paid_full_royalty",
            "paid_half_royalty",
            "paid_no_royalty",
        ]
    ].rename(
        columns={
            "PURCHASER": "Wallet",
            "MINT": "Mint",
            "SALES_AMOUNT": "Sales Amount",
            "total_royalty_amount": "Royalty Paid",
            "royalty_percent_paid": "Royalty Percentage Paid",
            "paid_full_royalty": "Paid Full Royalty",
            "paid_half_royalty": "Paid Half Royalty",
            "paid_no_royalty": "Paid No Royalty",
        }
    )
    if user_type == "Paid Full Royalty":
        royalty_paying_users = royalty_paying_users[royalty_paying_users["Paid Full Royalty"]].reset_index(
            drop=True
        )
    if user_type == "Paid Half Royalty":
        royalty_paying_users = royalty_paying_users[royalty_paying_users["Paid Half Royalty"]].reset_index(
            drop=True
        )
    if user_type == "Paid No Royalty":
        royalty_paying_users = royalty_paying_users[royalty_paying_users["Paid No Royalty"]].reset_index(
            drop=True
        )
    if user_type == "Paid any royalty":
        royalty_paying_users = royalty_paying_users[
            (royalty_paying_users["Paid Full Royalty"]) | (royalty_paying_users["Paid Half Royalty"])
        ].reset_index(drop=True)

    st.write(royalty_paying_users)

    st.download_button(
        "Click to Download",
        royalty_paying_users.to_csv(index=False).encode("utf-8"),
        f"{nft_collection.replace(' ', '_')}-MagicEden_royalty_payment_info.csv",
        "text/csv",
        key="download-nft-royalty",
    )
    st.write("---")
    with st.expander("View and Download Full Data Table"):
        nft_collection_df["solana_fm_url"] = nft_collection_df.TX_ID.apply(
            lambda x: f"https://solana.fm/tx/{x}"
        )
        st.write(nft_collection_df)
        st.download_button(
            "Click to Download",
            nft_collection_df.to_csv(index=False).encode("utf-8"),
            f"{nft_collection.replace(' ', '_')}-MagicEden_sales_info.csv",
            "text/csv",
            key="download-nft-colection",
        )
