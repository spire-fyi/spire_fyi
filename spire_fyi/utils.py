import datetime
import logging
import time
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from jinja2 import Environment, FileSystemLoader
from shroomdk import ShroomDK

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
__all__ = [
    "add_program_labels",
    "apply_program_name" "combine_flipside_date_data",
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
]

API_KEY = st.secrets["flipside"]["api_key"]
sdk = ShroomDK(API_KEY)

agg_method_dict = {
    "mean": "Average usage within date range",
    "sum": "Total usage within date range",
    "max": "Max daily usage during date range",
}
metric_dict = {
    "TX_COUNT": "Transaction Count",
    "SIGNERS": "Number of signers",
}


def combine_flipside_date_data(data_dir, add_date=False, with_program=False):
    d = Path(data_dir)
    data_files = d.glob("*.csv")
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

    labels_url = "https://hyper.solana.fm/v2/address/"
    label_results = []
    for i, id_set in enumerate(split_ids):
        if i % 4 == 0:
            time.sleep(1)
        r = requests.get(f"{labels_url}{','.join(id_set)}")
        label_results.append(r.json())
    combined_labels = {}
    for x in label_results:
        combined_labels = {**combined_labels, **x}
    df = (
        pd.DataFrame.from_dict(combined_labels)
        .T.dropna(subset="FriendlyName")
        .reset_index(drop=True)
        .rename(columns={"Address": "ADDRESS"})
    )
    df.to_csv(f"data/{output_prefix}_solana_fm_labels.csv", index=False)


def load_program_label_df():
    fs_labs = pd.read_csv("data/program_flipside_labels.csv")
    solfm_labs = pd.read_csv("data/program_solana_fm_labels.csv")
    merged = fs_labs.merge(solfm_labs, on="ADDRESS", how="outer")
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
        return f"{label.title()}: {address_name.title()}"


def get_program_chart_data(
    df,
    metric,
    agg_method,
    date_range,
    exclude_solana,
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


# @st.experimental_memo(ttl=60 * 10)
def load_labeled_program_data(new_users_only=False):
    if new_users_only:
        return pd.read_csv("data/programs_new_users_labeled.csv.gz")
    else:
        return pd.read_csv("data/programs_labeled.csv.gz")


# @st.experimental_memo(ttl=60 * 10)
def load_weekly_program_data():
    df = pd.read_csv("data/weekly_program.csv")
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


# @st.experimental_memo(ttl=60 * 10)
def load_weekly_new_program_data():
    df = pd.read_csv("data/weekly_new_program.csv")
    df = df.sort_values(by="WEEK")
    df = df.reset_index(drop=True)
    df["Cumulative Programs"] = df["New Programs"].cumsum()
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


# @st.experimental_memo(ttl=60 * 10)
def load_weekly_user_data():
    df = pd.read_csv("data/weekly_users.csv")
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    return df


# @st.experimental_memo(ttl=60 * 10)
def load_weekly_new_user_data():
    df = pd.read_csv("data/weekly_new_users.csv")
    datecols = ["WEEK"]
    df[datecols] = df[datecols].apply(pd.to_datetime)
    df = df.sort_values(by="WEEK")
    df = df.rename(columns={"NEW_USERS": "New Users"})
    df["Cumulative Users"] = df["New Users"].cumsum()
    return df


# @st.experimental_memo(ttl=60 * 10)
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
                "NFTS_SOLD": "NFTs Sold",
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
            "NFTs Sold",
            "Sale Amount (SOL)",
        ]
    )
    marketplace_info = main_data.melt(
        id_vars=[
            "Date",
            "Buyers",
            "Sellers",
            "Transaction Count",
            "NFTs Sold",
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


# @st.experimental_memo(ttl=60 * 10)
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
