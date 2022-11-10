#!/usr/bin/env python3
import datetime
import json
import logging
from multiprocessing import Pool
from pathlib import Path
import shutil
from time import sleep

import numpy as np
import pandas as pd
import streamlit as st
from jinja2 import Environment, FileSystemLoader
from shroomdk import ShroomDK
from shroomdk.api import CreateQueryResp
from shroomdk.models import Query

API_KEY = st.secrets["flipside"]["api_key"]
sdk = ShroomDK(API_KEY)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


# #TODO: move to utils and CLI

all_dates = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(datetime.date(2020, 3, 16), (datetime.datetime.today() - pd.Timedelta("1d")))
]
all_dates_2022 = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(datetime.date(2022, 1, 1), (datetime.datetime.today() - pd.Timedelta("1d")))
]
past_7d = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        (datetime.datetime.today() - pd.Timedelta("8d")),
        (datetime.datetime.today() - pd.Timedelta("1d")),
    )
]
past_30d = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        (datetime.datetime.today() - pd.Timedelta("31d")),
        (datetime.datetime.today() - pd.Timedelta("1d")),
    )
]
past_90d = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        (datetime.datetime.today() - pd.Timedelta("91d")),
        (datetime.datetime.today() - pd.Timedelta("1d")),
    )
]

all_weeks = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        datetime.date(2020, 3, 16), (datetime.datetime.today() - pd.Timedelta("1d")), freq="7d"
    )
]


def create_query_by_date(date, query_basename):
    env = Environment(loader=FileSystemLoader("./sql"))
    template = env.get_template(f"{query_basename}.sql")
    query = template.render({"date": f"'{date}'"})
    return query


def create_query_by_date_and_program(date, query_basename, program):
    env = Environment(loader=FileSystemLoader("./sql"))
    template = env.get_template(f"{query_basename}.sql")
    query = template.render({"date": f"'{date}'", "program_id": f"'{program}'"})
    return query


def create_label_query(addresses):
    env = Environment(loader=FileSystemLoader("./sql"))
    template = env.get_template("sdk_labels_sol.sql")
    query = template.render({"addresses": addresses})
    return query


def get_queries_by_date(date, query_basename, update_cache=False):
    query = create_query_by_date(date, query_basename)
    output_dir = Path(f"data/{query_basename}")
    output_file = Path(output_dir, f"{query_basename}_{date.replace(' ', '_')}.csv")
    if update_cache or not output_file.exists():
        return query, output_file


def get_queries_by_date_and_programs(date, query_basename, df, update_cache=False):
    program_ids = get_program_ids(df)
    queries_to_do = []
    for program in program_ids:
        if len(chart_df[(chart_df.Date == date) & (chart_df.PROGRAM_ID == program)]) > 0:
            query = create_query_by_date_and_program(date, query_basename, program)
            output_dir = Path(f"data/{query_basename}")
            output_file = Path(output_dir, f"{query_basename}_{date.replace(' ', '_')}_{program}.csv")
            if update_cache or not output_file.exists():
                pre_ran = Path(
                    "data/sdk_signers_by_programID_new_users_sol--all_user-programIDs",
                    f"{query_basename}_{date.replace(' ', '_')}_{program}.csv",
                )
                if pre_ran.exists():
                    logging.info(f"Copying {pre_ran} to {output_file}")
                    shutil.copy(pre_ran, output_file)
                else:
                    queries_to_do.append((query, output_file))
    return queries_to_do


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


def create_query(query, output_file):
    query_file = Path(output_file.parent, "queries", f"{output_file.stem}.sql")
    logging.info(f"#@# Submitting query for {output_file} ...")
    query_file.parent.mkdir(exist_ok=True, parents=True)
    with open(query_file, "w") as f:
        f.write(query)
    q = Query(
        sql=query,
        ttl_minutes=120,
        cached=True,
        timeout_minutes=30,
        retry_interval_seconds=1,
        page_size=1000000,
        page_number=1,
    )
    sent_q = sdk.api.create_query(q)
    return sent_q


def submit_flipside_queries(query_info):
    sent_queries = []
    for i, x in enumerate(query_info):
        query, output_file = x
        resp = create_query(query, output_file)
        sent_queries.append((resp, output_file))
        resp_file = Path(output_file.parent, "responses", f"{output_file.stem}.json")
        resp_file.parent.mkdir(exist_ok=True, parents=True)
        with open(resp_file, "w") as f:
            json.dump(resp.dict(), f)
        # #TODO: sleep?
        sleep(0.5)
        if i % 50 == 0 and i != 0:
            sleep(60)
    with open("data/submitted_queries.json", "w") as f:
        d = {str(k): v.dict() for v, k in sent_queries}
        json.dump(
            d,
            f,
        )
    return sent_queries


