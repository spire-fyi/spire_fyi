from typing import Dict, Iterable, Union

import asyncio
import datetime
import logging
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import requests
import solders
import streamlit as st
from flipside import Flipside
from helius import NFTAPI, BalancesAPI
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from solana.rpc.async_api import AsyncClient

from .xnft.accounts import Xnft

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
__all__ = [
    "LAMPORTS_PER_SOL",
    "query_base",
    "api_base",
    "add_program_labels",
    "apply_program_name",
    "combine_flipside_date_data",
    "get_flipside_labels",
    "get_program_chart_data",
    "load_labeled_program_data",
    "load_weekly_new_program_data",
    "load_weekly_program_data",
    "load_weekly_user_data",
    "load_weekly_last_use_data",
    "load_weekly_days_since_last_use_data",
    "load_defi_data",
    "agg_method_dict",
    "metric_dict",
    "get_program_ids",
    "load_royalty_data",
    "load_sol_daily_price",
    "load_top_nft_info",
    "get_random_image",
    "reformat_columns",
    "load_flipside_api_data",
    "run_query_and_cache",
    "get_short_address",
    "get_nft_mint_data",
    "get_bonk_balance",
    "load_fees",
    "load_fee_data",
    "get_native_balances",
    "load_xnft_data",
]

API_KEY = st.secrets["flipside"]["api_key"]
sdk = Flipside(API_KEY)

helius_key = st.secrets["helius"]["api_key"]
rpc_url = f"https://rpc.helius.xyz/?api-key={helius_key}"

LAMPORTS_PER_SOL = 1_000_000_000
IPFS_RESOLVER_URL = "https://cloudflare-ipfs.com/ipfs"
IPFS_RESOLVER_ALT_URL = "https://ipfs.io/ipfs"

query_base = "https://flipsidecrypto.xyz/edit/queries"
api_base = "https://api.flipsidecrypto.com/api/v2/queries"

agg_method_dict = {
    "mean": "Average usage within date range",
    "sum": "Total usage within date range",
    "max": "Max daily usage during date range",
}
metric_dict = {
    "TX_COUNT": "Transaction Count",
    "SIGNERS": "Number of signers",
    "Total Stake": "Total Stake (SOL)",
    "Txs": "Transaction Count",
    "Wallets": "Unique Wallets",
    "Amount": "Amount",
}

dex_programs = {
    "Mango Markets": [
        "mv3ekLzLbnVPNxjSKvqBpU3ZeZXPQdEC3bp5MDEBG68",
        "5fNfvyp5czQVX77yoACa3JJVEhdRaWjPuazuWgjhTqEH",
        "JD3bq9hGdy38PuWQ4h2YJpELmHVGPPfFSuFkpzAd9zfu",
    ],
    "Serum": [
        "J2NhFnBxcwbxovE7avBQCXWPgfVtxi5sJfz68AH6R2Mg",
        "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin",
        "22Y43yTVxuUkoRKdm9thyRhQ3SdgQS7c7kB6UNCiaczD",
        "EUqojwWA2rd19FZrzeBncJsm38Jm1hEhE3zsmX3bRc2o",
        "BJ3jrUzddfuSrZHXSCxMUUQsjKEyLmuuyZebkcaFp2fg",
        "4ckmDgGdxQoPDLUkDT3vHgSAkzA3QRdNq5ywwY4sUSJn",
    ],
    "Openbook": [
        "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX",
    ],
    "Aldrin": [
        "AMM55ShdkoGRB5jVYPjWziwk8m5MpwyDgsMWHaMSQWH6",
        "CURVGoZn8zycx6FXwwevgBTB2gVvdbGTEpvMJDbgs2t4",
    ],
    "Jupiter Aggregator": [
        "JUP6i4ozu5ydDCnLiMogSckDPpbtr7BJ4FtzYWkb5Rk",
        "JUP2jxvXaqu7NQY1GmNF4m1vodw12LVXYxbFL2uJvfo",
        "JUP3c2Uh3WA4Ng34tw6kPd2G4C5BB21Xo36Je1s32Ph",
        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
    ],
    "Raydium": [
        "RVKd61ztZW9GUwhRbbLoYVRE5Xf1B2tVscKqwZqXgEr",
        "27haf8L6oxUeXrHrgEgsexjSY5hbVUWEmvv9Nyxg8vQv",
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
        "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",
    ],
    "Saber": [
        "SSwpkEEcbUqx4vtoEByFjSkhKdCT862DNVb52nZg1UZ",
    ],
    "Mercurial": [
        "MERLuDFBMmsHnsBPZw2sDQZHvXFMwp8EdjudcU2HKky",
    ],
    "Orca": [
        "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1",
        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
        "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",
    ],
    "Step Finance": [
        "SSwpMgqNDsyV7mAgN9ady4bDVu5ySjmmXejXvy2vLt1",
    ],
    "Cykura": [
        "cysPXAjehMpVKUapzbMCCnpFxUFFryEWEaLgnb9NrR8",
    ],
    "Crema": [
        "6MLxLqiXaaSUpkgMnWDTuejNZEz3kE7k2woyHGVFw319",
    ],
    "Lifinity": [
        "EewxydAPCCVuNEyrVN68PuSYdQ7wKn27V9Gjeoi8dy3S",
    ],
    "Stepn": [
        "Dooar9JkhdZ7J3LHN3A7YCuoGRUggXhQaG4kijfLGU2j",
    ],
    "Invariant": [
        "HyaB3W9q6XdA5xwpU4XnSZV94htfmbmqJXZcEbRaJutt",
    ],
    "GooseFX": [
        "7WduLbRfYhTJktjLw5FDEyrqoEv61aTTCuGAetgLjzN5",
    ],
}

