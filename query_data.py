#!/usr/bin/env python3

import ast
import datetime
import hashlib
import json
import logging
import shutil
from multiprocessing import Pool
from pathlib import Path
from time import sleep

import numpy as np
import pandas as pd
import streamlit as st
from flipside import Flipside

# from flipside.errors.api_error import ApiError
from jinja2 import Environment, FileSystemLoader

import spire_fyi.utils as utils

API_KEY = st.secrets["flipside"]["api_key"]
sdk = Flipside(API_KEY)

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
past_14d = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        (datetime.datetime.today() - pd.Timedelta("15d")),
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
past_60d = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        (datetime.datetime.today() - pd.Timedelta("61d")),
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
past_180d = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        (datetime.datetime.today() - pd.Timedelta("181d")),
        (datetime.datetime.today() - pd.Timedelta("1d")),
    )
]
since_marinade_launch = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        datetime.datetime(2021, 7, 31, 0, 0),  # mSOL launched 2021-08-01
        (datetime.datetime.today() - pd.Timedelta("1d")),
    )
]
past_90d_hours = [
    # f"{x:%Y-%m-%d %H:%M:%S.%f}"
    f"{x:%F %T.%f}"[:-3]
    for x in pd.date_range(
        (datetime.datetime.today() - pd.Timedelta("91d")),
        (datetime.datetime.today() - pd.Timedelta("1d")),
        freq="1H",
        normalize=True,
    )
]

all_weeks = [
    f"{x:%Y-%m-%d}"
    for x in pd.date_range(
        datetime.date(2020, 3, 16), (datetime.datetime.today() - pd.Timedelta("7d")), freq="7d"
    )
]


def create_query_by_date(date, query_basename, date2=None):
    env = Environment(loader=FileSystemLoader("./sql"))
    template = env.get_template(f"{query_basename}.sql")
    if date2 is None:
        query = template.render({"date": f"'{date}'"})
    else:
        query = template.render({"date": f"'{date}'", "date2": f"'{date2}'"})
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


def create_query_by_creator_address_and_mints(query_basename, creator_address, mints):
    env = Environment(loader=FileSystemLoader("./sql"))
    template = env.get_template(f"{query_basename}.sql")
    query = template.render({"mints": mints, "creator_address": f"'{creator_address}'"})
    return query


def create_query_by_date_and_wallets(date, wallets, query_basename):
    env = Environment(loader=FileSystemLoader("./sql"))
    template = env.get_template(f"{query_basename}.sql")
    query = template.render({"date": f"'{date}'", "wallets": wallets})
    return query


def get_queries_by_date(date, query_basename, update_cache=False, output_file=None, date2=None):
    query = create_query_by_date(date, query_basename, date2)
    output_dir = Path(f"data/{query_basename}")
    if output_file is None:
        output_file = Path(output_dir, f"{query_basename}_{date.replace(' ', '_')}.csv")
    else:
        output_file = Path(output_dir, output_file)
    if update_cache or not output_file.exists():
        return query, output_file


def get_queries_by_date_and_wallets(
    date, query_basename, wallets, n_wallets, wallet_hash, update_cache=False
):
    query = create_query_by_date_and_wallets(date, wallets, query_basename)
    output_dir = Path(f"data/{query_basename}")
    output_file = Path(
        output_dir, f"{query_basename}_{n_wallets}wallets_sha1-{wallet_hash}_{date.replace(' ', '_')}.csv"
    )
    if update_cache or not output_file.exists():
        return query, output_file


def get_queries_by_date_and_dex_program(date, query_basename, program, update_cache=False):
    query = create_query_by_date_and_program(date, query_basename, program)
    output_dir = Path(f"data/{query_basename}")
    output_file = Path(output_dir, f"{query_basename}_{date.replace(' ', '_')}_{program}.csv")
    if update_cache or not output_file.exists():
        return query, output_file


def get_queries_by_mint_list(mintlist, query_basename, update_cache=False):
    query = create_query_by_creator_address_and_mints(query_basename, "", mintlist)
    output_dir = Path(f"data/{query_basename}")
    output_file = Path(output_dir, f"{query_basename}_2022-12-01.csv")
    if update_cache or not output_file.exists():
        return query, output_file


def get_nft_transfer_queries(unique_collection_mints, query_basename, update_cache=False):
    queries_to_do = []
    for _, x in unique_collection_mints.iterrows():
        creator_address = x.creator_address
        mints = x.mints
        collection_name = x.collection_name
        total_mints = x.total_mints
        if total_mints > 16000:
            output_dir = Path(f"data/{query_basename}")

            mints_p1 = mints[:15000]
            mints_p2 = mints[15000:]
            mints_p2_len = len(mints_p2)

            query_p1 = create_query_by_creator_address_and_mints(query_basename, creator_address, mints_p1)
            output_file_p1 = Path(
                output_dir,
                f"{query_basename}_{collection_name}-{creator_address}--{total_mints}mints_p1_first15000.csv",
            )
            if update_cache or not output_file_p1.exists():
                queries_to_do.append((query_p1, output_file_p1))

            query_p2 = create_query_by_creator_address_and_mints(query_basename, creator_address, mints_p2)
            output_file_p2 = Path(
                output_dir,
                f"{query_basename}_{collection_name}-{creator_address}--{total_mints}mints_p2_last{mints_p2_len}.csv",
            )
            if update_cache or not output_file_p2.exists():
                queries_to_do.append((query_p2, output_file_p2))
        else:
            query = create_query_by_creator_address_and_mints(query_basename, creator_address, mints)
            output_dir = Path(f"data/{query_basename}")
            output_file = Path(
                output_dir, f"{query_basename}_{collection_name}-{creator_address}--{total_mints}mints.csv"
            )
            if update_cache or not output_file.exists():
                queries_to_do.append((query, output_file))
    return queries_to_do


