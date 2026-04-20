import pandas as pd
import numpy as np


def calc_moisture_content(data) -> pd.DataFrame:
    """
    Computes the moisture content for each row in the input DataFrame.

    Args:
        data: DataFrame containing the following columns:
              - 'Mass of Tin + Wet Soil [g]': Combined mass of tin and wet soil sample.
              - 'Mass of Tin + Dry Soil [g]': Combined mass of tin and oven-dried soil.
              - 'Mass of Tin [g]': Mass of the empty tin.

    Returns:
        The input DataFrame with three new columns added:
            - 'Mass of Water [g]': Mass of water lost during drying.
            - 'Mass of Dry Soil [g]': Mass of the dry soil solids only.
            - '% Moisture': Moisture content as a percentage of dry soil mass.
    """
    # Mass of water is the weight lost during oven drying
    data['Mass of Water [g]']    = data['Mass of Tin + Wet Soil [g]'] - data['Mass of Tin + Dry Soil [g]']

    # Mass of dry soil is the oven-dried reading minus the empty tin weight
    data['Mass of Dry Soil [g]'] = data['Mass of Tin + Dry Soil [g]'] - data['Mass of Tin [g]']

    # Moisture content: mass of water as a percentage of dry soil mass
    data['% Moisture']           = data['Mass of Water [g]'] / data['Mass of Dry Soil [g]'] * 100

    return data


def process(ll_raw, pl_raw) -> tuple [pd.DataFrame, pd.DataFrame, float, float, float]:
    """
    Computes the Atterberg limits — Liquid Limit (LL), Plastic Limit (PL),
    and Plasticity Index (PI) — from raw Casagrande cup and thread-rolling data.

    The Liquid Limit is determined by fitting a semi-log flow curve to the
    blow count vs. moisture content data and reading off the moisture at 25 blows,
    per ASTM D4318.

    Args:
        ll_raw: DataFrame of Liquid Limit test readings with columns:
                'Number of Blows', 'Mass of Tin + Wet Soil [g]',
                'Mass of Tin + Dry Soil [g]', 'Mass of Tin [g]'.
        pl_raw: DataFrame of Plastic Limit test readings with columns:
                'Mass of Tin + Wet Soil [g]', 'Mass of Tin + Dry Soil [g]',
                'Mass of Tin [g]'.

    Returns:
        A tuple of (ll_data, pl_data, ll, pl, pi) where:
            - ll_data: ll_raw with moisture content columns added.
            - pl_data: pl_raw with moisture content columns added.
            - ll: Liquid Limit [%], moisture content at 25 blows (rounded).
            - pl: Plastic Limit [%], mean moisture content of thread-rolling trials (rounded).
            - pi: Plasticity Index [-], calculated as LL − PL.
    """
    # Compute moisture content for both the liquid limit and plastic limit specimens
    ll_data = calc_moisture_content(ll_raw)
    pl_data = calc_moisture_content(pl_raw)

    # Plastic Limit is the average moisture content across all thread-rolling trials
    pl = round(pl_data['% Moisture'].mean())

    # Fit a linear trend to the semi-log flow curve (moisture vs. log blow count);
    # the Casagrande method assumes a straight-line relationship on a log scale
    coeffs = np.polyfit(
        np.log(ll_data['Number of Blows'].to_numpy(dtype=float)),  # log-transformed blow counts
        ll_data['% Moisture'].to_numpy(dtype=float),               # corresponding moisture contents
        1                                                           # degree 1 = linear fit
    )
    trend = np.poly1d(coeffs)

    # Evaluate the fitted trend at log(25) to get the moisture content at 25 blows,
    # which is the defined Liquid Limit per ASTM D4318
    ll = round(trend(np.log(25)))

    # Plasticity Index is the range of moisture over which the soil behaves plastically
    pi = ll - pl

    return ll_data, pl_data, ll, pl, pi