liquid_staking_tokens = {
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So": ("mSOL", "Marinade staked SOL (mSOL)"),
    "7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj": ("stSOL", "Lido Staked SOL"),
    "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn": ("JitoSOL", "Jito Staked SOL"),  #
    "7Q2afV64in6N6SeZsAAB81TJzwDoD6zpqmHkzi9Dcavn": ("jSOL", "JPOOL Solana Token"),
    "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm": ("scnSOL", "Socean staked SOL"),
    "CgnTSoL3DgY9SFHxcLj6CgCgKKoTBr6tp4CPAEWy25DE": ("cgntSOL", "Cogent SOL"),  #
    "LAinEtNLgpmCP9Rvsf5Hn8W6EhNiKLZQti1xfWMLy6X": ("laineSOL", "Laine Stake"),  #
    "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1": ("bSOL", "BlazeStake Staked SOL (bSOL)"),
    "GEJpt3Wjmr628FqXxTgxMce1pLntcPV4uFi8ksxMyPQh": ("daoSOL", "daoSOL Token"),
    "BdZPG9xWrG3uFrx2KrUW1jT4tZ9VKPDWknYihzoPRJS3": ("prtSOL", "prtSOL (Parrot Staked SOL)"),  #
}


def combine_flipside_date_data(data_dir, add_date=False, with_program=False, nft_royalty=False):
    d = Path(data_dir)
    data_files = d.glob("*.csv")
    if nft_royalty:
        data_files_todo = {}
        # TODO: get the most recent / highest mints for each nft collection
    dfs = []
    for x in data_files:
        df = pd.read_csv(x)
        if add_date and not with_program:
            date_str = x.name.split("_")[-1].split(".csv")[0]
            df["DATE"] = date_str
        if add_date and with_program:
            date_str = x.name.split("_")[-2]
            df["DATE"] = date_str
        dfs.append(df)
    combined_df = pd.concat(dfs)
    return combined_df


def query_flipside_data(query_info, save=True):
    query, output_file = query_info
    query_file = Path(output_file.parent, "queries", f"{output_file.stem}.sql")
    logging.info(f"#@# Querying data for {output_file} ...")
    query_file.parent.mkdir(exist_ok=True, parents=True)
    with open(query_file, "w") as f:
        f.write(query)
    try:
        query_result_set = sdk.query(
            query,
            ttl_minutes=120,
            timeout_minutes=30,
            retry_interval_seconds=1,
            page_size=1000000,
            page_number=1,
            cached=False,
        )
        if save:
            df = pd.DataFrame(query_result_set.rows, columns=query_result_set.columns)
            output_file.parent.mkdir(exist_ok=True, parents=True)
            df.to_csv(
                output_file,
                index=False,
            )
        logging.info(f"#@# Saved {output_file}")
        return output_file
    except Exception as e:
        logging.info(f"[ERROR] ({query_file}) {e}")
        raise


def create_label_query(addresses):
    env = Environment(loader=FileSystemLoader("./sql"))
    template = env.get_template("sdk_labels_sol.sql")
    query = template.render({"addresses": addresses})
    return query


def get_flipside_labels(df, output_prefix, col):
    # #TODO combine with solana.fm
    ids = df[col].unique()
    labels = create_label_query(ids)
    query_flipside_data([labels, Path(f"data/{output_prefix}_flipside_labels.csv")])


def get_solana_fm_labels(df, output_prefix, col):
    ids = df[col].unique()
    split_ids = [ids[i : i + 100] for i in range(0, len(ids), 100)]

    label_url = "https://api.solana.fm/v0/accounts"
    label_results = []
    for i, id_set in enumerate(split_ids):
        if i % 4 == 0:
            time.sleep(1)
        r = requests.post(label_url, json={"accountHashes": list(id_set)})
        res = r.json()["result"]
        for x in res:
            try:
                data = x["data"]
                data["ADDRESS"] = x["accountHash"]
                label_results.append(data)
            except KeyError:
                pass
    df = pd.DataFrame(label_results).sort_values(by="ADDRESS").reset_index(drop=True)
    df = df.rename(columns={x: (x[0].upper() + x[1:]).replace("_", " ") for x in df.columns})
    df.to_csv(f"data/{output_prefix}_solana_fm_labels.csv", index=False)


def load_program_label_df(prefix="program", use_manual=True, sfm_only=False):
    solfm_labs = pd.read_csv(f"data/{prefix}_solana_fm_labels.csv")
    if sfm_only:
        return solfm_labs
    else:
        fs_labs = pd.read_csv(f"data/{prefix}_flipside_labels.csv")
        if use_manual:
            manual_labs = pd.read_csv(f"data/{prefix}_manual_labels.csv")
            labs = pd.concat([fs_labs, manual_labs])
        else:
            labs = fs_labs
        merged = labs.merge(solfm_labs, on="ADDRESS", how="outer")
        return merged