def get_queries_by_date_and_programs(date, query_basename, df, update_cache=False) -> list:
    program_ids = utils.get_program_ids(df)
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


def query_flipside_data(enumerated_query_info, save=True, page_size=1000000, page_number=1):
    i, query_info = enumerated_query_info
    query, output_file = query_info
    query_file = Path(output_file.parent, "queries", f"{output_file.stem}.sql")
    logging.info(f"#@# Querying data for {output_file} ...")
    query_file.parent.mkdir(exist_ok=True, parents=True)
    with open(query_file, "w") as f:
        f.write(query)
    # if i % 1 == 0:
    #     sleep(5)
    if i % 5 == 0:
        sleep(3)
    if i % 10 == 0:
        sleep(10)
    if i % 100 == 0:
        sleep(15)
    try:
        query_result_set = sdk.query(
            query,
            ttl_minutes=120,
            timeout_minutes=30,
            retry_interval_seconds=1,
            page_size=page_size,
            page_number=page_number,
            cached=False,
        )
        if save:
            df = pd.DataFrame(
                pd.DataFrame(query_result_set.rows, columns=query_result_set.columns)
            )  # NOTE: flipside SDK v2.0 returns lowercase values, need to check these
            output_file.parent.mkdir(exist_ok=True, parents=True)
            df.to_csv(
                output_file,
                index=False,
            )
        logging.info(f"#@# Saved {output_file}")
        return output_file
    # # #TODO deal with large page size
    # except ApiError as e:
    #     msg = e.args[0]
    #     if "RequestedPageSizeTooLarge" in msg:
    #         #HACK : attempt to parse error message
    #         max_rows = int(msg.split('We suggest reducing your page size to below ')[1].split(' ')[0])
    #     return
    except Exception as e:
        logging.info(f"[ERROR] ({query_file}) {e}")
        return


