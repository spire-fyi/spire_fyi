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
mad_lad_df = utils.load_mad_lad_data()
madlist_count = (
    mad_lad_df.groupby("Username")
    .agg(Count=("Mint", "nunique"))
    .reset_index()
    .sort_values(by="Count", ascending=False)
    .reset_index(drop=True)
)
daily_counts = (
    mad_lad_df.groupby(
        [
            pd.Grouper(key="Block Timestamp", axis=0, freq="D"),
        ]
    )
    .agg(Count=("Tx Id", "count"))
    .reset_index()
)

query_base = utils.query_base
api_base = utils.api_base
madlad_query_dict = {
    "sales": {
        "query": f"{query_base}/66990db6-668c-4d46-89fb-86cd8473c33d",
        "api": f"{api_base}/66990db6-668c-4d46-89fb-86cd8473c33d/data/latest",
        "datecols": ["BLOCK_TIMESTAMP"],
    },
    "mints": {
        "query": f"{query_base}/178d89e2-4064-4d59-a9ac-5c47453e7f5b",
        "api": f"{api_base}/178d89e2-4064-4d59-a9ac-5c47453e7f5b/data/latest",
        "datecols": ["BLOCK_TIMESTAMP"],
    },
    "volume_spike": {
        "query": f"{query_base}/565bfd32-7713-4abe-8a99-1e79cc78b11f",
        "api": f"{api_base}/565bfd32-7713-4abe-8a99-1e79cc78b11f/data/latest",
        "datecols": ["DATETIME"],
    },
}
madlad_data_dict = {}
for k, v in madlad_query_dict.items():
    madlad_data_dict[k] = utils.load_flipside_api_data(v["api"], v["datecols"])
    try:
        madlad_data_dict[k]["Explorer URL"] = madlad_data_dict[k]["Tx Id"].apply(
            lambda x: f"https://solana.fm/tx/{x}"
        )
    except:
        pass


volume_spike_by_marketplace = madlad_data_dict["volume_spike"][
    ["Datetime", "Label", "Combined Marketplace", "Sales Count", "Total Sales Sol", "Total Sales Usd"]
].rename(columns={"Combined Marketplace": "Marketplace"})
volume_spike_total = volume_spike_by_marketplace.groupby(["Datetime", "Label"]).sum().reset_index()

sales_df = utils.add_rarity_data(madlad_data_dict["sales"], how="left").rename(columns={"Image": "image"})
most_recent = sales_df.loc[sales_df.groupby("Mint")["Block Timestamp"].idxmax(), :][
    ["Mint", "Block Timestamp", "Purchaser", "Seller", "Sales Amount", "Sales Amount Usd"]
].rename(
    columns={
        "Block Timestamp": "Last Purchase Time",
        "Purchaser": "Last Purchaser",
        "Seller": "Last Seller",
        "Sales Amount": "Last Sales Amount",
        "Sales Amount Usd": "Last Sales Amount Usd",
    }
)
sales_df = sales_df.merge(most_recent, on="Mint")

mints_df = utils.add_rarity_data(madlad_data_dict["mints"])
grouped_mints = (
    mints_df.groupby(pd.Grouper(key="Block Timestamp", axis=0, freq="1h"))
    .agg(Mints=("Tx Id", "count"), Amount=("Amount", "sum"), Users=("Collector", "nunique"))
    .reset_index()
)
most_recent_price = sales_df.iloc[-1].Price
unique_collectors = mints_df.Collector.unique()
unique_mints = mints_df.Mint.unique()
total_raised = mints_df.Amount.sum()
total_raised_usd = total_raised * most_recent_price
total_fees = mints_df.Fee.sum()
total_fees_usd = total_fees * most_recent_price

mints_per_user = (
    mints_df.groupby("Collector")["Tx Id"]
    .count()
    .reset_index()
    .rename(columns={"Tx Id": "Count"})
    .sort_values(by="Count", ascending=False)
)
top_users = mints_per_user.iloc[:100]
backpack_usernames = []
for x in top_users.Collector:
    backpack_usernames.append({"Collector": x, "Username": utils.get_backpack_username(x)})
top_users = top_users.merge(pd.DataFrame(backpack_usernames), on="Collector")
no_username_count = top_users[top_users.Username.isna()].Collector.nunique()
top_users["Minter"] = top_users.apply(
    lambda x: x.Username if x.Username else f"One of {no_username_count} Addresses with no Username", axis=1
)


attributes = [
    "Attribute count",
    "Gender",
    "Type",
    "Expression",
    "Hat",
    "Eyes",
    "Clothing",
    "Background",
    "Hair",
    "Mustache",
    "Smoking",
    "Smoke",
    "Effort",
    "Mouth",
    "Hand",
    "Glove",
    "Back",
    "Necklace",
]

