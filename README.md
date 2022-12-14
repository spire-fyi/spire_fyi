# spire_fyi

<img alt="Spire" src="assets/images/spire_logo.png" width="150" height="150">

> A viewpoint above Solana data. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/) and [Helius](https://helius.xyz/).

Spire is a Solana-focused on-chain data platform that aims to provide in-depth data and insights to add value to the Solana ecosystem. 
Focusing on analyses we think are interesting, we provide a place where users and developers can regularly check for Solana ecosytem information, as well as deeper dives into specific areas.

**View the dashboard at https://spire.fyi/**

----
Spire is currently a beta project and is in active development. Reach out on Twitter with questions and comments, or file an issue here!
Follow us on Twitter [@spire_fyi](https://twitter.com/spire_fyi)

## Overview
Spire is a work in progress and in active development.

Spire uses [`streamlit`](https://streamlit.io/) to build our interactive dashboard.

Historical data is sourced from [Flipside Crypto](https://flipsidecrypto.xyz/) using their [SDK](https://sdk.flipsidecrypto.xyz/shroomdk).
Queries used for this can be found [here](sql).

[Helius](https://helius.xyz/) is used to acquire NFT metadata information, essential for NFT royalty analyses.

### Projects
- [NFT Royalties analysis](https://spire.fyi/NFT_Royalties): Which users pay royalties when this is optional? What is the potential loss in revenue from royalties?
  - Initial work focuses on Magic Eden sales since royalties became optional (15-Oct-2022), and only on sales of collection in the 99th percentile of volume. In the future, this tool will be expanded to all sales, a larger date range, and more collections
- [Program usage analysis](https://spire.fyi/Program_Usage): What are the top Solana programs used per day? How is this different for new users vs all users?
- Coming soon:
  - Network analysis of Program usage

## Team:
- LTirrell: [@ltirrell_](https://twitter.com/ltirrell_)
- Anduril: [@AndurilData](https://twitter.com/AndurilData)
