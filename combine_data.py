#!/usr/bin/env python3
import datetime
import gc
import json
import logging
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st

import spire_fyi.utils as utils

helius_key = st.secrets["helius"]["api_key"]


def get_labeled_program_df(df, programs):
    all_programs_df = pd.DataFrame({"ProgramID": pd.unique(programs)})
    all_programs_labeled = df.groupby("PROGRAM_ID").Name.first().reset_index()
    all_programs_df = all_programs_df.merge(
        all_programs_labeled[["PROGRAM_ID", "Name"]].rename(columns={"PROGRAM_ID": "ProgramID"}),
        on="ProgramID",
    )
    return all_programs_df


def get_net_and_programs(labeled_programs, signers, label, cutoff_date):
    programs_labeled = labeled_programs.copy()[labeled_programs.LABEL != "solana"]
    programs_labeled = programs_labeled[programs_labeled.Date >= cutoff_date]
    programs = utils.get_program_ids(programs_labeled)

    df = signers.copy()
    df["Date"] = pd.to_datetime(df.Date, utc=True)
    df = df[df.Date >= cutoff_date]
    df = df[df["Program ID"].isin(programs)]

    combos = list(combinations(programs, 2))

    labels = programs_labeled.groupby("PROGRAM_ID").Name.first().reset_index()
    df = df.merge(labels.rename(columns={"PROGRAM_ID": "Program ID"}), on="Program ID")

    prog_user_dict = {}
    for x in programs:
        try:
            prog_user_dict[x] = (
                df[df["Program ID"] == x].Name.iloc[0],
                df[df["Program ID"] == x].Address.unique(),
            )
        except IndexError:
            print(x)
            prog_user_dict[x] = (
                x,
                np.array([]),
            )

    df_list = []
    for i, j in combos:
        name1, prog1_users = prog_user_dict[i]
        name2, prog2_users = prog_user_dict[j]
        if len(prog1_users) < 10 or len(prog2_users) < 10:
            continue
        else:
            all_users = np.union1d(prog1_users, prog2_users)
            overlap = np.intersect1d(prog1_users, prog2_users, assume_unique=True)

            n_users = len(all_users)
            n_overlap = len(overlap)

            df_dict = {}
            df_dict["Program1"] = i
            df_dict["Program2"] = j
            df_dict["Name1"] = name1
            df_dict["Name2"] = name2
            df_dict["weight"] = n_overlap / n_users
            df_dict["Timedelta"] = label

            df_list.append(df_dict)
    net_df = pd.DataFrame(df_list)

    return net_df, programs


def get_top_creator_info(creators):
    data = {"creator_address": "", "creator_share": 0}
    for x in creators:
        if x["share"] > data["creator_share"]:
            data["creator_share"] = x["share"]
            data["creator_address"] = x["address"]
    return data


def get_important_metadata(enumerated_splits, filehandle):
    url = f"https://api.helius.xyz/v0/tokens/metadata?api-key={helius_key}"
    important_metadata = []
    mints_no_metadata = []
    for i, x in enumerated_splits:
        if i % 100 == 0:
            logging.info(f"Working on request {i}")
        mints = x.tolist()
        r = requests.post(url, json={"mintAccounts": mints})
        metadata = r.json()
        for y in metadata:
            mint = y["mint"]
            filehandle.write(f"{mint}\n")
            try:
                onchain = y["onChainData"]
                onchaindata = onchain["data"]
            except:
                mints_no_metadata.append(mint)
                continue

            try:
                name = onchaindata["name"]
            except:
                name = ""
            try:
                symbol = onchaindata["symbol"]
            except:
                symbol = ""
            try:
                seller_fee_basis_points = onchaindata["sellerFeeBasisPoints"]
            except:
                seller_fee_basis_points = 0
            try:
                uri = onchaindata["uri"]
            except:
                uri = ""
            try:
                update_authority = onchain["updateAuthority"]
            except:
                update_authority = ""
            try:
                creator_info = get_top_creator_info(onchaindata["creators"])
            except:
                creator_info = {"creator_address": "", "creator_share": 0}

            data = {
                "mint": mint,
                "name": name,
                "symbol": symbol,
                "seller_fee_basis_points": seller_fee_basis_points,
                "uri": uri,
                "update_authority": update_authority,
                **creator_info,
            }
            with open(f"data/nft_metadata/{mint}.json", "w") as f:
                json.dump(data, f)
            important_metadata.append(data)
    return pd.DataFrame(important_metadata), mints_no_metadata


