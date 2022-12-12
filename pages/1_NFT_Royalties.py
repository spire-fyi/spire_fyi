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
c2.caption("A viewpoint above Solana data. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/) and [Helius](https://helius.xyz/).")
c1.image(
    image,
    width=200,
)
st.write("---")

st.header("Marketplace comparison")
_, marketplace_info, _, _ = utils.load_nft_data()

totals = marketplace_info.groupby("Date").agg(
    total_transactions=('Transaction Count', 'sum'),
    total_sales_amount=('Sale Amount (SOL)', 'sum'),
    total_unique_NFTS=('Unique NFTs Sold', 'sum')
).reset_index()
marketplace_info = marketplace_info.merge(totals, on='Date')

marketplace_info['Transaction Count (%)'] = marketplace_info['Transaction Count']/marketplace_info.total_transactions
marketplace_info['Sale Amount (SOL) (%)'] = marketplace_info['Sale Amount (SOL)']/marketplace_info.total_sales_amount
marketplace_info['Unique NFTs Sold (%)'] = marketplace_info['Unique NFTs Sold']/marketplace_info.total_unique_NFTS

metric = st.selectbox(
    "Choose a metric:", ["Transaction Count", "Unique NFTs Sold", "Sale Amount (SOL)"], key="nft-marketplace-metric",
    index=2
)
chart = (
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
            scale=alt.Scale(scheme="category20"),
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
    .properties(height=600, width=600)
    .interactive()
)
st.altair_chart(chart, use_container_width=True)
with st.expander("View and Download Data Table"):
    marketplace_info = marketplace_info.rename(columns={"value": "Marketplace"}).drop(columns="variable").drop(columns=["total_transactions","total_sales_amount","total_unique_NFTS"])
    st.write(marketplace_info)
    st.download_button(
        "Click to Download",
        marketplace_info.to_csv(index=False).encode("utf-8"),
        f"weekly_nft_by_marketplace.csv",
        "text/csv",
        key="download-weekly-nft-marketplace",
    )

