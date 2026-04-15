import numpy as np


def calc_moisture_content(data):
    data['Mass of Water [g]']    = data['Mass of Tin + Wet Soil [g]'] - data['Mass of Tin + Dry Soil [g]']
    data['Mass of Dry Soil [g]'] = data['Mass of Tin + Dry Soil [g]'] - data['Mass of Tin [g]']
    data['% Moisture']           = data['Mass of Water [g]'] / data['Mass of Dry Soil [g]'] * 100
    return data

def process(ll_raw, pl_raw):
    ll_data = calc_moisture_content(ll_raw)
    pl_data = calc_moisture_content(pl_raw)

    pl = round(pl_data['% Moisture'].mean())

    coeffs = np.polyfit(np.log(ll_data['Number of Blows'].to_numpy(dtype=float)), ll_data['% Moisture'].to_numpy(dtype=float), 1)
    trend  = np.poly1d(coeffs)
    ll     = round(trend(np.log(25)))

    pi = ll - pl

    return ll_data, pl_data, ll, pl, pi
