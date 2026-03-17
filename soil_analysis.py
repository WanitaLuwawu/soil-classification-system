import pandas as pd
import numpy as np

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