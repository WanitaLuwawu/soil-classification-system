import pandas as pd
import numpy as np

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

def get_D_value(data, target_percent):

    # Sort by % passing (descending)
    sorted_data = sorted(zip(data["% Passing"], data["Sieve Size [mm]"]), reverse=True)

    for i in range(len(sorted_data) - 1):
        p1, d1 = sorted_data[i]
        p2, d2 = sorted_data[i + 1]

        if p1 >= target_percent >= p2:

            # log interpolation
            log_d1 = np.log10(d1)
            log_d2 = np.log10(d2)

            log_D = log_d1 + (target_percent - p1) * (log_d2 - log_d1) / (p2 - p1)

            return 10 ** log_D

    return None