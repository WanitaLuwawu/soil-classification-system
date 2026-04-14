import pandas as pd

# Lookup Tables

HYDROMETER_151H = pd.DataFrame({
    'Actual Hydrometer Reading': [
        1.000, 1.001, 1.002, 1.003, 1.004, 1.005, 1.006, 1.007, 1.008, 1.009,
        1.010, 1.011, 1.012, 1.013, 1.014, 1.015, 1.016, 1.017, 1.018, 1.019,
        1.020, 1.021, 1.022, 1.023, 1.024, 1.025, 1.026, 1.027, 1.028, 1.029,
        1.030, 1.031, 1.032, 1.033, 1.034, 1.035, 1.036, 1.037, 1.038, 1.039
    ],
    'Effective Depth L [cm]': [
        16.3, 16.0, 15.8, 15.5, 15.2, 15.0, 14.7, 14.4, 14.2, 13.9,
        13.7, 13.4, 13.1, 12.9, 12.6, 12.3, 12.1, 11.8, 11.5, 11.3,
        11.0, 10.7, 10.5, 10.2, 10.0,  9.7,  9.4,  9.2,  8.9,  8.6,
         8.4,  8.1,  7.8,  7.6,  7.3,  7.0,  6.8,  6.5,  6.2,  5.9
    ]
}).set_index('Actual Hydrometer Reading')

HYDROMETER_152H = pd.DataFrame({
    'Actual Hydrometer Reading': list(range(0, 61)),
    'Effective Depth L [cm]': [
        16.3, 16.1, 16.0, 15.8, 15.6, 15.5, 15.3, 15.2, 15.0, 14.8,
        14.7, 14.5, 14.3, 14.2, 14.0, 13.8, 13.7, 13.5, 13.3, 13.2,
        13.0, 12.9, 12.7, 12.5, 12.4, 12.2, 12.0, 11.9, 11.7, 11.5,
        11.4, 11.2, 11.1, 10.9, 10.7, 10.6, 10.4, 10.2, 10.1,  9.9,
         9.7,  9.6,  9.4,  9.2,  9.1,  8.9,  8.8,  8.6,  8.4,  8.3,
         8.1,  7.9,  7.8,  7.6,  7.4,  7.3,  7.1,  7.0,  6.8,  6.6,
         6.5
    ]
}).set_index('Actual Hydrometer Reading')

K_TABLE = pd.DataFrame(
    {
        2.45: [0.01510, 0.01511, 0.01492, 0.01474, 0.01456, 0.01438, 0.01421, 0.01404, 0.01388, 0.01372, 0.01357, 0.01342, 0.01327, 0.01312, 0.01298],
        2.50: [0.01505, 0.01486, 0.01467, 0.01449, 0.01431, 0.01414, 0.01397, 0.01381, 0.01365, 0.01349, 0.01334, 0.01319, 0.01304, 0.01290, 0.01276],
        2.55: [0.01481, 0.01462, 0.01443, 0.01425, 0.01408, 0.01391, 0.01374, 0.01358, 0.01342, 0.01327, 0.01312, 0.01297, 0.01283, 0.01269, 0.01256],
        2.60: [0.01457, 0.01439, 0.01421, 0.01403, 0.01386, 0.01369, 0.01353, 0.01337, 0.01321, 0.01306, 0.01291, 0.01277, 0.01264, 0.01269, 0.01236],
        2.65: [0.01435, 0.01417, 0.01399, 0.01382, 0.01365, 0.01348, 0.01332, 0.01317, 0.01301, 0.01286, 0.01272, 0.01258, 0.01244, 0.01230, 0.01217],
        2.70: [0.01414, 0.01396, 0.01378, 0.01361, 0.01344, 0.01328, 0.01312, 0.01297, 0.01282, 0.01267, 0.01253, 0.01239, 0.01255, 0.01212, 0.01199],
        2.75: [0.01394, 0.01376, 0.01359, 0.01342, 0.01325, 0.01309, 0.01294, 0.01279, 0.01264, 0.01249, 0.01235, 0.01221, 0.01208, 0.01195, 0.01182],
        2.80: [0.01374, 0.01356, 0.01339, 0.01323, 0.01307, 0.01291, 0.01276, 0.01261, 0.01246, 0.01232, 0.01218, 0.01204, 0.01191, 0.01178, 0.01165],
        2.85: [0.01356, 0.01338, 0.01321, 0.01305, 0.01289, 0.01273, 0.01258, 0.01243, 0.01229, 0.01215, 0.01201, 0.01188, 0.01175, 0.01162, 0.01149],
    },
    index=range(16, 31)
)
K_TABLE.index.name = 'Temperature [°C]'
K_TABLE.columns.name = 'Specific Gravity'

