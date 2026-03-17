import pandas as pd

def read_sieve_data(file):
    sieve_data = pd.read_excel(file, sheet_name='WS8 Sieve Analysis', header=None)

    # metadata
    end = sieve_data[sieve_data.iloc[:, 0].isna()].index[0]
    meta = sieve_data.iloc[:end]
    meta = dict(zip(meta[0], meta[1]))

    # section locations
    coarse_start = sieve_data[
        sieve_data.iloc[:, 0].astype(str).str.contains("Coarse Portion", na=False)
    ].index[0]

    fine_start = sieve_data[
        sieve_data.iloc[:, 0].astype(str).str.contains("Fine Portion", na=False)
    ].index[0]

    # coarse
    coarse = sieve_data[coarse_start + 1:fine_start]
    coarse.columns = coarse.iloc[0]
    coarse = coarse.iloc[1:]

    # fine
    fine = sieve_data[fine_start + 1:]
    fine.columns = fine.iloc[0]
    fine = fine.iloc[1:]

    return meta, coarse, fine


def read_sample_data(file):
    data = pd.read_excel(file, sheet_name='WS8 Data Sheet', header=None)
    return dict(zip(data[0], data[1]))