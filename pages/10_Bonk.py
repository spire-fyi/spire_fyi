import datetime

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
    A viewpoint above Solana data. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/), [Helius](https://helius.xyz/) and [SolanaFM APIs](https://docs.solana.fm/).

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi)
    """
)
c1.image(
    image,
    width=100,
)
st.write("---")
query_base = utils.query_base
api_base = utils.api_base
bonk_query_dict = {
    # Ecosystem
    "Daily Bonk Burned": {
        "query": f"{query_base}/166d0f20-c4e3-4460-b413-d5263bd850b0",
        "api": f"{api_base}/166d0f20-c4e3-4460-b413-d5263bd850b0/data/latest",
        "datecols": ["DATE"],
    },
    "Bonk Leaderboard": {
        "query": f"{query_base}/5de2aadc-622c-4500-bc70-9e0fd4bfbca4",
        "api": f"{api_base}/5de2aadc-622c-4500-bc70-9e0fd4bfbca4/data/latest",
        "datecols": None,
    },
    "Buyers vs Sellers": {
        "query": f"{query_base}/ac7933e1-8e70-4858-a243-8e8e494a40b1",
        "api": f"{api_base}/ac7933e1-8e70-4858-a243-8e8e494a40b1/data/latest",
        "datecols": ["DATE"],
    },
    "Total Bonk Burned": {
        "query": f"{query_base}/a1388731-93fb-431c-a9c0-a34c1533fa2d",
        "api": f"{api_base}/a1388731-93fb-431c-a9c0-a34c1533fa2d/data/latest",
        "datecols": ["DATE"],
    },
}
bonk_data_dict = {}
for k, v in bonk_query_dict.items():
    bonk_data_dict[k] = utils.load_flipside_api_data(v["api"], v["datecols"])
burn_data = bonk_data_dict["Daily Bonk Burned"].copy()
total_burn_df = bonk_data_dict["Total Bonk Burned"].copy()
leaderboard = bonk_data_dict["Bonk Leaderboard"].copy()
leaderboard["Explorer URL"] = leaderboard.Wallet.apply(lambda x: f"https://solana.fm/address/{x}")


st.header("BONK!")
st.write(
    "Examining Solana's community dog coin. **NOTE**: Except for `Total BONK Burned`, accounts associated with the Bonk team are not included in this analysis ([here](https://solana.fm/address/GYqXgEqjcthrFGJZaB4v9D6p4F7a1PKKJZeASfZWb2GH) and [here](https://solana.fm/address/3dWvUFYyDHNgFPrDno2mrMw6zjNWfoHoTAX6o96KX35b))."
)
st.write("---")

c1, c2 = st.columns([2, 1])
c1.subheader("BONK Burn Leaderboard")
c1.write(leaderboard)
slug = f"bonk_leaderboard"
st.download_button(
    "Click to Download",
    leaderboard.to_csv(index=False).encode("utf-8"),
    f"{slug}.csv",
    "text/csv",
    key=f"download-{slug}",
)
c2.subheader("‎")
total_burn = total_burn_df.iloc[-1]["Total Bonk Burned"]
c2.metric(f"Total BONK Burned", f"{total_burn:,.0f}", "🔥" * int(total_burn / 10**12))
st.write("---")

leaderboard["url"] = "https://pbs.twimg.com/profile_images/1600956334635098141/ZSzYTrHf_400x400.jpg"
leaderboard["wallet_short"] = leaderboard["Wallet"].apply(utils.get_short_address)
chart = (
    (
        alt.Chart(leaderboard.iloc[:15], title="Top 15 BONK Burners")
        .mark_image()
        .encode(
            x=alt.X("wallet_short", title="Wallet", sort="-y"),
            y=alt.Y("Total Bonk Burned", title="Total BONK Burned"),
            url="url",
            tooltip=[
                alt.Tooltip("Wallet"),
                alt.Tooltip("Total Bonk Burned", title="Total BONK Burned", format=",.0f"),
            ],
            href="Explorer URL",
        )
    )
    .properties(height=400, width=600)
    .interactive()
)
st.altair_chart(chart, use_container_width=True)


st.write("---")
bonk_burned = charts.alt_daily_cumulative_chart(
    burn_data,
    "BONK Burned: Daily",
    "Daily Bonk Burned",
    "Total Bonk Burned",
    width=20,
)
st.altair_chart(bonk_burned, use_container_width=True)
with st.expander("View and Download Data Table"):
    st.write(burn_data)
    slug = f"bonk_burn_daily"
    st.download_button(
        "Click to Download",
        burn_data.to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )
st.write("---")
st.subheader("BONK Buyers and Sellers")
c1, c2 = st.columns(2)
# Bought and sold
chart = (
    alt.Chart(bonk_data_dict["Buyers vs Sellers"], title=f"BONK Bought and Sold: Daily")
    .mark_line(
        interpolate="monotone",
    )
    .encode(
        x=alt.X("yearmonthdate(Date)", title="Date"),
        y=alt.Y("Bonk Amount", title="BONK Amount"),
        color=alt.Color(
            "Type",
            title="Purchase Type",
            scale=alt.Scale(domain=["Buy", "Sell"], range=["#4B3D60", "#FD5E53"]),
        ),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            alt.Tooltip("Type", title="Purchase Type"),
            alt.Tooltip("Bonk Amount", title="BONK Amount", format=","),
            alt.Tooltip("Txs", title=f"Transaction Count", format=","),
            alt.Tooltip("Unique Wallets", format=","),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
c1.altair_chart(chart, use_container_width=True)
# Unique Purchasers
chart = (
    alt.Chart(bonk_data_dict["Buyers vs Sellers"], title=f"BONK Bought and Sold: Daily")
    .mark_line(
        interpolate="monotone",
    )
    .encode(
        x=alt.X("yearmonthdate(Date)", title="Date"),
        y=alt.Y("Unique Wallets"),
        color=alt.Color(
            "Type",
            title="Purchase Type",
            scale=alt.Scale(domain=["Buy", "Sell"], range=["#4B3D60", "#FD5E53"]),
        ),
        tooltip=[
            alt.Tooltip("yearmonthdate(Date)", title="Date"),
            alt.Tooltip("Type", title="Purchase Type"),
            alt.Tooltip("Bonk Amount", title="BONK Amount", format=","),
            alt.Tooltip("Txs", title=f"Transaction Count", format=","),
            alt.Tooltip("Unique Wallets", format=","),
        ],
    )
    .properties(height=600, width=600)
    .interactive()
)
c2.altair_chart(chart, use_container_width=True)
with st.expander("View and Download Data Table"):
    st.write(bonk_data_dict["Buyers vs Sellers"])
    slug = f"bonk_buyers_sellers"
    st.download_button(
        "Click to Download",
        bonk_data_dict["Buyers vs Sellers"].to_csv(index=False).encode("utf-8"),
        f"{slug}.csv",
        "text/csv",
        key=f"download-{slug}",
    )

st.header("Go BONKers!")
st.write("Does an address BONK?")
wallet_address = st.text_input("Enter a wallet address:")
bonk = utils.get_bonk_balance(wallet_address)
if bonk == "":
    pass
elif bonk is None:
    source = "https://commons.wikimedia.org/wiki/File:Shiba_Inu_(Red_Sesame).JPG"
    st.write(
        f"""
    Sorry this address does not hodl BONK!

    View [BONK's price chart](https://birdeye.so/token/DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263) and consider purchasing some here.
    """
    )
    image = Image.open("assets/images/sad_bonk.jpeg")
    st.image(image, caption=source)
else:
    st.balloons()
    source = "https://commons.wikimedia.org/wiki/File:A_Shiba_Inu_dog_wearing_a_beret_and_black_turtleneck_DALLE2.jpg"
    st.write(
        f"""
    Congrats, this address has **{bonk['amount']/10**bonk['decimals']:,.0f}** BONK!

    If you want to join the Burn leaderboard, consider [burning some BONK](https://sol-incinerator.com/).
    """
    )
    image = Image.open("assets/images/happy_bonk.jpg")
    st.image(image, caption=source)


st.write("---")
with st.expander("Do you like BONK?!?!"):
    c1, c2 = st.columns(2)
    c1.markdown("![BONK!](https://media.tenor.com/oHjfWJorYB8AAAAC/bonk.gif)")
    c1.caption("[Source](https://media.tenor.com/oHjfWJorYB8AAAAC/bonk.gif)")
    c2.markdown("![BONK!](https://media.tenor.com/TbLpG9NCzjkAAAAC/bonk.gif)")
    c2.caption("[Source](https://media.tenor.com/TbLpG9NCzjkAAAAC/bonk.gif)")
    st.write("---")
    c1, c2 = st.columns(2)
    c1.markdown("![BONK!](https://thumbs.gfycat.com/TediousNaturalAffenpinscher-max-1mb.gif)")
    c1.caption("[Source](https://thumbs.gfycat.com/TediousNaturalAffenpinscher-max-1mb.gif)")
    c2.markdown("![BONK!](https://i.kym-cdn.com/photos/images/newsfeed/002/051/063/92e.gif)")
    c2.caption("[Source](https://i.kym-cdn.com/photos/images/newsfeed/002/051/063/92e.gif)")
    st.write("---")