def get_flipside_query_data(submitted_queries):
    running = []
    failed = []
    logging.info(f"Checking status for {len(submitted_queries)} queries...")
    for x in submitted_queries:
        query, output_file = x
        output_file = Path(output_file)
        result = sdk.api.get_query_result(query.data.token, 1, 100000)
        if result.data is not None and result.data.status == "running":
            running.append(x)
        elif result.data is not None and result.data.status == "finished":
            df = pd.DataFrame(result.data.results, columns=result.data.columnLabels)
            output_file.parent.mkdir(exist_ok=True, parents=True)
            df.to_csv(
                output_file,
                index=False,
            )
        else:  # #TODO figure out failures better
            if result.status_msg != "OK":
                failed.append(x)
            else:
                running.append(x)
    with open("data/failed_queries.json", "a") as f:
        d = {str(k): v.dict() for v, k in failed}
        json.dump(
            d,
            f,
        )
    if len(failed) > 0:
        logging.info(f"#@# {len(failed)} queries failed")
    if len(running) > 0:
        sleep(10)
        get_flipside_query_data(running)


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
        return


def get_submitted_queries_from_json(submitted_query_file):
    with open(submitted_query_file) as f:
        subs = json.load(f)
    submitted_queries = []
    for k, v in subs.items():
        submitted_queries.append((CreateQueryResp(**v), k))
    return submitted_queries


if __name__ == "__main__":
    # #TODO make cli...
    update_cache = False
    chart_df = pd.read_csv("data/programs_labeled.csv.gz")
    chart_df["Date"] = pd.to_datetime(chart_df.Date)
    chart_df = chart_df[chart_df.LABEL != "solana"]
    chart_df = chart_df[chart_df.Date >= (datetime.datetime.today() - pd.Timedelta("31d"))]

    chart_df_new_users = pd.read_csv("data/programs_new_users_labeled.csv.gz")
    chart_df_new_users["Date"] = pd.to_datetime(chart_df_new_users.Date)
    chart_df_new_users = chart_df_new_users[chart_df_new_users.LABEL != "solana"]
    chart_df_new_users = chart_df_new_users[
        chart_df_new_users.Date >= (datetime.datetime.today() - pd.Timedelta("31d"))
    ]

    query_info = []
    # #TODO: change dates/programs
    for q, dates in [
        ("sdk_programs_new_users_sol", all_dates_2022),
        ("sdk_programs_sol", all_dates_2022),
        ("sdk_new_users_sol", all_dates_2022),
        ("sdk_transactions_sol", all_dates_2022),
        ("sdk_weekly_new_program_count_sol", all_weeks),
        ("sdk_weekly_program_count_sol", all_weeks),
        ("sdk_weekly_new_users_sol", all_weeks),
        ("sdk_weekly_users_sol", all_weeks),
    ]:
        for date in dates:
            queries_to_do = get_queries_by_date(date, q)
            if queries_to_do is not None:
                query_info.append(queries_to_do)

    for q, dates, df in [
        ("sdk_signers_by_programID_new_users_sol", past_30d, chart_df_new_users),
        ("sdk_signers_by_programID_sol", past_30d, chart_df),
    ]:  # for program_ids
        for date in dates:
            queries_to_do = get_queries_by_date_and_programs(date, q, df)
            if queries_to_do != []:
                query_info.extend(queries_to_do)

    logging.info(f"Running {len(query_info)} queries...")
    with Pool() as p:
        p.map(query_flipside_data, query_info)

    # #TODO combine data, get program_ids
    # df = combine_flipside_date_data("data/sdk_programs_sol")
    # program_ids = df.PROGRAM_ID.unique()
    # labels = create_label_query(program_ids)
    # query_flipside_data([labels, Path("data/flipside_labels.csv")])
    # label_df = pd.read_csv("data/flipside_labels.csv")
    # df = df.merge(label_df, left_on="PROGRAM_ID", right_on="ADDRESS", how="left").drop(
    #     axis=1, columns=["ADDRESS", "BLOCKCHAIN"]
    # )
    # df.to_csv('data/labeled_programs', index=False)
    # #TODO new user only
