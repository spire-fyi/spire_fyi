import logging
from pathlib import Path
import time

import pandas as pd
import requests
import streamlit as st
from jinja2 import Environment, FileSystemLoader
from shroomdk import ShroomDK

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
__all__ = [
    "add_labels_to_df",
    "apply_program_name" "combine_flipside_date_data",
    "get_flipside_labels",
    "load_labeled_program_data",
    "load_weekly_new_program_data",
    "load_weekly_program_data",
]

API_KEY = st.secrets["flipside"]["api_key"]
sdk = ShroomDK(API_KEY)


def combine_flipside_date_data(data_dir, add_date=False):
    d = Path(data_dir)
    data_files = d.glob("*.csv*")  # include both .csv and .csv.gz
    dfs = []
    for x in data_files:
        df = pd.read_csv(x)
        if add_date:
            date_str = x.name.split("_")[-1].split(".csv")[0]
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


def get_flipside_labels(df):
    # #TODO combine with solana.fm
    program_ids = df.PROGRAM_ID.unique()
    labels = create_label_query(program_ids)
    query_flipside_data([labels, Path("data/flipside_labels.csv")])


def get_solana_fm_labels(df):
    program_ids = df.PROGRAM_ID.unique()
    split_ids = [program_ids[i : i + 100] for i in range(0, len(program_ids), 100)]

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
        .T.reset_index()
        .drop(columns="Address")
        .rename(columns={"index": "ADDRESS"})
        .dropna(subset="FriendlyName")
        .reset_index(drop=True)
    )
    df.to_csv("data/solana_fm_labels.csv")


def load_label_df():
    fs_labs = pd.read_csv("data/flipside_labels.csv")
    solfm_labs = pd.read_csv("data/solana_fm_labels.csv")
    merged = fs_labs.merge(solfm_labs, on="ADDRESS", how="outer")
    return merged


def add_labels_to_df(df):
    label_df = load_label_df()
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


# @st.experimental_memo(ttl=60 * 10)
def load_labeled_program_data():
    return pd.read_csv("data/programs_labeled.csv.gz")


# @st.experimental_memo(ttl=60 * 10)
def load_weekly_program_data():
    return pd.read_csv("data/weekly_program.csv")


# @st.experimental_memo(ttl=60 * 10)
def load_weekly_new_program_data():
    df = pd.read_csv("data/weekly_new_program.csv")
    df = df.sort_values(by="WEEK")
    df["Cumulative Programs"] = df["New Programs"].cumsum()
    return df