def add_program_labels(
    df,
    left_on="PROGRAM_ID",
    right_on="ADDRESS",
    drop=["ADDRESS", "BLOCKCHAIN"],
    rename_solana_label=True,
    prefix="program",
    use_manual=True,
    sfm_only=False,
):
    label_df = load_program_label_df(prefix, use_manual, sfm_only)
    df = df.merge(label_df, left_on=left_on, right_on=right_on, how="left").drop(axis=1, columns=drop)
    if rename_solana_label:
        df.loc[df.PROGRAM_ID == "ComputeBudget111111111111111111111111111111", "LABEL"] = "solana"
    return df


def apply_program_name(
    row,
    address_col="PROGRAM_ID",
    address_name_col="ADDRESS_NAME",
    label_col="LABEL",
    friendly_name_col="FriendlyName",
):
    address = row[address_col]
    address_name = row[address_name_col]
    label = row[label_col]
    friendly_name = row[friendly_name_col]
    if pd.isna(address_name):
        if pd.isna(friendly_name):
            return address
        else:
            return friendly_name
    else:
        try:
            return f"{label.title()}: {address_name.title()}"
        except AttributeError:
            return address_name


@st.cache_data(ttl=3600)
def get_program_chart_data(
    df,
    metric,
    agg_method,
    date_range,
    exclude_solana,
    exclude_oracle,
    programs,
):
    if date_range == "All dates":
        chart_df = df.copy()
    elif date_range == "Year to Date":
        chart_df = df.copy()[df.Date >= "2022-01-01"]
    else:
        chart_df = df.copy()[df.Date >= (datetime.datetime.today() - pd.Timedelta(date_range))]

    if exclude_solana:
        chart_df = chart_df[chart_df.LABEL != "solana"]
    if exclude_oracle:
        chart_df = chart_df[~chart_df.LABEL.isin(["pyth", "switchboard"])]
        chart_df = chart_df[~chart_df.FriendlyName.isin(["SwitchBoard V2 Program", "Chainlink Program"])]
        chart_df = chart_df[~chart_df.LABEL_SUBTYPE.isin(["oracle"])]
    if type(programs) == int:
        program_ids = (
            chart_df.groupby("PROGRAM_ID")
            .agg({metric: agg_method})
            .sort_values(by=metric, ascending=False)
            .iloc[:programs]
            .index
        )
    else:
        program_ids = programs
    chart_df = (
        chart_df[chart_df.PROGRAM_ID.isin(program_ids)]
        .sort_values(by=["Date", metric], ascending=False)
        .reset_index(drop=True)
    )

    return chart_df


@st.cache_data(ttl=600)
def load_labeled_program_data(new_users_only=False, user_type=None):
    if user_type == "Signers":
        if new_users_only:
            return pd.read_csv("data/programs_new_users_all_signers_labeled.csv.gz")
        else:
            return pd.read_csv("data/programs_all_signers_labeled.csv.gz")
    else:
        if new_users_only:
            return pd.read_csv("data/programs_new_users_labeled.csv.gz")
        else:
            return pd.read_csv("data/programs_labeled.csv.gz")


@st.cache_data(ttl=60)
def load_weekly_program_data():
    df = pd.read_csv("data/weekly_program.csv")
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


@st.cache_data(ttl=60)
def load_weekly_new_program_data():
    df = pd.read_csv("data/weekly_new_program.csv")
    df = df.sort_values(by="WEEK")
    df = df.reset_index(drop=True)
    df["Cumulative Programs"] = df["New Programs"].cumsum()
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


@st.cache_data(ttl=60)
def load_weekly_user_data(user_type="Fee Payers"):
    if user_type != "Fee Payers":
        df = pd.read_csv("data/weekly_users_all_signers.csv")
    else:
        df = pd.read_csv("data/weekly_users.csv")
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


@st.cache_data(ttl=60)
def load_weekly_new_user_data(user_type="Fee Payers"):
    if user_type != "Fee Payers":
        df = pd.read_csv("data/weekly_new_users_all_signers.csv")
    else:
        df = pd.read_csv("data/weekly_new_users.csv")
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    df = df.sort_values(by="WEEK")
    df = df.rename(columns={"NEW_USERS": "New Users"})
    df["Cumulative Users"] = df["New Users"].cumsum()
    return df


