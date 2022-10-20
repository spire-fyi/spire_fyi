#!/usr/bin/env python3
import spire_fyi.utils as utils
import pandas as pd
import datetime

# #TODO: add to cli


if __name__ == "__main__":
    # program_df = utils.combine_flipside_date_data("data/sdk_programs_sol", add_date=False)
    # program_df.to_csv("data/programs.csv.gz", index=False, compression="gzip")
    # utils.get_flipside_labels(program_df, "program", "PROGRAM_ID")
    # utils.get_solana_fm_labels(program_df, "program", "PROGRAM_ID")

    # labeled_program_df = utils.add_program_labels(program_df)
    # labeled_program_df.to_csv("data/programs_labeled.csv.gz", index=False, compression="gzip")

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

    user_df['Days Active']=(user_df.LAST_USE - user_df.CREATION_DATE).dt.total_seconds() /3600/24
    grouped = user_df.groupby(pd.Grouper(key="CREATION_DATE", axis=0, freq="7d"))["Days Active"].mean().reset_index()
    grouped.to_csv("data/weekly_days_active.csv", index=False)

    # #TODO: need to divide the ~500k+ addresses into ~10 queries
    # utils.get_flipside_labels(last30d_users, "user", "ADDRESS")
    # utils.get_solana_fm_labels(last30d_users, "user", "ADDRESS")

    # labeled_user_df = utils.add_labels_to_df(last30d_users)
    # labeled_user_df.to_csv("data/users_labeled.csv.gz", index=False, compression="gzip")

    weekly_program_data = utils.combine_flipside_date_data(
        "data/sdk_weekly_program_count_sol", add_date=False
    )
    weekly_program_data.to_csv("data/weekly_program.csv", index=False)

    weekly_new_program_data = utils.combine_flipside_date_data(
        "data/sdk_weekly_new_program_count_sol", add_date=False
    )

    weekly_new_program_data.to_csv("data/weekly_new_program.csv", index=False)
