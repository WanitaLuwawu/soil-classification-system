import pandas as pd

def read_sample_data(file, sheet_name) -> dict:
    """
    Reads a two-column Excel sheet and returns it as a key-value dictionary.

    Args:
        file: Path to the Excel file.
        sheet_name: Name or index of the sheet to read.

    Returns:
        A dict mapping values in column A to values in column B.
    """
    # Read the sheet with no header row, so all rows are treated as data
    data = pd.read_excel(file, sheet_name=sheet_name, header=None)

    # Zip the first column (keys) with the second column (values) into a dict
    return dict(zip(data[0], data[1]))


def read_tables(file, sheet_name, table_names, has_header=None) -> dict:
    """
    Reads multiple named tables stacked vertically within a single Excel sheet.

    Each table is assumed to be preceded by a title row whose first cell contains
    the table name. Tables are sliced from the row after their title up to the
    row before the next table title (or the end of the sheet for the last table).

    Args:
        file: Path to the Excel file.
        sheet_name: Name or index of the sheet to read.
        table_names: List of table title strings to locate within the sheet.
        has_header: Optional list of booleans, one per table, indicating whether
                    each table has a header row. Defaults to True for all tables.

    Returns:
        A dict mapping each table name to its corresponding cleaned DataFrame.
    """
    # Read the sheet without treating any row as a header
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)

    # Default all tables to having a header row if not specified
    if has_header is None:
        has_header = [True] * len(table_names)

    # Locate the row index of each table's title in the first column
    indices = []
    for name in table_names:
        idx = df[
            df.iloc[:, 0].astype(str).str.contains(name, na=False)
        ].index[0]
        indices.append(idx)

    tables = {}

    for i, name in enumerate(table_names):
        # Row where this table's title is found
        start = indices[i]

        # Slice from the row after the title up to the next table's title row;
        # for the last table, slice to the end of the sheet
        if i < len(indices) - 1:
            end = indices[i + 1]
            table = df[start + 1:end]
        else:
            table = df[start + 1:]

        # If the table has a header row, promote the first data row to column names
        # and drop it from the data; otherwise assign zero-based positional column names
        if has_header[i]:
            table.columns = table.iloc[0]
            table = table.iloc[1:]
        else:
            table.columns = list(range(table.shape[1]))

        # Clear the column index name carried over from the original DataFrame
        table.columns.name = None

        # Drop fully empty rows and reset the index to start from 0
        table = table.dropna(how='all').reset_index(drop=True)
        # Drop fully empty columns
        table = table.dropna(how='all', axis=1).reset_index(drop=True)

        tables[name] = table

    return tables