sales, mints, madlist = st.tabs(["Sales", "Mint", "Mad List"])

with sales:
    c1, c2 = st.columns([1, 8])
    image = Image.open("assets/images/MadLads_Logo.png")
    c1.image(image, width=100)
    c2.header("Mad Lads: Secondary Sales")
    c2.write(
        "[Mad Lads](https://twitter.com/MadLadsNFT) quickly became one of the top NFT collections by trading volume shortly after its mint."
    )
    st.write("---")
    st.subheader("NFT Trading Volume Spike")
    st.caption(
        "NFT trading volume spiked after the Mad Lads became tradable. This is also apparent in the [Whale Watcher](Whale_Watcher) page, showing large NFT sales transactions!"
    )

    c1, c2, c3 = st.columns(3)
    metric = c1.selectbox(
        "Metric:",
        [
            "Sales Count",
            "Total Sales",
            # These don't make sense for this dataset
            # "Unique Nfts Sold",
            # "Avg Sales Amount",
            # "Min Sales Amount",
            # "Max Sales Amount",
            # "Median Sales Amount",
        ],
        index=1,
        key="volume-selectbox",
    )
    normalize = c2.checkbox("Normalize", value=True, key="volume-normalize")
    if metric == "Total Sales" or "Amount" in metric:
        currency = c3.radio(
            "Currency:",
            ["Sol", "Usd"],
            format_func=lambda x: x.upper(),
            key="spike-currency",
            horizontal=True,
        )
    else:
        currency = None
    stack = "normalize" if normalize else True
    metric = f"{metric} {currency}" if currency is not None else metric
    metric_title = f"{metric[:-4]} ({currency.upper()})" if currency is not None else metric
    chart = (
        alt.Chart(
            volume_spike_total,
            title=f"NFT {metric_title}: Hourly",
        )
        .mark_bar(binSpacing=0)
        .encode(
            x=alt.X("yearmonthdatehours(Datetime)", title="Datetime"),
            y=alt.Y(metric, title=metric_title, stack=stack),
            color=alt.Color(
                "Label",
                scale=alt.Scale(domain=["Other", "MadLads"], range=["#4B3D60", "#FD5E53"]),
                sort="-y",
            ),
            tooltip=[
                alt.Tooltip("yearmonthdatehours(Datetime)", title="Datetime"),
                alt.Tooltip("Label"),
                alt.Tooltip("Sales Count", format=","),
                alt.Tooltip("Total Sales Sol", title="Total Sales (SOL)", format=",.2f"),
                alt.Tooltip("Total Sales Usd", title="Total Sales (USD)", format=",.2f"),
            ],
        )
    ).properties(height=600, width=600)
    st.altair_chart(chart, use_container_width=True)
    st.write("---")

    st.subheader("Sales Breakdown")
    c1, c2, c3 = st.columns(3)
    attribute = c1.selectbox(
        "Attribute:",
        attributes,
        index=2,
        key="rarity-selectbox",
    )
    currency = c2.radio(
        "Currency:",
        ["SOL", "USD"],
        key="rarity-currency",
        horizontal=True,
    )
    log_scale = c3.checkbox("Log Scale", value=True, key="rarity-log")
    load_image = c3.checkbox("Load Image on Hover (downloads a lot of data)", value=False, key="rarity-image")

    amount_column = "Sales Amount" if currency == "SOL" else "Sales Amount Usd"
    y_title = f"Sales Amount ({currency})"
    scale = "log" if log_scale else "linear"
    tooltip = [
        "Rank",
        alt.Tooltip(amount_column, title=y_title, format=",.2f"),
        alt.Tooltip("Last Purchaser"),
        alt.Tooltip("Last Seller"),
        alt.Tooltip("Last " + amount_column, title="Last " + y_title, format=",.2f"),
    ]
    if load_image:
        tooltip.append("image")
    legend_selection = alt.selection_multi(fields=[attribute], bind="legend")
    chart = (
        alt.Chart(sales_df, title=f'Rarity Rank vs Sales Amount, highlighting the "{attribute}" Attribute')
        .mark_circle()
        .encode(
            x="Rank",
            y=alt.Y(amount_column, title=y_title, scale=alt.Scale(type=scale, nice=False, zero=False)),
            color=alt.Color(attribute, scale=alt.Scale(scheme="turbo")),
            href="Howrare Url",
            tooltip=tooltip,
            opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.05)),
            size=alt.condition(legend_selection, alt.value(25), alt.value(10)),
        )
        .add_selection(legend_selection)
        .properties(height=800, width=600)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

