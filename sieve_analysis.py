import pandas as pd
import numpy as np

def process_coarse(coarse, total_weight) -> pd.DataFrame:
    """
    Computes cumulative and passing percentages for the coarse sieve fraction.

    Args:
        coarse: DataFrame with a 'Non-Cumulative Weight [g]' column and
                'Sieve Size [mm]' rows representing the coarse fraction (sieves >= No. 4).
        total_weight: Total dry weight of the entire sample [g], used as the
                      denominator when computing percent retained.

    Returns:
        The input DataFrame with three new columns added:
            - 'Cumulative Weight [g]': Running total of retained weight.
            - '% Retained': Cumulative weight as a percentage of the total sample weight.
            - '% Passing': Percentage of the sample finer than each sieve size.
    """
    # Accumulate retained weights from the largest sieve down
    coarse["Cumulative Weight [g]"] = coarse["Non-Cumulative Weight [g]"].cumsum()

    # Express cumulative retained weight as a percentage of the total sample weight
    coarse["% Retained"] = coarse["Cumulative Weight [g]"] / total_weight * 100

    # % Passing is the complement of % Retained
    coarse["% Passing"] = 100 - coarse["% Retained"]

    return coarse


def process_fine(fine, coarse, fines_weight) -> pd.DataFrame:
    """
    Computes cumulative and passing percentages for the fine sieve fraction,
    scaled to align with the coarse fraction at the No. 4 sieve (4.75 mm).

    The fine fraction is typically run on a sub-sample, so its weights are
    scaled by a factor derived from the percent passing the No. 4 sieve in
    the coarse analysis, ensuring continuity across the full gradation curve.

    Args:
        fine: DataFrame with a 'Non-Cumulative Weight [g]' column representing
              the fine fraction (sieves < No. 4), run on a sub-sample.
        coarse: Processed coarse DataFrame (output of process_coarse), used to
                retrieve the % passing value at the No. 4 sieve.
        fines_weight: Total weight of the fine sub-sample [g], used as the
                      basis for scaling fine weights to the full sample.

    Returns:
        The input DataFrame with three new columns added:
            - 'Cumulative Weight [g]': Running total of retained weight in the fine sub-sample.
            - '% Passing': Scaled percent passing, continuous with the coarse fraction.
            - '% Retained': Complement of % Passing.
    """
    # Retrieve the % passing at the No. 4 sieve (4.75 mm) from the coarse results;
    # this is the starting % passing value for the fine fraction
    percent_passing_no_4 = coarse[
        coarse["Sieve Size [mm]"] == 4.75
    ]["% Passing"].values[0]

    # Scaling factor to convert fine sub-sample weights to full-sample percentages
    factor = percent_passing_no_4 / fines_weight

    # Accumulate retained weights within the fine sub-sample
    fine["Cumulative Weight [g]"] = fine["Non-Cumulative Weight [g]"].cumsum()

    # Scale cumulative fine weights to the full sample using the factor,
    # subtracting from the No. 4 % passing to maintain a continuous gradation curve
    fine["% Passing"] = percent_passing_no_4 - fine["Cumulative Weight [g]"] * factor

    # % Retained is the complement of % Passing
    fine["% Retained"] = 100 - fine["% Passing"]

    return fine


def combine_data(coarse, fine) -> pd.DataFrame:
    """
    Concatenates the processed coarse and fine DataFrames into a single gradation table.

    Args:
        coarse: Processed coarse fraction DataFrame (output of process_coarse).
        fine: Processed fine fraction DataFrame (output of process_fine).

    Returns:
        A single DataFrame containing all sieve rows from both fractions,
        with the index reset to start from 0.
    """
    return pd.concat([coarse, fine], ignore_index=True)


def get_D_value(data, target_percent) -> float | None:
    """
    Interpolates the sieve diameter (Dx) at a given percent passing using
    log-linear interpolation on the gradation curve.

    Common usage: D10, D30, D60 for coefficient of uniformity and curvature.

    Args:
        data: DataFrame containing '% Passing' and 'Sieve Size [mm]' columns,
              typically the combined output of combine_data.
        target_percent: The percent passing value to interpolate at (e.g., 10, 30, 60).

    Returns:
        The interpolated sieve diameter [mm] at the target percent passing,
        or None if the target falls outside the range of the gradation data.
    """
    # Sort sieve rows by % passing in descending order to iterate from coarse to fine
    sorted_data = sorted(zip(data["% Passing"], data["Sieve Size [mm]"]), reverse=True)

    # Walk through consecutive sieve pairs to find the bracketing interval
    for i in range(len(sorted_data) - 1):
        p1, d1 = sorted_data[i]   # Upper bound: higher % passing, larger sieve
        p2, d2 = sorted_data[i + 1]  # Lower bound: lower % passing, smaller sieve

        # Check if the target percent falls within this interval
        if p1 >= target_percent >= p2:
            # Perform log-linear interpolation in log10 sieve size space,
            # since sieve sizes span orders of magnitude
            log_d1 = np.log10(d1)
            log_d2 = np.log10(d2)

            log_D = log_d1 + (target_percent - p1) * (log_d2 - log_d1) / (p2 - p1)

            # Convert back from log space to get the interpolated diameter
            return 10 ** log_D

    # Target percent is outside the range of the provided gradation data
    return None