@st.cache_data(ttl=1800)
def load_nft_data():
    main_data = (
        pd.read_json(f"{api_base}/2b945162-59a9-4ccc-95ee-fca67ac142c4/data/latest")
        .rename(
            columns={
                "WEEK": "Date",
                "MARKETPLACE_NORMALIZED": "Marketplace",
                "TXS": "Transaction Count",
                "BUYERS": "Buyers",
                "SELLERS": "Sellers",
                "NFTS_SOLD": "Unique NFTs Sold",
                "SOL_AMOUNT": "Sale Amount (SOL)",
            }
        )
        .sort_values(by="Date", ascending=False)
        .reset_index(drop=True)
    )
    main_data["Date"] = pd.to_datetime(main_data["Date"])
    buyers_sellers = main_data.melt(
        id_vars=[
            "Date",
            "Marketplace",
            "Transaction Count",
            "Unique NFTs Sold",
            "Sale Amount (SOL)",
        ]
    )
    marketplace_info = main_data.melt(
        id_vars=[
            "Date",
            "Buyers",
            "Sellers",
            "Transaction Count",
            "Unique NFTs Sold",
            "Sale Amount (SOL)",
        ]
    )
    mints_by_purchaser = (
        pd.read_json(f"{api_base}/04be6d7d-b5cd-4c11-9f73-68288e1353d4/data/latest")
        .rename(columns={"DATE": "Date", "AVERAGE_MINTS": "Average Mints per Address"})
        .sort_values(by="Date", ascending=False)
        .reset_index(drop=True)
    )
    mints_by_purchaser["Date"] = pd.to_datetime(mints_by_purchaser["Date"])
    mints_by_chain = (
        pd.read_json(f"{api_base}/88cfaf1c-e485-4926-817f-61ed261d9cfb/data/latest")
        .rename(columns={"DATE": "Date", "CHAIN": "Chain", "MINTS": "Count", "MINTERS": "Unique Users"})
        .sort_values(by="Date", ascending=False)
        .reset_index(drop=True)
    )
    mints_by_chain["Type"] = "Mints"
    mints_by_chain["Date"] = pd.to_datetime(mints_by_chain["Date"])
    sales_by_chain = pd.read_json(f"{api_base}/7daf5636-2364-4281-b1cb-2d44ae1bcffd/data/latest").rename(
        columns={"DATE": "Date", "CHAIN": "Chain", "SALES": "Count", "BUYERS": "Unique Users"}
    )
    sales_by_chain["Date"] = pd.to_datetime(sales_by_chain["Date"])
    sales_by_chain["Type"] = "Sales"
    by_chain_data = (
        pd.concat([mints_by_chain, sales_by_chain])
        .sort_values(by=["Type", "Date", "Chain"], ascending=False)
        .reset_index(drop=True)
    )[["Date", "Chain", "Unique Users", "Type", "Count"]]
    return buyers_sellers, marketplace_info, mints_by_purchaser, by_chain_data


@st.cache_data(ttl=1800)
def load_royalty_data():
    df = (
        pd.read_json(
            f"{api_base}/ffd713f1-4d05-4f3e-82b8-dc2c87db6691/data/latest"  # fork
            # f"{api_base}/7572e1e3-fbfb-4dd4-9d45-dd6cde7f42df/data/latest"  # original, see https://twitter.com/BlumbergKellen/status/1601245496789463045
        )
        .sort_values(by=["MONTH"])
        .drop(columns=["N_DAYS", "PCT_SALES_AMOUNT"])
        .reset_index(drop=True)
        .rename(
            columns={
                "MONTH": "Date",
                "SALES_AMOUNT": "Sales Amount (SOL)",
                "M_AMT": "Martketplace Fee Amount (SOL)",
                "R_AMT": "Royalty Fee Amount (SOL)",
                "PCT_NO_ROYALTIES": "Percent of Sales with Royalty Payments",
                "M_PCT": "Martketplace Fee Percentage",
                "R_PCT": "Royalty Fee Percentage",
                "AVG_DAILY_ROYALTIES": "Average Daily Royalties (SOL)",
                "MONTHLY_SALES_AMOUNT": "Monthly Sales Amount (SOL)",
                "MONTHLY_ROYALTIES": "Monthly Royalties Amount (SOL)",
                "MONTHLY_ROYALTY_PCT": "Monthly Royalty Percentage",
                "SALES_AMOUNT_USD": "Sales Amount (USD)",
                "M_AMT_USD": "Martketplace Fee Amount (USD)",
                "R_AMT_USD": "Royalty Fee Amount (USD)",
            }
        )
    )
    return df


@st.cache_data(ttl=1800)
def load_sol_daily_price():
    df = pd.read_json(f"{api_base}/398c8e9a-7178-4816-ae4a-74c3181dcafc/data/latest")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date")
    return df


@st.cache_data(ttl=1800)
def load_top_nft_info():
    df = (
        pd.read_csv("data/top_nft_sales_metadata_with_royalties.csv.gz")
        .sort_values(by=["BLOCK_TIMESTAMP"])
        .drop(columns=["uri_y"])
        .rename(columns={"uri_x": "uri"})
        .reset_index(drop=True)
    )
    df["BLOCK_TIMESTAMP"] = pd.to_datetime(df["BLOCK_TIMESTAMP"])
    df["paid_no_royalty"] = ~df["paid_royalty"]
    df["Date"] = df.BLOCK_TIMESTAMP.dt.normalize()
    # #HACK: get rid of incomplete date
    df = df[df.Date < "2022-12-10"]
    # #HACK: issue with some rows showing up twice for 2 NFT collections; dropping duplicates
    df = df.drop_duplicates(subset="TX_ID")
    # #TODO: handle situations where the seller is the creator
    df = df[df.SELLER != df.creator_address]
    # #HACK: removing 'CARD 1000 SOL' since there is very little information on the project
    # #TODO: remove all collections flagged on ME, or are known to be bad, from top projects
    df = df[df.Name != "CARD 1000 SOL"]
    # #HACK: some royalty payments are more than the expected amount
    df["paid_full_royalty"] = df["paid_full_royalty"] | (df.total_royalty_amount > df.expected_royalty)
    return df


