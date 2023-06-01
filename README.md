# spire_fyi

<img alt="Spire" src="assets/images/spire_logo.png" width="150" height="150">

> A viewpoint above Solana data. Insights and on-chain data analytics, inspired by the community and accessible to all. Powered by [Flipside Crypto](https://flipsidecrypto.xyz/), [Helius](https://helius.xyz/), [SolanaFM](https://docs.solana.fm/) and [HowRare](https://howrare.is/api).

Spire is a Solana-focused on-chain data platform that aims to provide in-depth data and insights to add value to the Solana ecosystem. 
Focusing on analyses we think are interesting, we provide a place where users and developers can regularly check for Solana ecosytem information, as well as deeper dives into specific areas.

**Visit Spire at https://spire.fyi/**

----
Spire is currently a beta project and is in active development. Reach out on Twitter with questions and comments, or file an issue here!
Follow us on Twitter [@spire_fyi](https://twitter.com/spire_fyi)

## Overview
Spire is a work in progress and in active development.

Spire uses [`streamlit`](https://streamlit.io/) to build our interactive dashboard.

Historical data is sourced from [Flipside Crypto](https://flipsidecrypto.xyz/) using their [Python SDK](https://docs.flipsidecrypto.com/flipside-api/key-concepts).
Queries used for this can be found [here](sql).

[Helius](https://helius.xyz/) is used to acquire NFT metadata and mintlist information, essential for NFT royalty analyses.

[Solana FM](https://solana.fm/) is used as our default Solana explorer.
Additionally Spire uses their API for Solana Statistics and indexing of programs using their IDL.

Data used for analysis is available for download as a CSV!
## Projects
### In progress
#### [Solana Grizzlython](https://solana.com/grizzlython):
- [xNFT Backpack Overview Page](https://spire.fyi/xNFT_Backpack): With the recent beta launch of the [Backpack Wallet](https://twitter.com/xNFT_Backpack), Spire analyzed the on-chain usage of these wallets interacting with the ["executable NFT" (xNFT) Program](https://solana.fm/address/xnft5aaToUM4UFETUQfj7NUDUBdvYHTVhNFThEYTm55), including:
  - Installs of each xNFT over time
  - Top xNFTs by installs and Ratings
  - Daily new xNFT users
  - A breakdown of xNFTs per user
  - [Mad Lads](https://twitter.com/MadLadsNFT) Madlist status (the NFT project from the Backpack team)
    - Top users by Madlist count
    - Mad List Tracker: see how many spots have been claimed so far
  - Backpack Username Lookup: get the address from a Backpack username, or get the username from an address. Also includes some basic usage statistics
- Infrastructure Updates: Spire is continuously working to improve our app, and is building tooling to automatically update and combine data from various sources, with caching for better performance.
  - [`spire-fyi-clj`](https://github.com/spire-fyi/spire-fyi-clj), a Clojure application to support the data collection for spire.fyi, was built for this purpose. Currently, this package schedules, executes and stores query results from the [Flipside Crypto API](https://docs.flipsidecrypto.com/flipside-api/key-concepts) with work in progress to integrate our other data sources (Helius, Solana FM and others)
- [DeFi Updates (`DeFi` tab at the top of the Overview page](https://spire.fyi): Breakdown of transaction and user counts for various DeFi protocols, view the ratio of Fee Payers to Signers, and track new users over time.
- [Fee Tracking (`Ecosystem` tab at the top of the Overview page)](https://spire.fyi): The mean, median, 95th and 99th percentile of daily fees per transaction are shown, allowing users to track prioritization fee usage. Additionally, track the total daily transactions fees generated and burned.

### Coming soon:
- Network analysis of Program usage
- More real-time data and user interaction
- Updated infrastructure

### Completed
#### [Magic Eden Creator Monetization Hackathon](https://blog.magiceden.io/winners-announcement-magic-eden-creator-monetization-hackathon) (2nd place, Royalty Tracking API Track)
- [NFT Royalties analysis](https://spire.fyi/NFT_Royalties): Which users pay royalties when this is optional? What is the potential loss in revenue from royalties?
  - Initial work focuses on Magic Eden sales since royalties became optional (15-Oct-2022), and only on sales of collection in the 99th percentile of volume. In the future, this tool will be expanded to all sales, a larger date range, and more collections
#### [Sandstorm Hackathon](https://www.sandstormhackathon.com/) (1st place, Analytics Track; 2nd place, Helius NFTs track)
- [Program usage analysis](https://spire.fyi/Program_Usage): What are the top Solana programs used per day? How is this different for new users vs all users?
- [Whale Watcher](https://spire.fyi/Whale_Watcher): Track the high value swaps, transfers and NFT sales that have occurred in the past week. Click on a data point to view the transaction on Solana FM for more details.
- [Bonk](https://spire.fyi/Bonk): View the Bonk Burn Leaderboard, and other data about Solana's community dog coin.
- [Overview Updates](https://spire.fyi): A referesh of the main overview page. Click a tab (`Ecosystem`, `NFT`, `Programs` or `DeFi`) to view highlights of a particular topic.

## Usage Instructions
While Spire is meant to be viewed from its [web page](https://spire.fyi/), it can be ran locally using either Python or within a Docker container.

Since there are API keys required to access some data, it is necessary to get these first.
Get a [Flipside API Key](https://flipsidecrypto.xyz/account/api-keys) and a [Helius API Key](https://helius.xyz/), and save them to a `.streamlit/secrets.toml` file:
```toml
[flipside]
api_key = "FLIPSIDE_KEY_HERE"

[helius]
api_key = "HELIUS_KEY_HERE"
```

Then follow one of the sets of instructions below.

### Docker 
With [Docker and Docker Compose](https://docs.docker.com/engine/install/) installed, run the following command:
```
docker compose up app
```
Go to `localhost:8501` in a web browser to view the app.

### Python
With [Poetry](https://python-poetry.org/) installed, run the following command to install spire and its dependencies:
```
poetry install
```
Next, run this command to start the streamlit server:
```
poetry run streamlit run Overview.py
```
Finally, go to `localhost:8501` in a web browser to view the app.


## Team:
- LTirrell: [@ltirrell_](https://twitter.com/ltirrell_)
- Anduril: [@AndurilData](https://twitter.com/AndurilData)
- jjttjj: [@jjttjj](https://twitter.com/jjttjj)
