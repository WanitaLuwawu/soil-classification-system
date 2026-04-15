import pandas as pd

def read_sample_data(file, sheet_name):
    data = pd.read_excel(file, sheet_name=sheet_name, header=None)
    return dict(zip(data[0], data[1]))

def read_tables(file, sheet_name, table_names, has_header=None):
    # read the sheet without treating any row as a header
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)

    # default all tables to having a header row
    if has_header is None:
        has_header = [True] * len(table_names)

    # find the row index of each table title
    indices = []
    for name in table_names:
        idx = df[
            df.iloc[:, 0].astype(str).str.contains(name, na=False)
        ].index[0]
        indices.append(idx)

    tables = {}

    for i, name in enumerate(table_names):
        # row where the table title is found
        start = indices[i]

        # slice from the row after the title up to the next table title
        # for the last table, slice to the end of the sheet
        if i < len(indices) - 1:
            end = indices[i + 1]
            table = df[start + 1:end]
        else:
            table = df[start + 1:]

        # if the table has a header row, use the first row as column names
        # and drop it from the data; otherwise assign positional column names
        if has_header[i]:
            table.columns = table.iloc[0]
            table = table.iloc[1:]
        else:
            table.columns = list(range(table.shape[1]))

        # remove the column index name left over from the original DataFrame
        table.columns.name = None

        # drop fully empty rows and reset index to start from 0
        table = table.dropna(how='all').reset_index(drop=True)
        # drop fully empty columns
        table = table.dropna(how='all', axis=1).reset_index(drop=True)

        tables[name] = table

    return tables