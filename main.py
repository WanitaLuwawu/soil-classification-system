import data_reader as dr
import sieve_analysis as sa_sieve
import hydrometer_analysis as sa_hydrometer
import atterberg_limits_analysis as sa_atterberg
import soil_properties as sp
import soil_classification as sc


# Supported test types
TEST_TYPES = {
    "1": "Sieve Analysis",
    "2": "Hydrometer Analysis",
    "3": "Atterberg Limits",
}

# Input functions

def prompt_file() -> str:
    return input("Enter the path to the Excel file: ").strip()


def prompt_test_type() -> str:
    print("\nSelect test type:")
    for key, name in TEST_TYPES.items():
        print(f"  {key}. {name}")
    while True:
        choice = input("Enter number: ").strip()
        if choice in TEST_TYPES:
            return TEST_TYPES[choice]
        print("  Invalid choice. Please enter 1, 2, or 3.")


def prompt_sheets_sieve() -> dict:
    print("\nEnter sheet names for Sieve Analysis:")
    return {
        "sieve_sheet":       input("  Sieve analysis sheet name: ").strip(),
        "data_sheet":        input("  Sample data sheet name (leave blank if none): ").strip(),
    }


def prompt_sheets_hydrometer() -> dict:
    print("\nEnter sheet names for Hydrometer Analysis:")
    return {
        "sieve_sheet":       input("  Sieve analysis sheet name: ").strip(),
        "hydrometer_sheet":  input("  Hydrometer analysis sheet name: ").strip(),
        "data_sheet":        input("  Sample data sheet name: ").strip(),
    }


def prompt_sheets_atterberg() -> dict:
    print("\nEnter sheet names for Atterberg Limits Analysis:")
    return {
        "atterberg_sheet":   input("  Atterberg limits sheet name: ").strip(),
    }


# Soil analysis functions

def run_sieve_analysis(file: str, sheets: dict):
    tables = dr.read_tables(
        file,
        sheets["sieve_sheet"],
        ['Experimental Mass', 'Coarse Portion', 'Fine Portion'],
        has_header=[False, True, True]
    )
    sample_data = dr.read_sample_data(file, sheets["data_sheet"]) if sheets['data_sheet'] else {}

    experimental_mass    = dict(zip(tables['Experimental Mass'].iloc[:, 0], tables['Experimental Mass'].iloc[:, 1]))
    initial_total_weight = experimental_mass['Initial Total Weight [g]']
    fines_weight         = experimental_mass['Fines Total Weight Before Wash [g]']

    coarse     = sa_sieve.process_coarse(tables['Coarse Portion'], initial_total_weight)
    fine       = sa_sieve.process_fine(tables['Fine Portion'], tables['Coarse Portion'], fines_weight)
    full_data  = sa_sieve.combine_data(coarse, fine)

    D10 = sa_sieve.get_D_value(full_data, 10)
    D30 = sa_sieve.get_D_value(full_data, 30)
    D60 = sa_sieve.get_D_value(full_data, 60)

    if D10 is not None and D30 is not None and D60 is not None:
        Cu = D60 / D10
        Cc = (D30 ** 2) / (D10 * D60)
    else:
        Cu = None
        Cc = None

    properties = sp.compute_properties(sample_data) if sample_data else None

    result = sc.classify_uscs(
        percent_fines               = fine[fine['Sieve Size [mm]'] == 0.075]['% Passing'].values[0],
        percent_coarse_retained_no4 = coarse[coarse['Sieve Size [mm]'] == 4.75]['% Retained'].values[0],
        Cu                          = Cu,
        Cc                          = Cc,
        LL                          = sample_data.get('Liquid Limit [-]'),
        PL                          = sample_data.get('Plastic Limit [-]'),
        LL_oven_dried               = None,
        is_highly_organic           = False,
    )
    return result


