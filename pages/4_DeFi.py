import altair as alt
import streamlit as st
from PIL import Image

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
st.header("DeFi")
st.write("Additonal analysis coming soon!")