with mints:
    c1, c2 = st.columns([1, 8])
    image = Image.open("assets/images/MadLads_Logo.png")
    c1.image(image, width=100)
    c2.header("Mad Lads: Mint Process")
    c2.write(
        "The [Mad Lads](https://twitter.com/MadLadsNFT) mint consisted of a private (Madlist only) mint, and a public phase. Both took place exclusively in the Backpack app."
    )
    st.write("---")
    c1, c2 = st.columns(2)
    chart = (
        alt.Chart(grouped_mints, title="Mad Lads Mint: Total Amount Raised")
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
            x=alt.X("yearmonthdatehours(Block Timestamp)", title="Datetime"),
            y=alt.Y("Amount", title="Amount paid (SOL)"),
            tooltip=[
                alt.Tooltip("yearmonthdatehours(Block Timestamp)", title="Datetime"),
                alt.Tooltip("Amount", title="Amount paid (SOL)", format=",.2f"),
                alt.Tooltip("Mints", format=","),
                alt.Tooltip("Users", format=","),
            ],
        )
        .properties(height=600, width=600)
    )
    c1.altair_chart(chart, use_container_width=True)

    chart1 = (
        alt.Chart(grouped_mints, title="Mad Lads Mint: Mints and Unique Users")
        .mark_area(color="#FD5E53", interpolate="monotone")
        .encode(
            x=alt.X("yearmonthdatehours(Block Timestamp)", title="Datetime"),
            y=alt.Y("Mints", title="Count"),
            # y2=alt.Y2("Users"),
            tooltip=[
                alt.Tooltip("yearmonthdatehours(Block Timestamp)", title="Datetime"),
                alt.Tooltip("Amount", title="Amount paid (SOL)", format=",.2f"),
                alt.Tooltip("Mints", format=","),
                alt.Tooltip("Users", format=","),
            ],
        )
        .properties(height=600, width=500)
    )
    chart2 = (
        alt.Chart(grouped_mints, title="Mad Lads Mint: Mints and Unique Users")
        .mark_area(color="#4B3D60", interpolate="monotone")
        .encode(
            x=alt.X("yearmonthdatehours(Block Timestamp)", title="Datetime"),
            y=alt.Y("Users", title="Count"),
            # y2=alt.Y2("Users"),
            tooltip=[
                alt.Tooltip("yearmonthdatehours(Block Timestamp)", title="Datetime"),
                alt.Tooltip("Amount", title="Amount paid (SOL)", format=",.2f"),
                alt.Tooltip("Mints", format=","),
                alt.Tooltip("Users", format=","),
            ],
        )
        .properties(height=600, width=500)
    )
    c2.altair_chart(chart1 + chart2, use_container_width=True)
    c1, c2 = st.columns(2)
    c1.metric("Mad Lads Minted", f"{len(unique_mints):,}")
    c2.metric("Unique Minters", f"{len(unique_collectors):,}")
    c1.metric("Total Amount Raised", f"{total_raised:,.1f} SOL (${total_raised_usd:,.2f})")
    c2.metric("Fees paid during mint", f"{total_fees:,.2f} SOL (${total_fees_usd:,.2f})")
    st.write("---")

    chart = (
        alt.Chart(
            top_users,
            title=f"Top 100 Users by Number of Mad Lads Minted",
        )
        .mark_bar()
        .encode(
            x=alt.X("Minter", sort="-y", axis=alt.Axis(labelAngle=-70)),
            y=alt.Y("Count", title="Mad Lads Minted"),
            tooltip=[
                # alt.Tooltip("Username"),
                alt.Tooltip("Minter"),
                alt.Tooltip("Collector"),
                alt.Tooltip("Count", title="Madlist Spots Minted", format=","),
            ],
            color=alt.Color(
                "Username",
                sort=alt.EncodingSortField(field="Count", op="max", order="descending"),
                scale=alt.Scale(scheme="turbo"),
                legend=None,
            ),
        )
    ).properties(height=600, width=600)
    st.altair_chart(chart, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean Mad Lads Minted per User", f"{mints_per_user.Count.mean():.2f}")
    c2.metric("Median Mad Lads Minted per User", f"{mints_per_user.Count.median():.2f}")
    c3.metric("Max Mad Lads Minted per User", f"{mints_per_user.Count.max()}")
    c4.metric("Min Mad Lads Minted per User", f"{mints_per_user.Count.min()}")
    st.write("---")

with madlist:
    c1, c2 = st.columns([1, 8])
    image = Image.open("assets/images/MadLads_Logo.png")
    c1.image(image, width=100)
    c2.header("Mad Lads: Madlist Tracker")
    c2.write(
        "The [Mad Lads](https://twitter.com/MadLadsNFT) NFT collection from the xNFT Backpack team, was mintable only by users with a Madlist spot."
    )
    st.write("---")

    c1, c2 = st.columns(2)
    chart = (
        alt.Chart(daily_counts, title="Madlist Spots Minted by Date")
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
            x=alt.X("yearmonthdate(Block Timestamp)", title="Date"),
            y=alt.Y("Count", title="Madlist Spots Minted"),
            tooltip=[
                alt.Tooltip("yearmonthdate(Block Timestamp)", title="Date"),
                alt.Tooltip("Count", title="Madlist Spots Minted"),
            ],
        )
    ).properties(height=600, width=600)
    c1.altair_chart(chart, use_container_width=True)

    chart = (
        alt.Chart(
            madlist_count.sort_values(by="Count", ascending=False).iloc[:15],
            title=f"Top 15 Users by Madlist Count",
        )
        .mark_bar()
        .encode(
            x=alt.X("Username", sort="-y", axis=alt.Axis(labelAngle=-70)),
            y=alt.Y("Count", title="Madlist Spots Minted"),
            tooltip=[
                alt.Tooltip("Username"),
                alt.Tooltip("Count", title="Madlist Spots Minted", format=","),
            ],
            color=alt.Color(
                "Username",
                sort=alt.EncodingSortField(field="Count", op="max", order="descending"),
                scale=alt.Scale(scheme="turbo"),
                legend=None,
            ),
        )
    ).properties(height=600, width=600)
    c2.altair_chart(chart, use_container_width=True)

    st.subheader("Mad List Tracker")
    c1, c2 = st.columns(2)

    inner_radius = 150
    outer_radius = 250
    arc_df = pd.DataFrame(
        {
            "Category": [
                "Claimed by users with > 1 spot",
                "Claimed by users with 1 spot",
                "Unclaimed",
            ],
            "Spots": [
                madlist_count[madlist_count.Count > 1].Count.sum(),
                madlist_count[madlist_count.Count == 1].Count.sum(),
                10_000 - len(mad_lad_df),
            ],
        }
    )
    chart = (
        alt.Chart(arc_df)
        .mark_arc(
            innerRadius=inner_radius,
            outerRadius=outer_radius,
            theta=3.1415 / 2,
            theta2=-3.1415 / 2,
            yOffset=outer_radius / 2,
        )
        .encode(
            theta=alt.Theta(
                field="Spots",
                stack=True,
                scale=alt.Scale(type="linear", rangeMax=1.5708, rangeMin=-1.5708),
            ),
            color=alt.Color(
                "Category",
                scale=alt.Scale(
                    domain=["Claimed by users with 1 spot", "Claimed by users with > 1 spot", "Unclaimed"],
                    range=[
                        "#FD5E53",
                        "#4B3D60",
                        "#dbd8df",
                    ],
                ),
                legend=alt.Legend(
                    orient="none",
                    legendX=inner_radius * 1.25,
                    legendY=outer_radius * 0.75,
                    direction="vertical",
                    titleAnchor="middle",
                    title=None,
                ),
            ),
        )
        .properties(height=300, width=600)
        .configure_legend(
            titleFontSize=18,
            labelFontSize=15,
            labelLimit=400,
        )
    )
    c1.altair_chart(chart)
    c1.caption("(Assuming a 10,000 NFT collection size)")

    c2.metric("Total Madlist spots claimed", len(mad_lad_df))
    c2.metric("Median Madlist spots per user", f"{madlist_count.Count.median():.1f}")
    c2.metric(
        "Proportion of users with more than one Madlist spots",
        f"{len(madlist_count[madlist_count.Count > 1]) / len(madlist_count):.1%}",
    )

