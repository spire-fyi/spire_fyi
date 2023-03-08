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

    [@spire_fyi](https://twitter.com/spire_fyi) | [spire-fyi/spire_fyi](https://github.com/spire-fyi/spire_fyi) | Donations: GvvrKbq21eTkknHRt9FGVFN54pLWXSSo4D4hz2i1JCn5
    """
)
c1.image(
    image,
    width=100,
)
st.write("---")
st.header("xNFT Analysis")

all_xnft_tx = {
    "query": f"{utils.query_base}/8a368540-2f46-4582-b0e5-76342d1f07df",
    "api": f"{utils.api_base}/8a368540-2f46-4582-b0e5-76342d1f07df/data/latest",
    "datecols": ["BLOCK_TIMESTAMP"],
}

xnft_df = utils.load_flipside_api_data(all_xnft_tx["api"], all_xnft_tx["datecols"])

st.write(xnft_df)