def fix_carriage_return_error(df):
    """There is a `\r` character in some NFT metadata, which breaks parsing.
    Hack to fix this
    """
    # First collection fix:
    idx = df[df.BLOCK_TIMESTAMP.isna() & (df.TX_ID == "GBwAAou24vCFiBayvpqkurXiUYKUbBUJY7yGbRMqwNZX")].index
    idx2 = idx - 1
    idx = df[df.BLOCK_TIMESTAMP.isna() & (df.TX_ID == "GBwAAou24vCFiBayvpqkurXiUYKUbBUJY7yGbRMqwNZX")].index
    idx2 = idx - 1
    for i, j in zip(idx, idx2):
        df.iloc[j, df.columns.get_loc("update_authority")] = df.iloc[i, df.columns.get_loc("TX_ID")]
        df.iloc[j, df.columns.get_loc("creator_address")] = df.iloc[i, df.columns.get_loc("PURCHASER")]
        df.iloc[j, df.columns.get_loc("creator_share")] = df.iloc[i, df.columns.get_loc("SELLER")]
    df = df.drop(idx)
    df = df.reset_index(drop=True)

    # Second collection fix
    idx = df[df.BLOCK_TIMESTAMP.isna() & (df.TX_ID == "BAR")].index
    idx2 = idx - 1
    for i, j in zip(idx, idx2):
        df.iloc[j, df.columns.get_loc("symbol")] = df.iloc[i, df.columns.get_loc("TX_ID")]
        df.iloc[j, df.columns.get_loc("seller_fee_basis_points")] = df.iloc[
            i, df.columns.get_loc("PURCHASER")
        ]
        df.iloc[j, df.columns.get_loc("uri")] = df.iloc[i, df.columns.get_loc("SELLER")]
        df.iloc[j, df.columns.get_loc("update_authority")] = df.iloc[i, df.columns.get_loc("MINT")]
        df.iloc[j, df.columns.get_loc("creator_address")] = df.iloc[i, df.columns.get_loc("SALES_AMOUNT")]
        df.iloc[j, df.columns.get_loc("creator_share")] = df.iloc[i, df.columns.get_loc("name")]
    df = df.drop(idx)
    df = df.reset_index(drop=True)

    # fix types
    df = df.fillna(
        {
            "name": "",
            "symbol": "",
            "seller_fee_basis_points": 0,
            "uri": "",
            "update_authority": "",
            "creator_address": "",
            "creator_share": 0,
        }
    )
    df = df.astype(
        {
            "BLOCK_TIMESTAMP": "datetime64[ns]",
            "SALES_AMOUNT": float,
            "seller_fee_basis_points": float,
            "creator_share": float,
        }
    )

    return df


def get_collection_name(row):
    s = row["symbol"].strip()
    try:
        n = row["name"].strip()
    except AttributeError:
        print(row)
        raise
    if s != "":
        return s.strip()
    elif "#" in n:
        split = n.split("#")
        if len(split) != 2:
            return split[0].strip()
        elif n.startswith("#"):
            if split[0] == "" and split[1].strip().isnumeric():
                return row.creator_address.strip()
            else:
                rest = split[1].split()
                if rest[0].strip().isnumeric():
                    return " ".join(x for x in rest[1:] if x.isalnum()).strip()
                else:
                    return row.creator_address.strip()
        elif split[1].strip().isnumeric():
            return split[0].strip()
        elif split[0] == "":
            rest = rest = split[1].split()
            return " ".join(x for x in rest if x.isalnum()).strip()
    elif ":" in n:
        return n.split(":")[0].strip()
    elif "|" in n:
        return n.split("|")[0].strip()
    elif "-" in n:
        split = n.split("-")
        if split[0] == "TYR":
            return " ".join(x.strip() for x in split if x.isalpha()).strip()
        else:
            return n.split("-")[0].strip()
    elif not n[-1].isnumeric():
        return n.strip()

    else:
        return row.creator_address.strip()


