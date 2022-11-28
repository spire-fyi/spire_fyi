#!/usr/bin/env python3
import datetime
from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd

import spire_fyi.utils as utils

# #TODO: add to cli


if __name__ == "__main__":
    program_df = utils.combine_flipside_date_data("data/sdk_programs_sol", add_date=False)
    program_df.to_csv("data/programs.csv.gz", index=False, compression="gzip")
    utils.get_flipside_labels(program_df, "program", "PROGRAM_ID")
    utils.get_solana_fm_labels(program_df, "program", "PROGRAM_ID")

    labeled_program_df = utils.add_program_labels(program_df)
    labeled_program_df.to_csv("data/programs_labeled.csv.gz", index=False, compression="gzip")

    # New users only
    program_new_users_df = utils.combine_flipside_date_data("data/sdk_programs_new_users_sol", add_date=False)
    program_new_users_df.to_csv("data/programs_new_users.csv.gz", index=False, compression="gzip")
    utils.get_flipside_labels(program_new_users_df, "program_new_users", "PROGRAM_ID")
    utils.get_solana_fm_labels(program_new_users_df, "program_new_users", "PROGRAM_ID")

    labeled_program_new_users_df = utils.add_program_labels(program_new_users_df)
    labeled_program_new_users_df.to_csv(
        "data/programs_new_users_labeled.csv.gz", index=False, compression="gzip"
    )

    user_df = utils.combine_flipside_date_data("data/sdk_new_users_sol", add_date=False)
    datecols = ["CREATION_DATE", "LAST_USE"]
    user_df[datecols] = user_df[datecols].apply(pd.to_datetime)
    last30d_users = user_df[user_df.CREATION_DATE > (datetime.datetime.today() - pd.Timedelta("31d"))]

    user_df.to_csv("data/users.csv.gz", index=False, compression="gzip")
    last30d_users.to_csv("data/last30d_users.csv.gz", index=False, compression="gzip")

    user_df["Days since last use"] = (datetime.datetime.today() - pd.Timedelta("1d")) - user_df.LAST_USE

    grouped = (
        user_df.groupby(pd.Grouper(key="CREATION_DATE", axis=0, freq="7d")).ADDRESS.count().reset_index()
    )
    grouped.to_csv("data/weekly_users.csv", index=False)
    grouped = user_df.groupby(pd.Grouper(key="LAST_USE", axis=0, freq="7d")).ADDRESS.count().reset_index()
    grouped.to_csv("data/weekly_users_last_use.csv", index=False)

    user_df["Days since last use"] = (
        ((datetime.datetime.today() - pd.Timedelta("1d")) - user_df.LAST_USE).dt.total_seconds() / 3600 / 24
    )
    grouped = (
        user_df.groupby(pd.Grouper(key="CREATION_DATE", axis=0, freq="7d"))["Days since last use"]
        .mean()
        .reset_index()
    )
    grouped["Days since creation"] = (
        ((datetime.datetime.today() - pd.Timedelta("1d")) - grouped.CREATION_DATE).dt.total_seconds()
        / 3600
        / 24
    )
    grouped.to_csv("data/weekly_days_since_last_use.csv", index=False)

    user_df["Days Active"] = (user_df.LAST_USE - user_df.CREATION_DATE).dt.total_seconds() / 3600 / 24
    grouped = (
        user_df.groupby(pd.Grouper(key="CREATION_DATE", axis=0, freq="7d"))["Days Active"]
        .mean()
        .reset_index()
    )
    grouped.to_csv("data/weekly_days_active.csv", index=False)

    weekly_program_data = utils.combine_flipside_date_data(
        "data/sdk_weekly_program_count_sol", add_date=False
    )
    weekly_program_data.to_csv("data/weekly_program.csv", index=False)

    weekly_new_program_data = utils.combine_flipside_date_data(
        "data/sdk_weekly_new_program_count_sol", add_date=False
    )
    weekly_new_program_data.to_csv("data/weekly_new_program.csv", index=False)

    weekly_user_data = utils.combine_flipside_date_data("data/sdk_weekly_users_sol", add_date=False)
    weekly_user_data.to_csv("data/weekly_users.csv", index=False)
    weekly_new_user_data = utils.combine_flipside_date_data("data/sdk_weekly_new_users_sol", add_date=False)
    weekly_new_user_data.to_csv("data/weekly_new_users.csv", index=False)

    # Network stuff
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
    # #---

    # #TODO: need to divide the ~500k+ addresses into ~10 queries to add labels, if necessary
    # utils.get_flipside_labels(last30d_users, "user", "ADDRESS")
    # utils.get_solana_fm_labels(last30d_users, "user", "ADDRESS")

    # labeled_user_df = utils.add_labels_to_df(last30d_users)
    # labeled_user_df.to_csv("data/users_labeled.csv.gz", index=False, compression="gzip")
    # #---

    # Network tables
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
        df = df["Date"] = pd.to_datetime(df.Date)
        df = df[df.Date >= cutoff_date]
        df = df[df["Program ID"].isin(programs)]

        combos = list(combinations(programs, 2))

        labels = programs_labeled.groupby("PROGRAM_ID").Name.first().reset_index()
        df = df.merge(labels.rename(columns={"PROGRAM_ID": "Program ID"}), on="Program ID")

        prog_user_dict = {}
        for x in programs:
            prog_user_dict[x] = (
                df[df["Program ID"] == x].Name.iloc[0],
                df[df["Program ID"] == x].Address.unique(),
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

    labeled_program_df["Date"] = pd.to_datetime(labeled_program_df.Date)
    labeled_program_df["Name"] = labeled_program_df.apply(utils.apply_program_name, axis=1)

    labeled_program_new_users_df["Date"] = pd.to_datetime(labeled_program_new_users_df.Date)
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
        net_df, programs = get_net_and_programs(labeled_program_df, signers_by_programID, label, cutoff_date)
        net_dfs.append(net_df)
        all_programs.extend(list(programs))

        net_df_new_users, programs_new_users = get_net_and_programs(labeled_program_new_users_df, signers_by_programID_new_users, label, cutoff_date)
        net_dfs_new_users.append(net_df_new_users)
        all_programs_new_users.extend(list(programs_new_users))

    all_net_df = pd.concat(net_dfs)
    all_net_df.to_csv("data/all_net.csv", index=False)
    all_programs_df = get_labeled_program_df(labeled_program_df, all_programs)
    all_programs_df.to_csv("data/all_programs.csv", index=False)

    all_net_df_new_users = pd.concat(net_dfs_new_users)
    all_net_df_new_users.to_csv("data/all_net_new_users.csv", index=False)
    all_programs_new_users_df = get_labeled_program_df(labeled_program_new_users_df, all_programs_new_users)
    all_programs_new_users_df.to_csv("data/all_programs_new_users.csv", index=False)
        # programs_labeled = labeled_program_df.copy()[labeled_program_df.LABEL != "solana"]
        # programs_labeled = programs_labeled[programs_labeled.Date  >= cutoff_date]
        # programs = utils.get_program_ids(programs_labeled)

        # df = signers_by_programID.copy()
        # df = df["Date"] = pd.to_datetime(df.Date)
        # df = df[df.Date > cutoff_date]
        # df = df[df["Program ID"].isin(programs)]

        # combos = list(combinations(programs, 2))

        # labels = programs_labeled.groupby("PROGRAM_ID").Name.first().reset_index()
        # df = df.merge(labels.rename(columns={"PROGRAM_ID": "Program ID"}), on="Program ID")

        # prog_user_dict = {}
        # for x in programs:
        #     prog_user_dict[x] = (
        #         df[df["Program ID"] == x].Name.iloc[0],
        #         df[df["Program ID"] == x].Address.unique()
        #     )

        # df_list = []
        # for i, j in combos:
        #     name1, prog1_users = prog_user_dict[i]
        #     name2, prog2_users = prog_user_dict[j]
        #     if len(prog1_users) < 10 or len(prog2_users) < 10:
        #         continue
        #     else:
        #         all_users = np.union1d(prog1_users, prog2_users)
        #         overlap = np.intersect1d(prog1_users, prog2_users, assume_unique=True)

        #         n_users = len(all_users)
        #         n_overlap = len(overlap)

        #         df_dict = {}
        #         df_dict["Program1"] = i
        #         df_dict["Program2"] = j
        #         df_dict["Name1"] = name1
        #         df_dict["Name2"] = name2
        #         df_dict["weight"] = n_overlap / n_users
        #         df_dict['Timedelta'] = label

        #         df_list.append(df_dict)
        # net_df = pd.DataFrame(df_list)
        # net_dfs.append(net_df)

        # all_programs.extend(list(programs))

        # labeled_program_df_ = labeled_program_df.copy()[labeled_program_df.LABEL != "solana"]
        # labeled_program_df_ = labeled_program_df_[labeled_program_df_.Date >= cutoff_date]
        # programs = utils.get_program_ids(labeled_program_df_)
        # all_programs.extend(list(programs))

        # all_programs_df = pd.DataFrame({"ProgramID": pd.unique(all_programs)})
        # all_programs_labeled = labeled_program_df.groupby("PROGRAM_ID").Name.first().reset_index()
        # all_programs_df = all_programs_df.merge(
        #     all_programs_labeled[["PROGRAM_ID", "Name"]].rename(columns={"PROGRAM_ID": "ProgramID"}),
        #     on="ProgramID",
        # )

        # # new users
        # labeled_program_new_users_df_ = labeled_program_new_users_df.copy()[
        #     labeled_program_new_users_df.LABEL != "solana"
        # ]
        # labeled_program_new_users_df_ = labeled_program_new_users_df_[
        #     labeled_program_new_users_df_.Date >= cutoff_date
        # ]
        # programs_new_users = utils.get_program_ids(labeled_program_new_users_df_)
        # all_programs_new_users.extend(list(programs_new_users))

        # all_programs_new_users_df = pd.DataFrame({"ProgramID": pd.unique(all_programs_new_users)})
        # all_programs_new_users_labeled = (
        #     labeled_program_new_users_df.groupby("PROGRAM_ID").Name.first().reset_index()
        # )
        # all_programs_new_users_df = all_programs_new_users_df.merge(
        #     all_programs_new_users_labeled[["PROGRAM_ID", "Name"]].rename(columns={"PROGRAM_ID": "ProgramID"}),
        #     on="ProgramID",
        # )