TEMPERATURE_CORRECTION_FACTORS = pd.Series({
    15: -1.14, 15.5: -1.02, 16: -0.9, 16.5: -0.78, 17: -0.67,
    17.5: -0.56, 18: -0.46, 18.5: -0.35, 19: -0.25, 19.5: -0.15,
    20: -0.04, 20.5: 0.07, 21: 0.18, 21.5: 0.29, 22: 0.41,
    22.5: 0.53, 23: 0.66, 23.5: 0.8, 24: 0.95, 24.5: 1.11,
    25: 1.27, 25.5: 1.45
})

UNIT_WEIGHT_CORRECTION_FACTORS = pd.Series({
    2.95: 0.94, 2.85: 0.96, 2.8: 0.97, 2.75: 0.98, 2.7: 0.99,
    2.65: 1.0, 2.6: 1.01, 2.55: 1.02, 2.5: 1.04, 2.45: 1.05, 2.35: 1.08
})

HYDROMETER_TYPES = {
    '151H': HYDROMETER_151H,
    '152H': HYDROMETER_152H
}


def nearest(value, options):
    options = sorted(options)
    for i in range(len(options) - 1):
        midpoint = (options[i] + options[i + 1]) / 2
        if value < midpoint:
            return options[i]
    return options[-1]


def lookup_effective_depth(reading, series):
    if pd.isna(reading):
        return None
    if reading in series.index:
        return series.loc[reading]
    new_index = series.index.union([reading])
    return series.reindex(new_index).interpolate(method='index').loc[reading]


def lookup_K(temperature, specific_gravity):
    if pd.isna(temperature) or pd.isna(specific_gravity):
        return None
    nearest_sg   = nearest(specific_gravity, K_TABLE.columns.tolist())
    nearest_temp = nearest(temperature, K_TABLE.index.tolist())
    return K_TABLE.loc[nearest_temp, nearest_sg]

def process(test_data, sample_data, percent_passing_75um):
    test_data = test_data.copy()

    hydrometer_type = sample_data['Hydrometer Type']
    specific_gravity = sample_data['Specific Gravity']
    depth_series = HYDROMETER_TYPES[hydrometer_type]['Effective Depth L [cm]']

    test_data['Meniscus Corrected Hydrometer Reading'] = (
        test_data['Hydrometer Reading'] + sample_data['Meniscus Correction']
    )

    test_data['Effective Depth [cm]'] = test_data['Meniscus Corrected Hydrometer Reading'].apply(
        lambda x: lookup_effective_depth(x, depth_series)
    )

    test_data['K'] = test_data['Temperature [°C]'].apply(
        lambda temp: lookup_K(temp, specific_gravity)
    )

    elapsed = test_data['Elapsed Time [min]'].replace(0, float('nan'))
    test_data['Equivalent Particle Diameter [mm]'] = (
        test_data['K'] * (test_data['Effective Depth [cm]'] / elapsed) ** 0.5
    )

    test_data.loc[1:, 'Temperature Correction Factor'] = test_data['Temperature [°C]'].iloc[1:].apply(
        lambda temp: TEMPERATURE_CORRECTION_FACTORS.loc[nearest(temp, TEMPERATURE_CORRECTION_FACTORS.index)]
    )

    test_data.loc[1:, 'Unit Weight Correction Factor'] = (
        UNIT_WEIGHT_CORRECTION_FACTORS.loc[nearest(specific_gravity, UNIT_WEIGHT_CORRECTION_FACTORS.index)]
    )

    test_data['Corrected Hydrometer Reading'] = (
        test_data['Meniscus Corrected Hydrometer Reading']
        - sample_data['Composite Correction']
        + test_data['Temperature Correction Factor']
    )

    test_data['Percent Finer'] = (
        test_data.loc[1:, 'Corrected Hydrometer Reading']
        * test_data.loc[1:, 'Unit Weight Correction Factor']
    ) / sample_data['Tested Mass'] * 100

    test_data['Percent Finer A'] = (
        test_data['Percent Finer'] * percent_passing_75um
    ) / sample_data['Tested Mass']

    return test_data