import altair as alt
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
c2.caption("A viewpoint above Solana data. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/).")
c1.image(
    image,
    width=200,
)
st.write("---")

st.header("Marketplace comparison")
_, marketplace_info, _, by_chain_data = utils.load_nft_data()
metric = st.selectbox(
    "Choose a metric:", ["Transaction Count", "NFTs Sold", "Sale Amount (SOL)"], key="nft-marketplace-metric"
)
chart = (
    alt.Chart(marketplace_info, title=f"{metric} by Marketplace: Weekly")
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
            "value",
            title="Marketplace",
            scale=alt.Scale(scheme="turbo"),
            sort=alt.EncodingSortField(field=metric, op="max", order="ascending"),
        ),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            alt.Tooltip("value", title="Marketplace"),
            alt.Tooltip(metric, format=",.2f" if metric == "Sale Amount (SOL)" else ","),
            alt.Tooltip("Buyers", format=","),
            alt.Tooltip("Sellers", format=","),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
st.altair_chart(chart, use_container_width=True)
with st.expander("View and Download Data Table"):
    marketplace_info = marketplace_info.rename(columns={"value": "Marketplace"}).drop(columns="variable")
    st.write(marketplace_info)
    st.download_button(
        "Click to Download",
        marketplace_info.to_csv(index=False).encode("utf-8"),
        f"weekly_nft_by_marketplace.csv",
        "text/csv",
        key="download-weekly-nft-marketplace",
    )

st.header("Cross-chain comparison")
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