def run_hydrometer_analysis(file: str, sheets: dict):
    tables = dr.read_tables(
        file,
        sheets["sieve_sheet"],
        ['Experimental Mass', 'Sieve Analysis Before Hydrometer Testing', 'Sieve Analysis After Hydrometer Testing'],
        has_header=[False, True, True]
    )
    hydrometer_tables = dr.read_tables(
        file,
        sheets["hydrometer_sheet"],
        ['Hygroscopic Moisture Content Data', 'Hydrometer Test Sample Data', 'Hydrometer Test Data'],
        has_header=[False, False, True]
    )
    sample_data = dr.read_sample_data(file, sheets["data_sheet"])  if sheets['data_sheet'] else {}

    experimental_mass          = dict(zip(tables['Experimental Mass'].iloc[:, 0],           tables['Experimental Mass'].iloc[:, 1]))
    moisture_content_data      = dict(zip(hydrometer_tables['Hygroscopic Moisture Content Data'].iloc[:, 0], hydrometer_tables['Hygroscopic Moisture Content Data'].iloc[:, 1]))
    hydrometer_sample_data     = dict(zip(hydrometer_tables['Hydrometer Test Sample Data'].iloc[:, 0],       hydrometer_tables['Hydrometer Test Sample Data'].iloc[:, 1]))

    total_exp_mass             = experimental_mass['Initial Total Weight [g]']
    hygroscopic_correction     = moisture_content_data['Mass of Oven Dried Soil [g]'] / moisture_content_data['Mass of Air Dried Soil [g]']

    coarse                     = sa_sieve.process_coarse(tables['Sieve Analysis Before Hydrometer Testing'], total_exp_mass)
    percent_passing_2mm        = coarse.loc[coarse['Sieve Size [mm]'] == 2, '% Passing'].values[0]
    tested_mass                = (hygroscopic_correction * hydrometer_sample_data['Total Sample Mass']) / percent_passing_2mm * 100
    fine                       = sa_sieve.process_fine(tables['Sieve Analysis After Hydrometer Testing'], coarse, tested_mass)

    percent_passing_75um       = fine.loc[fine['Sieve Size [mm]'] == 0.075, '% Passing'].values[0]

    hydrometer_test_data       = sa_hydrometer.process(
        test_data            = hydrometer_tables['Hydrometer Test Data'],
        sample_data          = hydrometer_sample_data,
        percent_passing_75um = percent_passing_75um,
    )

    full_data  = sa_sieve.combine_data(coarse, fine)

    D10        = sa_sieve.get_D_value(full_data, 10)
    D30        = sa_sieve.get_D_value(full_data, 30)
    D60        = sa_sieve.get_D_value(full_data, 60)

    if D10 is not None and D30 is not None and D60 is not None:
        Cu = D60 / D10
        Cc = (D30 ** 2) / (D10 * D60)
    else:
        Cu = None
        Cc = None

    properties = sp.compute_properties(sample_data) if sample_data else None

    result = sc.classify_uscs(
        percent_fines               = percent_passing_75um,
        percent_coarse_retained_no4 = coarse[coarse['Sieve Size [mm]'] == 4.75]['% Retained'].values[0],
        Cu                          = Cu,
        Cc                          = Cc,
        LL                          = sample_data.get('Liquid Limit [-]'),
        PL                          = sample_data.get('Plastic Limit [-]'),
        LL_oven_dried               = None,
        is_highly_organic           = False,
    )
    return result


def run_atterberg_limits(file: str, sheets: dict):
    atterberg_tables = dr.read_tables(
        file,
        sheets["atterberg_sheet"],
        ['Liquid Limit', 'Plastic Limit'],
        has_header=[True, True]
    )

    ll_data, pl_data, ll, pl, pi = sa_atterberg.process(
        atterberg_tables['Liquid Limit'],
        atterberg_tables['Plastic Limit']
    )

    result = sc.classify_uscs(
        percent_fines     = 100,
        LL                = ll,
        PL                = pl,
        LL_oven_dried     = None,
        is_highly_organic = False,
    )
    return result

# Main

def main():
    file      = prompt_file()
    test_type = prompt_test_type()

    if test_type == "Sieve Analysis":
        sheets = prompt_sheets_sieve()
        result = run_sieve_analysis(file, sheets)

    elif test_type == "Hydrometer Analysis":
        sheets = prompt_sheets_hydrometer()
        result = run_hydrometer_analysis(file, sheets)

    elif test_type == "Atterberg Limits":
        sheets = prompt_sheets_atterberg()
        result = run_atterberg_limits(file, sheets)

    print("\n── USCS Classification ──────────────────")
    if result["error"]:
        print("  Classification failed:")
        for note in result["notes"]:
            print(f"  x {note}")
    else:
        print(f"  Group Symbol : {result['group_symbol']}")
        print(f"  Group Name   : {result['group_name']}")
        print(f"  Category     : {result['category']}")
        if result["notes"]:
            print("  Notes:")
            for note in result["notes"]:
                print(f"    - {note}")


if __name__ == "__main__":
    main()