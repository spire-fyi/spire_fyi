#!/usr/bin/env python3
import spire_fyi.utils as utils

# #TODO: add to cli


if __name__ == "__main__":
    df = utils.combine_flipside_date_data("data/sdk_programs_sol", add_date=False)
    df.to_csv("data/programs.csv.gz", index=False, compression="gzip")
    utils.get_flipside_labels(df)
    utils.get_solana_fm_labels(df)

    labeled_df = utils.add_labels_to_df(df)
    labeled_df.to_csv("data/programs_labeled.csv.gz", index=False, compression="gzip")

    weekly_program_data = utils.combine_flipside_date_data(
        "data/sdk_weekly_program_count_sol", add_date=False
    )
    weekly_program_data.to_csv("data/weekly_program.csv", index=False)

    weekly_new_program_data = utils.combine_flipside_date_data(
        "data/sdk_weekly_new_program_count_sol", add_date=False
    )

    weekly_new_program_data.to_csv("data/weekly_new_program.csv", index=False)
