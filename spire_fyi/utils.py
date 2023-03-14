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
from helius import NFTAPI, BalancesAPI
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from shroomdk import ShroomDK
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
sdk = ShroomDK(API_KEY)
rpc_url = "https://rpc.helius.xyz/?api-key=f09ecb19-af19-427c-b4e6-31580b74c837"

LAMPORTS_PER_SOL = 1_000_000_000
IPFS_RESOLVER_URL = "https://cloudflare-ipfs.com/ipfs/"

query_base = "https://next.flipsidecrypto.xyz/edit/queries"
api_base = "https://api.flipsidecrypto.com/api/v2/queries"

helius_key = st.secrets["helius"]["api_key"]

agg_method_dict = {
    "mean": "Average usage within date range",
    "sum": "Total usage within date range",
    "max": "Max daily usage during date range",
}
metric_dict = {
    "TX_COUNT": "Transaction Count",
    "SIGNERS": "Number of signers",
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
        query_result_set = sdk.query(query, cached=False)
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
        r = requests.post(label_url, json={"accountHashes": list(id_set), "fields": ["*"]})
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


def load_program_label_df():
    fs_labs = pd.read_csv("data/program_flipside_labels.csv")
    solfm_labs = pd.read_csv("data/program_solana_fm_labels.csv")
    manual_labs = pd.read_csv("data/program_manual_labels.csv")
    labs = pd.concat([fs_labs, manual_labs])
    merged = labs.merge(solfm_labs, on="ADDRESS", how="outer")
    return merged


def add_program_labels(df):
    label_df = load_program_label_df()
    df = df.merge(label_df, left_on="PROGRAM_ID", right_on="ADDRESS", how="left").drop(
        axis=1, columns=["ADDRESS", "BLOCKCHAIN"]
    )
    df.loc[df.PROGRAM_ID == "ComputeBudget111111111111111111111111111111", "LABEL"] = "solana"
    return df


def apply_program_name(row):
    prog_id = row.PROGRAM_ID
    address_name = row.ADDRESS_NAME
    label = row.LABEL
    friendly_name = row.FriendlyName
    if pd.isna(address_name):
        if pd.isna(friendly_name):
            return prog_id
        else:
            return friendly_name
    else:
        try:
            return f"{label.title()}: {address_name.title()}"
        except AttributeError:
            return address_name


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
        d = f"{int(date_range[:-1])+1}d"
        chart_df = df.copy()[df.Date >= (datetime.datetime.today() - pd.Timedelta(d))]

    if exclude_solana:
        chart_df = chart_df[chart_df.LABEL != "solana"]
    if exclude_oracle:
        chart_df = chart_df[~chart_df.LABEL.isin(["pyth", "switchboard"])]
        chart_df = chart_df[~chart_df.FriendlyName.isin(["SwitchBoard V2 Program", "Chainlink Program"])]
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
def load_labeled_program_data(new_users_only=False):
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
def load_weekly_user_data():
    df = pd.read_csv("data/weekly_users.csv")
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


@st.cache_data(ttl=60)
def load_weekly_new_user_data():
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
        pd.read_json(
            "https://node-api.flipsidecrypto.com/api/v2/queries/3d71d36a-ca9a-4fcf-97a9-802dbbc2b98d/data/latest"
        )
        .rename(
            columns={
                "WEEK": "Date",
                "MARKETPLACE": "Marketplace",
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
        pd.read_json(
            "https://node-api.flipsidecrypto.com/api/v2/queries/ac73a290-6f2e-4e15-be6f-203562bbd911/data/latest"
        )
        .rename(columns={"DATE": "Date", "AVERAGE_MINTS": "Average Mints per Address"})
        .sort_values(by="Date", ascending=False)
        .reset_index(drop=True)
    )
    mints_by_chain = (
        pd.read_json(
            "https://node-api.flipsidecrypto.com/api/v2/queries/d40f62a3-d937-460c-938d-a699b5be9f6e/data/latest"
        )
        .rename(columns={"DATE": "Date", "CHAIN": "Chain", "MINTS": "Count", "MINTERS": "Unique Users"})
        .sort_values(by="Date", ascending=False)
        .reset_index(drop=True)
    )
    mints_by_chain["Type"] = "Mints"
    sales_by_chain = pd.read_json(
        "https://node-api.flipsidecrypto.com/api/v2/queries/d79d5037-6777-44eb-a881-e0243af11cea/data/latest"
    ).rename(columns={"DATE": "Date", "CHAIN": "Chain", "SALES": "Count", "BUYERS": "Unique Users"})
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
            "https://node-api.flipsidecrypto.com/api/v2/queries/ffd713f1-4d05-4f3e-82b8-dc2c87db6691/data/latest"  # fork
            # "https://node-api.flipsidecrypto.com/api/v2/queries/7572e1e3-fbfb-4dd4-9d45-dd6cde7f42df/data/latest"  # original, see https://twitter.com/BlumbergKellen/status/1601245496789463045
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
    df = pd.read_json(
        "https://node-api.flipsidecrypto.com/api/v2/queries/398c8e9a-7178-4816-ae4a-74c3181dcafc/data/latest"
    )
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
        pd.read_json(
            "https://node-api.flipsidecrypto.com/api/v2/queries/02d025f0-9eb1-4bff-b317-299c8b251178/data/latest"
        )
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
        query_result_set = sdk.query(query)
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


def resolve_ipfs_uri(uri):
    parsed = urlparse(uri)
    if parsed.scheme == "ipfs":
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
    if "ipfs" in url:
        time.sleep(1)
    try:
        data = requests.get(url).json()
    except:
        data = requests.get(url)
        print(data.text)
        raise
    info = {"uri": uri}
    info["description"] = data["description"]
    info["image"] = resolve_ipfs_uri(data["image"])
    try:
        info["programIds"] = data["xnft"]["programIds"]
    except KeyError:
        pass
    try:
        info = {**info, **get_xnft_contacts(data["xnft"]["contact"])}
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
@st.cache_data(ttl=1800)
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


@st.cache_data(ttl=3600)
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


@st.cache_data(ttl=3600)
def get_backpack_addresses(username):
    if username == "":
        return ""
    try:
        url = "https://xnft-api-server.xnfts.dev/v1/users/fromUsername"
        r = requests.get(url, params={"username": username})
        j = r.json()
        addresses = j["user"]["public_keys"]
        for x in addresses:
            if x["blockchain"] == "solana":
                return x["public_key"]
    except KeyError:
        return None


def get_mad_lad_mints():
    nft = NFTAPI(helius_key)
    # TODO: shouldn't have to deal with pagination due to collection size, but may need to eventually?
    mintlist = nft.get_mintlists(
        verified_collection_addresses=["FCk24cq1pYhQo5MQYKHf5N9VnY8tdrToF7u6gvvsnGrn"],
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