st.write("---")
with st.expander("View and Download Data Table"):
    st.subheader("Sales")
    st.write("**NFT Volume after the Mad Lads mint**")
    st.write(volume_spike_total)
    slug = f"mad_lad_volume"
    st.download_button(
        "Click to Download",
        volume_spike_total.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("**Mad Lad Sales**")
    st.write(sales_df)
    slug = f"mad_lad_sales"
    st.download_button(
        "Click to Download",
        sales_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )

    st.subheader("Mints")
    st.write("**All Mint Transactions**")
    st.write(mints_df)
    slug = f"mad_lad_mints"
    st.download_button(
        "Click to Download",
        mints_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("**Mad Lads minted per user**")
    st.write(mints_per_user)
    slug = f"mad_lad_user_mints"
    st.download_button(
        "Click to Download",
        mints_per_user.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )

    st.subheader("Mad Lad Data")
    st.write("**All Madlist Token holders**")
    st.write(mad_lad_df)
    slug = f"mad_lad_all"
    st.download_button(
        "Click to Download",
        mad_lad_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("**All Madlist Token Counts by User**")
    st.write(madlist_count)
    slug = f"mad_lad_user"
    st.download_button(
        "Click to Download",
        madlist_count.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
    st.write("**Mad List Tracker**")
    st.write(arc_df)
    slug = f"mad_list_tracker"
    st.download_button(
        "Click to Download",
        arc_df.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