@st.cache_data(ttl=600)
def get_random_image(df):
    num = np.random.randint(len(df))
    rand_row = df.iloc[num]
    r = requests.get(rand_row.uri)
    j = r.json()
    try:
        img_file = j["properties"]["files"][0]["uri"]
        if img_file.lower().endswith("gif"):
            img_file = img_file = j["properties"]["files"][1]["uri"]
    except:
        img_file = j["image"]

    try:
        response = requests.get(img_file)
        image = Image.open(BytesIO(response.content))
    except:
        image = None

    return num, image


@st.cache_data(ttl=1800)
def load_defi_data():
    df = (
        pd.read_json(f"{api_base}/02d025f0-9eb1-4bff-b317-299c8b251178/data/latest")
        .sort_values(by=["WEEK", "SWAP_PROGRAM"])
        .reset_index(drop=True)
        .rename(
            columns={
                "WEEK": "Date",
                "SWAP_PROGRAM": "Swap Program",
                "DAILY_TXS": "Transaction Count",
                "DAILY_BUYERS": "Unique Users",
            }
        )
    )
    return df


# #TODO: not used currently
def load_weekly_last_use_data():
    df = pd.read_csv("data/weekly_users_last_use.csv")
    datecols = ["LAST_USE"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


def load_weekly_days_since_last_use_data():
    df = pd.read_csv("data/weekly_days_since_last_use.csv")
    datecols = ["CREATION_DATE"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


def load_weekly_days_active_data():
    df = pd.read_csv("data/weekly_days_active.csv")
    datecols = ["CREATION_DATE"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


# #---


def get_program_ids(df):
    prog_list = []
    for agg_method in ["mean", "sum", "max"]:
        for metric in ["TX_COUNT", "SIGNERS"]:
            program_ids = (
                df.groupby("PROGRAM_ID")
                .agg({metric: agg_method})
                .sort_values(by=metric, ascending=False)
                .iloc[:30]
                .index
            )
            prog_list.extend(program_ids.to_list())
    return pd.unique(prog_list)


# sandstorm
@st.cache_data(ttl=300)
def reformat_columns(df: pd.DataFrame, datecols: Union[list, None]) -> pd.DataFrame:
    if datecols is not None:
        df[datecols] = df[datecols].apply(pd.to_datetime)
        # TODO: eventually use timezones. currently impossible to properly handle with altair and streamlit
        # for x in datecols:
        #     df[x] = pd.to_datetime(df[x], utc=True)
        df = df.sort_values(by=datecols).reset_index(drop=True)
    df = df.rename(columns={x: x.replace("_", " ").title() for x in df.columns})
    return df


@st.cache_data(ttl=3600)
def load_flipside_api_data(url: str, datecols: Union[list, None]) -> pd.DataFrame:
    df = pd.read_json(url)
    df = reformat_columns(df, datecols)
    return df


@st.cache_data(ttl=3600 * 6)
def run_query_and_cache(name, sql, param, force_update=False):
    today = datetime.date.today()
    cache_dir = Path("data/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    file_path = cache_dir / f"{today}_{name}_{param}.csv"
    if file_path.exists() and not force_update:
        return pd.read_csv(file_path)
    else:
        query = sql.format(param=param)
        query_result_set = sdk.query(
            query,
            ttl_minutes=120,
            timeout_minutes=30,
            retry_interval_seconds=1,
            page_size=1000000,
            page_number=1,
            cached=False,
        )
        df = pd.DataFrame(query_result_set.rows, columns=query_result_set.columns)
        df.to_csv(
            file_path,
            index=False,
        )
        return df


def get_short_address(address: str) -> str:
    return address[:6] + "..." + address[-6:]


@st.cache_data(ttl=3600)
def get_nft_mint_data(splits):
    nft_api = NFTAPI(helius_key)
    mint_data = []
    for x in splits:
        mints = nft_api.get_nft_metadata(list(x))
        mint_data.extend(mints)
    # HACK: just using names for now to get collection id
    names = []
    for x in mint_data:
        try:
            names.append(x["onChainData"]["data"]["name"])
        # #HACK: some bad data mint address data
        except TypeError:
            names.append("Unknown")
    collections = [x.split("-")[0].split("#")[0].strip() for x in names]
    collection_df = pd.DataFrame({"Mint": [x["mint"] for x in mint_data], "NFT Name": collections})
    return collection_df


@st.cache_data(ttl=3600)
def get_bonk_balance(address):
    if address == "":
        return ""
    try:
        balances_api = BalancesAPI(helius_key)
        bal = balances_api.get_balances(address)
        for x in bal["tokens"]:
            if x["mint"] == "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263":
                return x
    except:
        return


def load_fees(dates):
    data = []
    for d in dates:
        r = requests.get(f"https://api.solana.fm/v0/stats/tx-fees?date={d.strftime('%d-%m-%Y')}")
        data.append(r.json()["result"])

    fees = pd.DataFrame(data)
    fees["Date"] = pd.to_datetime(fees.date, dayfirst=True)
    fees["Fees"] = fees.totalTxFees / 10**9
    fees["Burn"] = fees["Fees"] / 2
    fees = fees[["Date", "Fees", "Burn"]]
    return fees


@st.cache_data(ttl=3600)
def load_fee_data():
    df = pd.read_csv("data/fees.csv")
    df["Date"] = pd.to_datetime(df.Date)
    return df


@st.cache_data(ttl=3600)
def get_native_balances(address):
    if address == "":
        return ""
    balances_api = BalancesAPI(helius_key)
    bal = balances_api.get_balances(address)
    return bal["nativeBalance"] / LAMPORTS_PER_SOL


async def lookup_xnft(xnft: str) -> Xnft:
    conn = AsyncClient(rpc_url)
    xnft_id = solders.pubkey.Pubkey.from_string(xnft)
    return await Xnft.fetch(conn, xnft_id)


def get_xnft_info(xnfts: Iterable[str]) -> dict:
    data = {}
    for x in xnfts:
        data[x] = asyncio.run(lookup_xnft(x)).to_json()
    return data


def create_xnft_info_df(xnft_info: Dict[str, dict]) -> pd.DataFrame:
    xnft_info_df = pd.DataFrame(xnft_info).T
    xnft_info_df["XNFT"] = xnft_info_df.index
    xnft_info_df = xnft_info_df.reset_index(drop=True)
    xnft_info_df["kind"] = xnft_info_df["kind"].apply(lambda x: x["kind"])
    xnft_info_df["tag"] = xnft_info_df["tag"].apply(lambda x: x["kind"])
    xnft_info_df["created_datetime"] = xnft_info_df["created_ts"].apply(
        lambda x: datetime.datetime.fromtimestamp(x).isoformat(sep=" ")
    )
    xnft_info_df["updated_datetime"] = xnft_info_df["updated_ts"].apply(
        lambda x: datetime.datetime.fromtimestamp(x).isoformat(sep=" ")
    )
    return xnft_info_df


def resolve_ipfs_uri(uri, use_alternate=False):
    parsed = urlparse(uri)
    if parsed.scheme == "ipfs":
        if use_alternate:
            url = f"{IPFS_RESOLVER_ALT_URL}/{parsed.netloc}"
        else:
            url = f"{IPFS_RESOLVER_URL}/{parsed.netloc}"
    else:
        url = uri
    return url


def get_xnft_contacts(contact: dict) -> dict:
    d = {}
    for k, v in contact.items():
        d[f"contact_{k}"] = v
    return d


def get_uri_info(uri: str) -> dict:
    url = resolve_ipfs_uri(uri)
    info = {"uri": uri}
    if "ipfs" in url:
        time.sleep(np.random.randint(2, 10))
        try:
            data = requests.get(url).json()
        except:
            logging.warning(f"Request failed for: {url} -- Retrying in 30s")
            time.sleep(30)
            try:
                data = requests.get(url).json()
            except:
                logging.warning(f"Request failed for: {url} -- Retrying in 60s with alternate resolver")
                time.sleep(60)
                try:
                    url = resolve_ipfs_uri(uri, use_alternate=True)
                    data = requests.get(url).json()
                except:
                    return info
    else:
        try:
            data = requests.get(url).json()
        except:
            return info
    info["description"] = data["description"]
    info["image"] = resolve_ipfs_uri(data["image"])
    try:
        info["programIds"] = data["xnft"]["programIds"]
    except KeyError:
        pass
    try:
        xnft_contact = data["xnft"]["contact"]
        if type(xnft_contact) == str:
            contact_info = {"Contact Other": xnft_contact}
        else:
            contact_info = get_xnft_contacts(xnft_contact)
            info = {**info, **contact_info}
    except KeyError:
        pass
    return info


def add_uri_info(xnft_info: pd.DataFrame) -> pd.DataFrame:
    # TODO: better caching
    data = []
    for x in xnft_info.uri.unique():
        data.append(get_uri_info(x))
    uri_info = pd.DataFrame(data)
    df = xnft_info.copy().merge(uri_info, on="uri")
    return df


@st.cache_data(ttl=60)
def load_xnft_data():
    df = pd.read_csv("data/xnft_create_install_all_info.csv")
    datecols = ["BLOCK_TIMESTAMP", "created_datetime", "updated_datetime"]
    df = reformat_columns(df, datecols)
    return df


# def grouping_with_other(x):
#     if
@st.cache_data(ttl=3600)
def aggregate_xnft_data(df, n=15):
    total_counts = (
        df.groupby(["Xnft", "Mint Seed Name"])["Tx Id"]
        .count()
        .reset_index()
        .rename(columns={"Tx Id": "Count"})
        .sort_values(by="Count", ascending=False)
        .reset_index(drop=True)
    )
    total_counts["Rank"] = total_counts.index + 1

    df["Rank"] = df.Xnft.apply(lambda x: total_counts[total_counts.Xnft == x].Rank.values[0])
    df["Display Name"] = df.apply(lambda x: x["Mint Seed Name"] if x.Rank <= n else "Other", axis=1)
    df["xNFT"] = df.apply(lambda x: x["Xnft"] if x.Rank <= n else "Other", axis=1)
    daily_counts = (
        df.groupby([pd.Grouper(key="Block Timestamp", axis=0, freq="D"), "Display Name", "xNFT"])
        .agg(Count=("Tx Id", "count"))
        .reset_index()
    )
    daily_counts["url"] = daily_counts["xNFT"].apply(
        lambda x: f"https://www.xnft.gg/app/{x}" if x != "Other" else "https://www.xnft.gg"
    )
    daily_counts["Block Timestamp"] = daily_counts["Block Timestamp"].dt.date

    total_counts["url"] = total_counts["Xnft"].apply(
        lambda x: f"https://www.xnft.gg/app/{x}" if x != "Other" else "https://www.xnft.gg"
    )

    total_reviews = (
        df.groupby(["Xnft", "Mint Seed Name"])[["Total Rating", "Num Ratings"]].max().reset_index()
    )
    total_reviews["Rating"] = total_reviews["Total Rating"] / total_reviews["Num Ratings"]

    totals = total_counts.merge(total_reviews, on=["Xnft", "Mint Seed Name"])
    # total_reviews = total_reviews.sort_values(by="Rating", ascending=False)
    totals = totals.rename(columns={"Xnft": "xNFT"})
    return daily_counts, totals


@st.cache_data(ttl=3600 * 24)
def get_backpack_usernames(
    addresses: Iterable, address_key="Collector", username_key="Username"
) -> pd.DataFrame:
    df = pd.read_csv("data/backpack_info.csv")
    cached = dict(zip(df.address.values, df.user.values))
    new_entries = []
    output = []
    for x in addresses:
        if x in cached.keys():
            username = cached[x]
        else:
            username = get_backpack_username(x)
            if username is not None:
                new_entries.append({"user": username, "address": x})
        output.append({address_key: x, username_key: username})
    if new_entries != []:
        df = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
        df.to_csv("data/backpack_info.csv", index=False)
    return pd.DataFrame(output)


@st.cache_data(ttl=3600 * 24)
def get_backpack_username(x):
    if x == "":
        return ""
    try:
        url = "https://xnft-api-server.xnfts.dev/v1/users/fromPubkey"
        r = requests.get(url, params={"publicKey": x, "blockchain": "solana"})
        j = r.json()
        username = j["user"]["username"]
    except KeyError:
        return None
    return username


@st.cache_data(ttl=3600 * 24)
def get_backpack_addresses(
    usernames: Iterable, address_key="Collector", username_key="Username"
) -> pd.DataFrame:
    df = pd.read_csv("data/backpack_info.csv")
    cached = dict(zip(df.user.values, df.address.values))
    new_entries = []
    output = []
    for x in usernames:
        if x in cached.keys():
            address = cached[x]
        else:
            address = get_backpack_address(x)
            if address is not None:
                new_entries.append({"user": x, "address": address})
        output.append({address_key: address, username_key: x})
    df = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
    df.to_csv("data/backpack_info.csv", index=False)
    return pd.DataFrame(output)


@st.cache_data(ttl=3600 * 24)
def get_backpack_address(username):
    if username == "":
        return ""
    try:
        url = "https://xnft-api-server.xnfts.dev/v1/users/fromUsername"
        r = requests.get(url, params={"username": username})
        j = r.json()
        addresses = j["user"]["public_keys"]
        for x in addresses:
            if x["blockchain"] == "solana":
                address = x["public_key"]
    except KeyError:
        return None
    return address


@st.cache_data(ttl=3600 * 24)
def add_backpack_username(df, address_col, username_col="Username"):
    df[username_col] = get_backpack_usernames(df[address_col].values)[username_col].values
    return df


def get_mintlist(verified_collection_addresses):
    nft = NFTAPI(helius_key)
    # TODO: shouldn't have to deal with pagination due to collection size, but may need to eventually?
    mintlist = nft.get_mintlists(
        verified_collection_addresses=verified_collection_addresses,
        first_verified_creators=[],
        limit=10000,
    )
    return mintlist


def get_mad_lad_df(mad_lad_mintlist):
    df = pd.DataFrame(mad_lad_mintlist["result"])
    df["username"] = df.name.str.split("@").str[1]
    return df


@st.cache_data(ttl=3600)
def load_mad_lad_data():
    df = pd.read_csv("data/mad_lad_all.csv")
    datecols = ["BLOCK_TIMESTAMP"]
    df = reformat_columns(df, datecols)
    return df


@st.cache_data(ttl=3600)
def load_xnft_new_users():
    df = pd.read_csv("data/xnft_new_users.csv")
    datecols = ["FIRST_TX_DATE"]
    df = reformat_columns(df, datecols)
    return df


@st.cache_data(ttl=3600)
def load_defi_data():
    dex_info = pd.read_csv("data/dex_info.csv")
    datecols = ["DATE"]
    dex_info = reformat_columns(dex_info, datecols)

    dex_new_user = pd.read_csv("data/dex_new_users.csv")
    datecols = ["FIRST_TX_DATE"]
    dex_new_user = reformat_columns(dex_new_user, datecols)

    dex_signers_fee_payers = pd.read_csv("data/dex_signers_fee_payers.csv")
    datecols = ["DATE"]
    dex_signers_fee_payers = reformat_columns(dex_signers_fee_payers, datecols)

    return dex_info, dex_new_user, dex_signers_fee_payers


@st.cache_data(ttl=3600)
def agg_defi_data(df, date_range):
    chart_df = df.copy()[
        df["Date"] >= (pd.to_datetime(datetime.datetime.today()) - pd.Timedelta(f"{int(date_range[:-1])}d"))
    ]

    top_dex_tx = chart_df.groupby(["Dex"]).Txs.sum().sort_values(ascending=False).reset_index()
    top_dex_tx["Rank"] = top_dex_tx.index + 1

    top_dex_user = chart_df.groupby(["Dex"])["Fee Payers"].sum().sort_values(ascending=False).reset_index()
    top_dex_user["Rank"] = top_dex_user.index + 1

    chart_df["Dex Grouped by Tx"] = chart_df.Dex.apply(
        lambda x: x if top_dex_tx[top_dex_tx.Dex == x].Rank.values[0] < 7 else "Other"
    )
    chart_df["Dex Grouped by Fee Payer"] = chart_df.Dex.apply(
        lambda x: x if top_dex_user[top_dex_user.Dex == x].Rank.values[0] < 7 else "Other"
    )

    tx_data = chart_df.groupby(["Date", "Dex Grouped by Tx"])[["Txs", "Fee Payers"]].sum().reset_index()
    tx_data["Rank"] = tx_data["Dex Grouped by Tx"].apply(
        lambda x: top_dex_tx[top_dex_tx.Dex == x].Rank.values[0] if x != "Other" else 10
    )
    tx_data["Normalized"] = tx_data["Txs"] / tx_data.groupby(["Date"])["Txs"].transform("sum")
    user_data = (
        chart_df.groupby(["Date", "Dex Grouped by Fee Payer"])[["Txs", "Fee Payers"]].sum().reset_index()
    )
    user_data["Rank"] = user_data["Dex Grouped by Fee Payer"].apply(
        lambda x: top_dex_user[top_dex_user.Dex == x].Rank.values[0] if x != "Other" else 10
    )
    user_data["Normalized"] = user_data["Fee Payers"] / user_data.groupby(["Date"])["Fee Payers"].transform(
        "sum"
    )
    return tx_data, user_data


@st.cache_data(ttl=3600)
def agg_defi_signers_data(df, date_range, protocol):
    chart_df = df.copy()[
        (df["Date"] >= (pd.to_datetime(datetime.datetime.today()) - pd.Timedelta(f"{int(date_range[:-1])}d")))
        & (df.Dex == protocol)
    ].reset_index(drop=True)
    chart_df["Normalized"] = chart_df["Wallets"] / chart_df.groupby(["Date"])["Wallets"].transform("sum")
    return chart_df


@st.cache_data(ttl=3600)
def agg_new_defi_users_data(df, date_range, protocol):
    chart_df = df.copy()[
        (
            df["First Tx Date"]
            >= (pd.to_datetime(datetime.datetime.today()) - pd.Timedelta(f"{int(date_range[:-1])}d"))
        )
        & (df.Dex == protocol)
    ].reset_index(drop=True)
    chart_df["url"] = chart_df["Program Id"].apply(lambda x: f"https://solana.fm/address/{x}")
    return chart_df


@st.cache_data(ttl=3600)
def add_rarity_data(df, rarity_df="data/madlads_rarity.csv", on="Mint", how="inner"):
    df2 = pd.read_csv(rarity_df)
    merged = df.merge(df2, on=on, how=how)
    return merged


# @st.cache_data(ttl=3600)
def load_staker_data():
    # TODO: move to combine_data
    df = pd.read_csv("data/staking_combined.csv.gz", low_memory=False)
    df = reformat_columns(df, ["DATE"])
    df = (
        df[["Date"] + df.columns.drop("Date").to_list()]
        .sort_values(by=["Date", "Total Stake"], ascending=False)
        .reset_index(drop=True)
    )
    return df


@st.cache_data(ttl=3600)
def get_stakers_chart_data(
    df,
    date_range,
    exclude_foundation,
    exclude_labeled,
    n_addresses,
    user_type,
    token,
):
    chart_df = df.copy()[df.Date >= (datetime.datetime.today() - pd.Timedelta(date_range))]

    if exclude_foundation:
        chart_df = chart_df[chart_df["Address Name"] != "Solana Foundation Delegation Account"]
    if exclude_labeled:
        chart_df = chart_df[(chart_df["Address Name"].isna()) & (chart_df["Friendlyname"].isna())]

    staker_chart_df = (
        chart_df.copy()
        .sort_values("Total Stake", ascending=False)
        .groupby("Date", as_index=False)
        .head(n_addresses)
        .sort_values(by=["Date", "Total Stake"], ascending=False)
        .reset_index(drop=True)
    )
    if user_type == "top_stakers":
        token_chart_df = staker_chart_df.copy()[staker_chart_df["Token Name"] == token]
    elif user_type == "top_holders":
        token_chart_df = (
            chart_df.copy()[(chart_df.Amount > 1) & (chart_df["Token Name"] == token)]
            .sort_values("Amount", ascending=False)
            .groupby(["Date", "Address", "Token"], as_index=False)
            .head(n_addresses)
            .sort_values(by=["Address", "Date"], ascending=False)
            .reset_index(drop=True)
        )

    return staker_chart_df, token_chart_df


@st.cache_data(ttl=3600)
def load_lst(filled=True):
    if filled:
        df = pd.read_csv("data/liquid_staking_token_holders.csv.gz")
    else:
        df = pd.read_csv("data/liquid_staking_token_holders_delta.csv")
    df = reformat_columns(df, ["DATE"])
    df = df.sort_values(by=["Address", "Token", "Date"])
    return df
