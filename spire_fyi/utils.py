import logging
from pathlib import Path

import pandas as pd
import streamlit as st
from jinja2 import Environment, FileSystemLoader
from shroomdk import ShroomDK

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
__all__ = ["combine_flipside_date_data", "load_labeled_program_data", "get_label_df", "add_labels_to_df"]

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


def get_label_df(df):
    # #TODO combine with solana.fm
    program_ids = df.PROGRAM_ID.unique()
    labels = create_label_query(program_ids)
    query_flipside_data([labels, Path("data/flipside_labels.csv")])


def load_label_df():
    # #TODO combine with solana.fm
    return pd.read_csv("data/flipside_labels.csv")


def add_labels_to_df(df):
    label_df = load_label_df()
    df = df.merge(label_df, left_on="PROGRAM_ID", right_on="ADDRESS", how="left").drop(
        axis=1, columns=["ADDRESS", "BLOCKCHAIN"]
    )
    return df


@st.experimental_memo(ttl=60 * 10)
def load_labeled_program_data():
    return pd.read_csv("data/programs_labeled.csv.gz")