if __name__ == "__main__":
    # #TODO make cli...
    update_cache = False
    lst_force_update = False
    do_main = True
    do_new_users = False
    do_network = False
    do_nft_mints = False
    do_nft_metadata = False
    do_xnft = True
    do_lst = False
    # main routines
    do_pull_flipside_data = True
    do_pool = True

    query_info = []
    if do_main:
        # #TODO: change dates/programs
        main_queries = [
            ("sdk_programs_sol", all_dates_2022),
            ("sdk_programs_all_signers_sol", past_90d),
            ("sdk_transactions_sol", all_dates_2022),
            ("sdk_weekly_new_program_count_sol", all_weeks),
            ("sdk_weekly_program_count_sol", all_weeks),
            ("sdk_weekly_new_users_sol", all_weeks),
            ("sdk_weekly_users_sol", all_weeks),
            ("sdk_weekly_new_users_all_signers_sol", all_weeks),
            ("sdk_weekly_users_all_signers_sol", all_weeks),
            ("sdk_dex", past_180d),
            ("sdk_openbook_users", past_180d),
            ("sdk_top_stakers_by_date_sol", past_180d),
        ]
        if do_new_users:
            main_queries.extend(
                [
                    ("sdk_programs_new_users_sol", all_dates_2022),
                    ("sdk_programs_new_users_all_signers_sol", past_90d),
                    ("sdk_dex_new_users", past_180d),
                    # ("sdk_new_users_sol", all_dates_2022), #NOTE: this is not currently used
                ]
            )
        if do_nft_mints:
            main_queries.append(("sdk_nft_mints", past_90d_hours))
        for q, dates in main_queries:
            for date in dates:
                if q == "sdk_dex_new_users":  # HACK
                    dex_program_ids = [x for v in utils.dex_programs.values() for x in v]  # flatten dict
                    for p in dex_program_ids:
                        queries_to_do = get_queries_by_date_and_dex_program(date, q, p)
                        if queries_to_do is not None:
                            query_info.append(queries_to_do)
                else:
                    queries_to_do = get_queries_by_date(date, q)
                    if queries_to_do is not None:
                        query_info.append(queries_to_do)

        if do_network:
            for dates, max_date_string in [  # HACK
                (past_7d, "8d"),
                (past_14d, "15d"),
                (past_30d, "31d"),
                (past_60d, "61d"),
                (past_90d, "91d"),
            ]:
                chart_df = pd.read_csv("data/programs_labeled.csv.gz")
                chart_df["Date"] = pd.to_datetime(chart_df.Date, utc=True)
                chart_df = chart_df[chart_df.LABEL != "solana"]
                chart_df = chart_df[
                    chart_df.Date >= (datetime.datetime.today() - pd.Timedelta(max_date_string))
                ]

                chart_df_new_users = pd.read_csv("data/programs_new_users_labeled.csv.gz")
                chart_df_new_users["Date"] = pd.to_datetime(chart_df_new_users.Date, utc=True)
                chart_df_new_users = chart_df_new_users[chart_df_new_users.LABEL != "solana"]
                chart_df_new_users = chart_df_new_users[
                    chart_df_new_users.Date >= (datetime.datetime.today() - pd.Timedelta(max_date_string))
                ]

                for q, df in [
                    ("sdk_signers_by_programID_new_users_sol", chart_df_new_users),
                    ("sdk_signers_by_programID_sol", chart_df),
                ]:  # for program_ids
                    for date in dates:
                        queries_to_do = get_queries_by_date_and_programs(date, q, df)
                        if queries_to_do != []:
                            query_info.extend(queries_to_do)

    if do_nft_metadata:
        # NFT processing
        nft_metadata_file = "data/unique_collection_mints.csv"
        unique_collection_mints = pd.read_csv(nft_metadata_file)
        unique_collection_mints["mints"] = unique_collection_mints["mints"].apply(
            lambda x: ast.literal_eval(x)
        )
        queries_to_do = get_nft_transfer_queries(unique_collection_mints, "sdk_nft_royalty_tx")
        if queries_to_do != []:
            query_info.extend(queries_to_do)

    if do_xnft:
        # Madlads
        mintlist = utils.get_mintlist(["FCk24cq1pYhQo5MQYKHf5N9VnY8tdrToF7u6gvvsnGrn"])
        mad_lad_df = utils.get_mad_lad_df(mintlist)
        mad_lad_df.to_csv("data/mad_lad.csv", index=False)
        mintlist = list(mad_lad_df.mint)
        query_info.extend(
            [
                get_queries_by_date("2022-12-01", "sdk_xnft", date2="2023-04-15"),
                get_queries_by_date("2022-12-01", "sdk_xnft_new_users", date2="2023-04-15"),
                get_queries_by_date(
                    "2023-04-15",
                    "sdk_xnft",
                    update_cache=True,
                    output_file="sdk_xnft_current.csv",
                    date2=past_7d[-1],
                ),
                get_queries_by_date(
                    "2023-04-15",
                    "sdk_xnft_new_users",
                    update_cache=True,
                    output_file="sdk_xnft_new_users_current.csv",
                    date2=past_7d[-1],
                ),
                get_queries_by_mint_list(mintlist, "sdk_madlist", update_cache=True),
            ]
        )

    if do_lst:
        """#TODO:
        - maybe move to combine_data, since it relies on top_stakers?
        - have an init and update step?
        - get first transaction date for each new wallet, so can run smaller numbers of queries for new wallets?
        - query all dates, for `top_stakers`, for each date since mSOL launch
        - save files for each wallet/max_date combo, so if new wallets are added to top_stakers dont need to re-run
        - forward fill dates to create final csv
        """
        if lst_force_update:
            top_stakers = pd.read_csv("data/top_stakers.csv.gz")
            top_staker_addresses = sorted(top_stakers.ADDRESS.unique().tolist())
        else:  # HACK until better way to update data, sticking with original top stakers as of 5/30
            with open("data/top_stakers.json") as f:
                d = json.load(f)
                top_staker_addresses = d["e69df08b7135b93f6f064d13d9a53b0db7390ec1"]["wallets"]
        n_wallets = len(top_staker_addresses)
        wallet_hash = hashlib.sha1("".join(top_staker_addresses).encode("utf-8")).hexdigest()
        date_range = since_marinade_launch
        last_date = date_range[-1]
        for q, dates in [("sdk_top_liquid_staking_token_holders_delta", date_range)]:
            for date in dates:
                queries_to_do = get_queries_by_date_and_wallets(
                    date, q, top_staker_addresses, n_wallets, wallet_hash
                )
                if queries_to_do is not None:
                    query_info.append(queries_to_do)
        with open("data/top_stakers.json") as f:
            top_stakers_log = json.load(f)
        with open("data/top_stakers.json", "w") as f:
            top_stakers_log[wallet_hash] = {
                "n_wallets": n_wallets,
                "last_date": date_range,
                "wallets": top_staker_addresses,
            }
            json.dump(top_stakers_log, f, indent=2)

    if do_pool:
        logging.info(f"Running {len(query_info)} queries...")
        with Pool() as p:
            p.map(query_flipside_data, list(enumerate(query_info)))

    if do_pull_flipside_data:
        top_staker_interactions = utils.load_flipside_api_data(
            f"{utils.api_base}/2cc62d89-4f67-4197-82cf-8daf9b69ff45/data/latest",
            ["DATE"],
        )
        top_staker_interactions.sort_values(by="Date", ascending=False).to_csv(
            "data/top_staker_interactions.csv", index=False
        )

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
