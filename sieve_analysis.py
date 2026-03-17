import pandas as pd


def process_coarse(coarse, total_weight):
    coarse["Cumulative Weight [g]"] = coarse["Non-Cumulative Weight [g]"].cumsum()
    coarse["% Retained"] = coarse["Cumulative Weight [g]"] / total_weight * 100
    coarse["% Passing"] = 100 - coarse["% Retained"]
    return coarse


def process_fine(fine, coarse, fines_weight):
    percent_passing_no_4 = coarse[
        coarse["Sieve Size [mm]"] == 4.75
    ]["% Passing"].values[0]

    factor = percent_passing_no_4 / fines_weight

    fine["Cumulative Weight [g]"] = fine["Non-Cumulative Weight [g]"].cumsum()
    fine["% Passing"] = percent_passing_no_4 - fine["Cumulative Weight [g]"] * factor
    fine["% Retained"] = 100 - fine["% Passing"]

    return fine


def combine_data(coarse, fine):
    return pd.concat([coarse, fine], ignore_index=True)