# #TODO: add to cli
if __name__ == "__main__":
    do_main = True
    do_network = False
    do_nft = False
    combine_nft = False
    do_xnft = True
    do_fees = True
    do_madlad_metadata = True
    do_staking_report = True

    if do_main:
        dfs = []
        for x in [
            ("data/sdk_programs_sol", "data/programs.csv.gz"),
            ("data/sdk_programs_new_users_sol", "data/programs_new_users.csv.gz"),
            ("data/sdk_programs_all_signers_sol", "data/programs_all_signers.csv.gz"),
            ("data/sdk_programs_new_users_all_signers_sol", "data/programs_new_users_all_signers.csv.gz"),
        ]:
            data, output_file = x
            df = utils.combine_flipside_date_data(data, add_date=False, rename_columns={"DATE": "Date"})
            df["PROGRAM_ID"] = df["PROGRAM_ID"].apply(
                lambda x: "11111111111111111111111111111111" if x == "1.1111111111111112e+31" else x
            )
            df.to_csv(output_file, index=False, compression="gzip")
            dfs.append(df)
        program_df = pd.concat(dfs)
        utils.get_flipside_labels(program_df, "all_programs", "PROGRAM_ID")
        utils.get_solana_fm_labels(program_df, "all_programs", "PROGRAM_ID")

        for data, output_file in zip(
            dfs,
            [
                "data/programs_labeled.csv.gz",
                "data/programs_new_users_labeled.csv.gz",
                "data/programs_all_signers_labeled.csv.gz",
                "data/programs_new_users_all_signers_labeled.csv.gz",
            ],
        ):
            labeled_program_df = utils.add_program_labels(data, prefix="all_programs")
            labeled_program_df.to_csv(output_file, index=False, compression="gzip")

        # ----------
        # # #NOTE: this section looks at new users, and is not currently used. will be useful when doing network analysis
        # user_df = utils.combine_flipside_date_data("data/sdk_new_users_sol", add_date=False)
        # datecols = ["CREATION_DATE", "LAST_USE"]
        # user_df[datecols] = user_df[datecols].apply(pd.to_datetime, utc=True)
        # last30d_users = user_df[user_df.CREATION_DATE > (datetime.datetime.today() - pd.Timedelta("31d"))]
        # user_df.to_csv("data/users.csv.gz", index=False, compression="gzip")
        # last30d_users.to_csv("data/last30d_users.csv.gz", index=False, compression="gzip")

        # user_df["Days since last use"] = (datetime.datetime.today() - pd.Timedelta("1d")) - user_df.LAST_USE

        # grouped = (
        #     user_df.groupby(pd.Grouper(key="CREATION_DATE", axis=0, freq="7d")).ADDRESS.count().reset_index()
        # )
        # # This is currently taken from the "weekly users" queries
        # grouped.to_csv("data/grouped_weekly_users.csv", index=False)

        # # These CSVs may be useful, but no analysis use them yet:
        # grouped = user_df.groupby(pd.Grouper(key="LAST_USE", axis=0, freq="7d")).ADDRESS.count().reset_index()
        # grouped.to_csv("data/weekly_users_last_use.csv", index=False)

        # user_df["Days since last use"] = (
        #     ((datetime.datetime.today() - pd.Timedelta("1d")) - user_df.LAST_USE).dt.total_seconds()
        #     / 3600
        #     / 24
        # )
        # grouped = (
        #     user_df.groupby(pd.Grouper(key="CREATION_DATE", axis=0, freq="7d"))["Days since last use"]
        #     .mean()
        #     .reset_index()
        # )
        # grouped["Days since creation"] = (
        #     ((datetime.datetime.today() - pd.Timedelta("1d")) - grouped.CREATION_DATE).dt.total_seconds()
        #     / 3600
        #     / 24
        # )
        # grouped.to_csv("data/weekly_days_since_last_use.csv", index=False)

        # user_df["Days Active"] = (user_df.LAST_USE - user_df.CREATION_DATE).dt.total_seconds() / 3600 / 24
        # grouped = (
        #     user_df.groupby(pd.Grouper(key="CREATION_DATE", axis=0, freq="7d"))["Days Active"]
        #     .mean()
        #     .reset_index()
        # )
        # grouped.to_csv("data/weekly_days_active.csv", index=False)
        # ------

        weekly_program_data = utils.combine_flipside_date_data(
            "data/sdk_weekly_program_count_sol", add_date=False
        )
        weekly_program_data.to_csv("data/weekly_program.csv", index=False)

        weekly_new_program_data = utils.combine_flipside_date_data(
            "data/sdk_weekly_new_program_count_sol",
            add_date=False,
            rename_columns={"NEW PROGRAMS": "New Programs"},
        )
        weekly_new_program_data.to_csv("data/weekly_new_program.csv", index=False)

        weekly_user_data = utils.combine_flipside_date_data("data/sdk_weekly_users_sol", add_date=False)
        weekly_user_data.to_csv("data/weekly_users.csv", index=False)
        weekly_new_user_data = utils.combine_flipside_date_data(
            "data/sdk_weekly_new_users_sol", add_date=False
        )
        weekly_new_user_data.to_csv("data/weekly_new_users.csv", index=False)

        weekly_user_all_signers_data = utils.combine_flipside_date_data(
            "data/sdk_weekly_users_all_signers_sol", add_date=False
        )
        weekly_user_all_signers_data.to_csv("data/weekly_users_all_signers.csv", index=False)
        weekly_new_user_all_signers_data = utils.combine_flipside_date_data(
            "data/sdk_weekly_new_users_all_signers_sol", add_date=False
        )
        weekly_new_user_all_signers_data.to_csv("data/weekly_new_users_all_signers.csv", index=False)

        dex_new_users = utils.combine_flipside_date_data("data/sdk_dex_new_users", add_date=False)
        dex_new_users.to_csv("data/dex_new_users.csv", index=False)

        dex = utils.combine_flipside_date_data("data/sdk_dex", add_date=False)
        dex.to_csv("data/dex_info.csv", index=False)

        signers_fee_payers = utils.combine_flipside_date_data("data/sdk_openbook_users", add_date=False)
        signers_fee_payers.to_csv("data/dex_signers_fee_payers.csv", index=False)

        # #---
        # #TODO: need to divide the ~500k+ addresses into ~10 queries to add labels, if necessary
        # utils.get_flipside_labels(last30d_users, "user", "ADDRESS")
        # utils.get_solana_fm_labels(last30d_users, "user", "ADDRESS")

        # labeled_user_df = utils.add_labels_to_df(last30d_users)
        # labeled_user_df.to_csv("data/users_labeled.csv.gz", index=False, compression="gzip")
        # #---

    if do_network:
        signers_by_programID = utils.combine_flipside_date_data(
            "data/sdk_signers_by_programID_sol", add_date=True, with_program=True
        ).rename(columns={"DATE": "Date", "PROGRAM_ID": "Program ID", "SIGNERS": "Address"})
        signers_by_programID.to_csv("data/signers_by_programID.csv.gz", compression="gzip", index=False)

        signers_by_programID_new_users = utils.combine_flipside_date_data(
            "data/sdk_signers_by_programID_new_users_sol", add_date=True, with_program=True
        ).rename(columns={"DATE": "Date", "PROGRAM_ID": "Program ID", "SIGNERS": "Address"})
        signers_by_programID_new_users.to_csv(
            "data/signers_by_programID_new_users.csv.gz", compression="gzip", index=False
        )

        labeled_program_df["Date"] = pd.to_datetime(labeled_program_df.Date, utc=True)
        labeled_program_df["Name"] = labeled_program_df.apply(utils.apply_program_name, axis=1)

        labeled_program_new_users_df["Date"] = pd.to_datetime(labeled_program_new_users_df.Date, utc=True)
        labeled_program_new_users_df["Name"] = labeled_program_new_users_df.apply(
            utils.apply_program_name, axis=1
        )

        cutoff_dates = [
            ("7d", datetime.datetime.today() - pd.Timedelta("8d")),
            ("14d", datetime.datetime.today() - pd.Timedelta("15d")),
            ("30d", datetime.datetime.today() - pd.Timedelta("31d")),
            ("60d", datetime.datetime.today() - pd.Timedelta("61d")),
            ("90d", datetime.datetime.today() - pd.Timedelta("91d")),
        ]

        all_programs = []
        all_programs_new_users = []
        net_dfs = []
        net_dfs_new_users = []

        for label, cutoff_date in cutoff_dates:
            print(cutoff_date)
            print("#@# all programs")
            net_df, programs = get_net_and_programs(
                labeled_program_df, signers_by_programID, label, cutoff_date
            )
            net_dfs.append(net_df)
            all_programs.extend(list(programs))
            print("#@# new users only")
            net_df_new_users, programs_new_users = get_net_and_programs(
                labeled_program_new_users_df, signers_by_programID_new_users, label, cutoff_date
            )
            net_dfs_new_users.append(net_df_new_users)
            all_programs_new_users.extend(list(programs_new_users))
            print("---")

        all_net_df = pd.concat(net_dfs)
        all_net_df.to_csv("data/all_net.csv", index=False)
        all_programs_df = get_labeled_program_df(labeled_program_df, all_programs)
        all_programs_df.to_csv("data/all_programs.csv", index=False)

        all_net_df_new_users = pd.concat(net_dfs_new_users)
        all_net_df_new_users.to_csv("data/all_net_new_users.csv", index=False)
        all_programs_new_users_df = get_labeled_program_df(
            labeled_program_new_users_df, all_programs_new_users
        )
        all_programs_new_users_df.to_csv("data/all_programs_new_users.csv", index=False)

    if do_nft:
        if do_main:
            # Clear memory so this runs on my laptop
            del program_df
            del labeled_program_df
            del program_new_users_df
            del labeled_program_new_users_df
            del user_df
            del last30d_users
            del grouped
            del weekly_program_data
            del weekly_new_program_data
            del weekly_user_data
            del weekly_new_user_data
        if do_network:
            del signers_by_programID
            del signers_by_programID_new_users
            del all_net_df
            del all_programs_df
            del all_net_df_new_users
            del all_programs_new_users_df
        gc.collect()

        nft_mints_df = utils.combine_flipside_date_data("data/sdk_nft_mints", add_date=False)
        nft_mints_df["BLOCK_TIMESTAMP"] = pd.to_datetime(nft_mints_df["BLOCK_TIMESTAMP"], utc=True)
        # #TODO: eventually do all dates, for now just since right before royalties turned off
        nft_mints_df = nft_mints_df[nft_mints_df["BLOCK_TIMESTAMP"] >= "2022-10-07"]
        all_mints = sorted(nft_mints_df.MINT.astype(str).unique())

        checked_for_metadata_file = "data/checked_for_metadata.txt"
        with open("data/checked_for_metadata.txt", "r+") as f:
            completed_metadata = [x.strip() for x in f]
            mints_to_check = np.setdiff1d(all_mints, completed_metadata)

            n_splits = np.ceil(len(mints_to_check) / 100)
            if n_splits == 0:
                logging.info("#@# No new mints to  check")
            else:
                all_mint_splits = np.array_split(mints_to_check, n_splits)
                logging.info(
                    f"#@# Using Helius get metadata for {len(mints_to_check)} of {len(all_mints)} divided into {len(all_mint_splits)} requests..."
                )
                all_mints_metadata, mints_no_metadata = get_important_metadata(enumerate(all_mint_splits), f)
                # #TODO: remove, not necessary:
                # with open("data/mints_no_metadata.txt", "w") as f:
                #     f.writelines(f"{x}\n" for x in mints_no_metadata)
        if len(mints_to_check) != len(all_mints):
            json_data = []
            for x in Path("data/nft_metadata").glob("*.json"):
                with open(x) as f:
                    data = json.load(f)
                    json_data.append(data)
            all_mints_metadata = pd.DataFrame(json_data)
        all_mints_metadata.to_csv("data/nft_mints_metadata.csv.gz", compression="gzip", index=False)

        nft_mints_df = nft_mints_df.merge(
            all_mints_metadata.rename(columns={"mint": "MINT"}), on="MINT", how="left"
        )
        nft_mints_df.to_csv("data/nft_mints.csv.gz", compression="gzip", index=False)

        if not do_nft and combine_nft:
            nft_mints_df = pd.read_csv("data/nft_mints.csv.gz")
        nft_mints_df = fix_carriage_return_error(nft_mints_df)

        # #TODO: need to get rid of duplicates
        unique_collection_df = utils.combine_flipside_date_data(
            "data/sdk_nft_royalty_tx", add_date=False, nft_royalty=True
        )
        unique_collection_df["BLOCK_TIMESTAMP"] = pd.to_datetime(
            unique_collection_df["BLOCK_TIMESTAMP"], utc=True
        )

        nft_mints_df = nft_mints_df.merge(
            unique_collection_df, on=["BLOCK_TIMESTAMP", "TX_ID", "MINT", "SALES_AMOUNT"], how="left"
        )

        # Add in useful column
        nft_mints_df["royalty_percentage"] = nft_mints_df.seller_fee_basis_points / 10000
        nft_mints_df["total_royalty_amount"] = nft_mints_df.ROYALTY_AMOUNT / (
            nft_mints_df.creator_share / 100
        )

        nft_mints_df["expected_royalty"] = nft_mints_df.SALES_AMOUNT * nft_mints_df.royalty_percentage
        nft_mints_df["royalty_diff"] = nft_mints_df.total_royalty_amount - nft_mints_df.expected_royalty

        nft_mints_df["royalty_percent_paid"] = nft_mints_df.total_royalty_amount / nft_mints_df.SALES_AMOUNT

        nft_mints_df["paid_royalty"] = (nft_mints_df.ROYALTY_AMOUNT > 0) | (
            nft_mints_df.royalty_percentage == 0
        )
        nft_mints_df["paid_full_royalty"] = np.isclose(
            nft_mints_df.expected_royalty, nft_mints_df.total_royalty_amount, atol=0.001
        )
        nft_mints_df["paid_half_royalty"] = (
            np.isclose(nft_mints_df.expected_royalty / 2, nft_mints_df.total_royalty_amount, atol=0.001)
        ) & (nft_mints_df.royalty_percentage != 0)
        # TODO: add this in, remove from utils
        # df["paid_full_royalty"] = (df["paid_full_royalty"] | (df.total_royalty_amount > df.expected_royalty))
        # save full data
        nft_mints_df.to_csv("data/nft_sales_with_royalties.csv.gz", compression="gzip", index=False)

        # only datasets with metadata:
        metadata_df = nft_mints_df[~((nft_mints_df.name == "") & (nft_mints_df.symbol == ""))]
        collection_names = metadata_df.copy().apply(get_collection_name, axis=1)
        metadata_df["collection_name"] = collection_names
        metadata_df["unique_collection"] = metadata_df.collection_name + "-" + metadata_df.creator_address
        # save all metadata datasets
        metadata_df.to_csv("data/nft_sales_metadata_with_royalties.csv.gz", compression="gzip", index=False)

        # get unique_collection_mints
        unique_collection_mints = (
            metadata_df.groupby(["collection_name", "creator_address"])
            .agg(
                mints=("MINT", "unique"), total_sales=("SALES_AMOUNT", "sum"), total_mints=("MINT", "nunique")
            )
            .reset_index()
        )
        unique_collection_mints = unique_collection_mints[
            unique_collection_mints.total_sales >= unique_collection_mints.total_sales.quantile(0.5)
        ].sort_values(by="total_mints", ascending=False)
        unique_collection_mints["mints"] = unique_collection_mints["mints"].apply(lambda x: x.tolist())
        unique_collection_mints.to_csv("data/unique_collection_mints.csv", index=False)

        # get 99th percentile, ~top 75
        total_sales = (
            metadata_df[metadata_df.BLOCK_TIMESTAMP > (datetime.datetime.today() - pd.Timedelta("31d"))]
            .groupby(["unique_collection"])
            .SALES_AMOUNT.sum()
            .reset_index()
        )
        top_collections = total_sales[
            total_sales.SALES_AMOUNT > total_sales.SALES_AMOUNT.quantile(0.99)
        ].sort_values("SALES_AMOUNT", ascending=False)
        metadata_df = metadata_df[metadata_df.unique_collection.isin(top_collections.unique_collection)]

        # manual labeled collections from the above dataset
        labels = pd.read_csv("data/labeled_collections_by_uri.csv")  # #TODO: need to manually update this
        metadata_df = metadata_df.merge(labels, on="unique_collection", how="left")
        x = metadata_df[metadata_df.Name.isna()]
        assert len(x) == 0
        metadata_df.to_csv(
            "data/top_nft_sales_metadata_with_royalties.csv.gz", compression="gzip", index=False
        )

    if do_xnft:
        xnft_df = utils.combine_flipside_date_data("data/sdk_xnft")
        createInstall = xnft_df[xnft_df["INSTRUCTION_TYPE"] == "createInstall"].reset_index(drop=True)

        xnfts = createInstall.XNFT.unique()
        xnft_info = utils.get_xnft_info(xnfts)
        xnft_info_df = utils.create_xnft_info_df(xnft_info)
        xnft_info_df = xnft_info_df[
            xnft_info_df.columns.drop(["bump", "reserved0", "reserved1", "reserved2"])
        ]
        xnft_info_df = utils.add_uri_info(xnft_info_df)

        merged_xnft = createInstall.merge(xnft_info_df, on="XNFT")

        # TODO: get all xNFT users?
        # users = merged_xnft.FEE_PAYER.unique()
        # username_dict = {"FEE_PAYER":[], "Username":[]}
        # for i, x in enumerate(users):
        #     if i % 100 == 0:
        #         logging.info(f"Working on {i} of {len(users)}: {x}")
        #     username_dict['Username'].append(utils.get_backpack_username(x))
        #     username_dict["FEE_PAYER"].append(x)
        # logging.info(len(users), len(username_dict['FEE_PAYER']), len(username_dict["Username"]))

        # username_df = pd.DateFrame(username_dict)
        # merged_xnft = merged_xnft.merge(username_df, on='FEE_PAYER')

        merged_xnft.to_csv("data/xnft_create_install_all_info.csv", index=False)

        mad_lad_df = pd.read_csv("data/mad_lad.csv").rename(columns={"mint": "MINT"})
        mint_df = utils.combine_flipside_date_data("data/sdk_madlist")
        merged_mad_lad = mad_lad_df.merge(mint_df, on="MINT", how="left")
        merged_mad_lad.to_csv("data/mad_lad_all.csv", index=False)

        xnft_new_users = utils.combine_flipside_date_data("data/sdk_xnft_new_users")
        # TODO: any aggregation?
        xnft_new_users.to_csv("data/xnft_new_users.csv", index=False)

    if do_fees:
        dates = pd.date_range(end=datetime.date.today() - pd.Timedelta("1d"), periods=60, freq="1d")
        fee_df = utils.load_fees(dates)
        fee_df.to_csv("data/fees.csv", index=False)

    if do_madlad_metadata:
        data = []
        rarity_data = requests.get("https://api.howrare.is/v0.1/collections/madlads").json()
        collection = rarity_data["result"]["data"]["collection"]
        for x in rarity_data["result"]["data"]["items"]:
            d = {
                "Mint": x["mint"],
                "Collection": collection,
                "Name": x["name"],
                "Id": x["id"],
                "Image": x["image"],
                "Howrare Url": x["link"],
                "Rank": x["rank"],
            }
            for a in x["attributes"]:
                d[a["name"]] = a["value"]
                d[f"{a['name']} Rarity"] = a["rarity"]
            for k, v in x["all_ranks"].items():
                d[f"{k} Rank"] = v
            data.append(d)
        rarity_df = pd.DataFrame(data)
        rarity_df.to_csv("data/madlads_rarity.csv", index=False)

    if do_staking_report:
        stakers_df = utils.combine_flipside_date_data("data/sdk_top_stakers_by_date_sol", add_date=True)
        all_staker_addresses = stakers_df.rename(columns={"STAKER": "ADDRESS"})
        utils.get_solana_fm_labels(all_staker_addresses, "stakers", "ADDRESS")
        labeled_stakers = utils.add_program_labels(
            all_staker_addresses,
            left_on="ADDRESS",
            rename_solana_label=False,
            prefix="stakers",
            use_manual=False,
            drop=[],
            sfm_only=True,
        )
        labeled_stakers["Name"] = labeled_stakers.apply(
            utils.apply_program_name, axis=1, address_col="ADDRESS"
        )
        labeled_stakers["Rank"] = labeled_stakers.groupby("DATE")["TOTAL_STAKE"].rank(ascending=False)
        labeled_stakers["Diff"] = labeled_stakers.groupby(["ADDRESS"]).Rank.diff()
        labeled_stakers["DATE"] = pd.to_datetime(labeled_stakers["DATE"], utc=True)
        labeled_stakers = labeled_stakers.sort_values(
            by=["DATE", "TOTAL_STAKE"], ascending=False
        ).reset_index(drop=True)
        labeled_stakers.to_csv("data/top_stakers.csv.gz", index=False, compression="gzip")
        # -----

        lst_delta_df = utils.combine_flipside_date_data(
            "data/sdk_top_liquid_staking_token_holders_delta", raise_error=False
        )
        lst_delta_df["DATE"] = pd.to_datetime(lst_delta_df["DATE"], utc=True)
        lst_delta_df = lst_delta_df.rename(columns={"WALLET": "ADDRESS"})
        # Add in token labels
        for token, v in utils.liquid_staking_tokens.items():
            symbol, token_name = v
            lst_delta_df.loc[lst_delta_df["TOKEN"] == token, "TOKEN_NAME"] = token_name
            lst_delta_df.loc[lst_delta_df["TOKEN"] == token, "SYMBOL"] = symbol
        lst_delta_df = lst_delta_df.sort_values(by=["ADDRESS", "TOKEN", "DATE"]).reset_index(drop=True)
        lst_delta_df.to_csv("data/liquid_staking_token_holders_delta.csv", index=False)
        # #TODO: figure out issue for data after June 10 before using full token date range
        # max_date = lst_delta_df.DATE.max()
        max_date = labeled_stakers.DATE.max()
        lst_delta_df = lst_delta_df[lst_delta_df.DATE <= max_date].reset_index(drop=True)
        # ---
        results = []
        for x in lst_delta_df.ADDRESS.unique():
            df = lst_delta_df[lst_delta_df.ADDRESS == x]
            for y in df.TOKEN.unique():
                results.append(df[df.TOKEN == y].DATE.idxmax())
        lst_delta_df_copy = lst_delta_df.iloc[results].copy()
        lst_delta_df_copy["DATE"] = max_date
        lst_df = pd.concat([lst_delta_df, lst_delta_df_copy])

        # https://stackoverflow.com/a/74039090
        c = ["ADDRESS", "TOKEN", "TOKEN_NAME", "SYMBOL", "DATE"]
        m = lst_df[c].duplicated(keep="last")
        s = (
            lst_df[~m]
            .set_index("DATE")
            .groupby(["ADDRESS", "TOKEN", "TOKEN_NAME", "SYMBOL"])
            .resample("D")
            .ffill()
        )
        lst_df = (
            s.droplevel(["ADDRESS", "TOKEN", "TOKEN_NAME", "SYMBOL"])
            .reset_index()
            # .sort_values(by=["DATE", "ADDRESS", "TOKEN"])
            .sort_values(by=["ADDRESS", "TOKEN", "DATE"])
            .reset_index(drop=True)
        )
        #     lst_df = lst_df.join(
        #         labeled_stakers['ADDRESS', 'TOTAL_STAKE', 'ADDRESS_NAME', 'LABEL', 'LABEL_SUBTYPE',
        #    'LABEL_TYPE', 'DATE', 'FriendlyName', 'Abbreviation', 'Category',
        #    'VoteKey', 'Network', 'Tags', 'LogoURI', 'Flag', 'Name', 'Rank',
        #    'Diff']
        #     )
        lst_df["LST_Rank"] = lst_df.groupby(["DATE", "SYMBOL"])["AMOUNT"].rank(ascending=False)
        lst_df.to_csv("data/liquid_staking_token_holders.csv.gz", index=False, compression="gzip")

        # Combine the two datasets
        staking_combined_df = lst_df.merge(
            labeled_stakers,
            how="outer",
            on=["DATE", "ADDRESS"],
            #   right_on=['DATE', 'ADDRESS']
        )
        # get rid of na's in Name
        staking_combined_df["Name"] = staking_combined_df.apply(
            utils.apply_program_name, axis=1, address_col="ADDRESS"
        )
        staking_combined_df["Explorer URL"] = staking_combined_df.ADDRESS.apply(
            lambda x: f"https://solana.fm/address/{x}"
        )
        staking_combined_df.to_csv("data/staking_combined.csv.gz", index=False, compression="gzip")

        # #NOTE: probably dont need this, can just use the delta table
        # lst_delta_df = lst_delta_df.rename(columns={"Date": "DATE", "WALLET": "ADDRESS"})
        # staking_delta_combined = lst_delta_df.merge(
        #     labeled_stakers,
        #     how="inner",
        #     on=["DATE", "ADDRESS"],
        #     #   right_on=['Date', 'WALLET']
        # )
        # staking_delta_combined.to_csv("data/staking_delta_combined.csv.gz", index=False, compression="gzip")
