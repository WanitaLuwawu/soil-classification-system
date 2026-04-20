import data_reader as dr
import sieve_analysis as sa_sieve
import hydrometer_analysis as sa_hydrometer
import atterberg_limits_analysis as sa_atterberg
import soil_properties as sp
import soil_classification as sc


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Maps menu selection numbers to their corresponding test type labels
TEST_TYPES = {
    "1": "Sieve Analysis",
    "2": "Hydrometer Analysis",
    "3": "Atterberg Limits",
}


# ---------------------------------------------------------------------------
# Input / prompt functions
# ---------------------------------------------------------------------------

def prompt_file() -> str:
    """Prompts the user for the path to the input Excel file."""
    return input("Enter the path to the Excel file: ").strip()


def prompt_test_type() -> str:
    """
    Displays the available test types and prompts the user to select one.
    Loops until a valid choice (1, 2, or 3) is entered.

    Returns:
        The test type label string (e.g. 'Sieve Analysis').
    """
    print("\nSelect test type:")
    for key, name in TEST_TYPES.items():
        print(f"  {key}. {name}")
    while True:
        choice = input("Enter number: ").strip()
        if choice in TEST_TYPES:
            return TEST_TYPES[choice]
        print("  Invalid choice. Please enter 1, 2, or 3.")


def prompt_sheets_sieve() -> dict:
    """
    Prompts the user for the sheet names required by the Sieve Analysis workflow.

    Returns:
        A dict with keys 'sieve_sheet' and 'data_sheet'.
        'data_sheet' may be an empty string if no sample data sheet exists.
    """
    print("\nEnter sheet names for Sieve Analysis:")
    return {
        "sieve_sheet": input("  Sieve analysis sheet name: ").strip(),
        "data_sheet":  input("  Sample data sheet name (leave blank if none): ").strip(),
    }


def prompt_sheets_hydrometer() -> dict:
    """
    Prompts the user for the sheet names required by the Hydrometer Analysis workflow.

    Returns:
        A dict with keys 'sieve_sheet', 'hydrometer_sheet', and 'data_sheet'.
    """
    print("\nEnter sheet names for Hydrometer Analysis:")
    return {
        "sieve_sheet":      input("  Sieve analysis sheet name: ").strip(),
        "hydrometer_sheet": input("  Hydrometer analysis sheet name: ").strip(),
        "data_sheet":       input("  Sample data sheet name: ").strip(),
    }


def prompt_sheets_atterberg() -> dict:
    """
    Prompts the user for the sheet name required by the Atterberg Limits workflow.

    Returns:
        A dict with key 'atterberg_sheet'.
    """
    print("\nEnter sheet names for Atterberg Limits Analysis:")
    return {
        "atterberg_sheet": input("  Atterberg limits sheet name: ").strip(),
    }


# ---------------------------------------------------------------------------
# Soil analysis functions
# ---------------------------------------------------------------------------

def run_sieve_analysis(file: str, sheets: dict) -> tuple[dict, dict | None]:
    """
    Executes the full Sieve Analysis workflow:
      1. Reads coarse and fine sieve tables and optional sample data from Excel.
      2. Processes percent retained / passing for both fractions.
      3. Interpolates D10, D30, D60 and computes Cu and Cc.
      4. Computes geotechnical properties if sample data is present.
      5. Classifies the soil using USCS.

    Args:
        file:   Path to the input Excel file.
        sheets: Dict with keys 'sieve_sheet' and 'data_sheet' (may be empty string).

    Returns:
        A (result, properties) tuple where result is the USCS classification dict
        and properties is the geotechnical properties dict (or None if no sample data).
    """
    # Read the three stacked tables from the sieve sheet; Experimental Mass has
    # no header row, the two portion tables do
    tables = dr.read_tables(
        file,
        sheets["sieve_sheet"],
        ['Experimental Mass', 'Coarse Portion', 'Fine Portion'],
        has_header=[False, True, True]
    )

    # Read optional sample-level metadata (specific gravity, Atterberg limits, etc.)
    sample_data = dr.read_sample_data(file, sheets["data_sheet"]) if sheets['data_sheet'] else {}

    # Unpack the two key mass measurements from the Experimental Mass table
    experimental_mass    = dict(zip(tables['Experimental Mass'].iloc[:, 0], tables['Experimental Mass'].iloc[:, 1]))
    initial_total_weight = experimental_mass['Initial Total Weight [g]']
    fines_weight         = experimental_mass['Fines Total Weight Before Wash [g]']

    # Compute cumulative weights and percent passing for both fractions
    coarse    = sa_sieve.process_coarse(tables['Coarse Portion'], initial_total_weight)
    fine      = sa_sieve.process_fine(tables['Fine Portion'], tables['Coarse Portion'], fines_weight)
    full_data = sa_sieve.combine_data(coarse, fine)

    # Interpolate the characteristic diameters from the combined gradation curve
    D10 = sa_sieve.get_D_value(full_data, 10)
    D30 = sa_sieve.get_D_value(full_data, 30)
    D60 = sa_sieve.get_D_value(full_data, 60)

    # Cu and Cc are only meaningful if all three diameters are available;
    # any missing D-value (outside the tested range) yields None for both
    if D10 is not None and D30 is not None and D60 is not None:
        Cu = D60 / D10
        Cc = (D30 ** 2) / (D10 * D60)
    else:
        Cu = None
        Cc = None

    # Compute bulk density, unit weight, moisture content, void ratio, and porosity
    # only if sample data was provided
    properties = sp.compute_properties(sample_data) if sample_data else None

    # Classify using percent passing the No. 200 sieve (0.075 mm) as percent fines
    # and percent retained on the No. 4 sieve (4.75 mm) for the gravel/sand split
    result = sc.classify_uscs(
        percent_fines               = fine[fine['Sieve Size [mm]'] == 0.075]['% Passing'].values[0],
        percent_coarse_retained_no4 = coarse[coarse['Sieve Size [mm]'] == 4.75]['% Retained'].values[0],
        Cu                          = Cu,
        Cc                          = Cc,
        LL                          = sample_data.get('Liquid Limit [-]'),
        PL                          = sample_data.get('Plastic Limit [-]'),
        LL_oven_dried               = None,   # Not tested in sieve-only workflow
        is_highly_organic           = False,  # Not assessed in sieve-only workflow
    )
    return result, properties


def run_hydrometer_analysis(file: str, sheets: dict) -> tuple[dict, dict | None]:
    """
    Executes the full Hydrometer Analysis workflow:
      1. Reads sieve tables (pre- and post-hydrometer) and hydrometer test data from Excel.
      2. Computes hygroscopic moisture content and correction factor for the sub-sample.
      3. Derives the oven-dry tested mass scaled to the full sample via the 2 mm passing fraction.
      4. Processes percent passing for both sieve fractions.
      5. Runs the hydrometer analysis to obtain equivalent particle diameters and percent finer.
      6. Interpolates D10, D30, D60 and computes Cu and Cc.
      7. Computes geotechnical properties if sample data is present.
      8. Classifies the soil using USCS.

    Args:
        file:   Path to the input Excel file.
        sheets: Dict with keys 'sieve_sheet', 'hydrometer_sheet', and 'data_sheet'.

    Returns:
        A (result, properties) tuple where result is the USCS classification dict
        and properties is the geotechnical properties dict (or None if no sample data).
    """
    # Read pre- and post-hydrometer sieve tables from the sieve sheet
    tables = dr.read_tables(
        file,
        sheets["sieve_sheet"],
        ['Experimental Mass', 'Sieve Analysis Before Hydrometer Testing', 'Sieve Analysis After Hydrometer Testing'],
        has_header=[False, True, True]
    )

    # Read hygroscopic moisture content, hydrometer sample metadata, and time-series readings
    hydrometer_tables = dr.read_tables(
        file,
        sheets["hydrometer_sheet"],
        ['Hygroscopic Moisture Content Data', 'Hydrometer Test Sample Data', 'Hydrometer Test Data'],
        has_header=[False, False, True]
    )

    sample_data = dr.read_sample_data(file, sheets["data_sheet"]) if sheets['data_sheet'] else {}

    # Unpack the total experimental mass used to scale coarse sieve percentages
    experimental_mass = dict(zip(tables['Experimental Mass'].iloc[:, 0], tables['Experimental Mass'].iloc[:, 1]))
    total_exp_mass    = experimental_mass['Initial Total Weight [g]']

    # Compute hygroscopic moisture content and the correction factor needed to
    # convert the air-dried sub-sample mass to an oven-dry equivalent
    moisture_data = dict(zip(
        hydrometer_tables['Hygroscopic Moisture Content Data'].iloc[:, 0],
        hydrometer_tables['Hygroscopic Moisture Content Data'].iloc[:, 1]
    ))
    moisture_data['Mass of Air Dried Soil [g]']         = moisture_data['Air Dried Mass + Pan [g]'] - moisture_data['Mass of Pan [g]']
    moisture_data['Mass of Oven Dried Soil [g]']        = moisture_data['Oven Dried Mass + Pan [g]'] - moisture_data['Mass of Pan [g]']
    moisture_data['Mass of Water [g]']                  = moisture_data['Mass of Air Dried Soil [g]'] - moisture_data['Mass of Oven Dried Soil [g]']
    moisture_data['Hygroscopic Moisture Content [%]']   = moisture_data['Mass of Water [g]'] / moisture_data['Mass of Oven Dried Soil [g]'] * 100
    moisture_data['Hygroscopic Correction Factor [-]']  = moisture_data['Mass of Oven Dried Soil [g]'] / moisture_data['Mass of Air Dried Soil [g]']

    # Unpack the hydrometer sample metadata (hydrometer type, specific gravity, corrections, etc.)
    hydrometer_sample_data = dict(zip(
        hydrometer_tables['Hydrometer Test Sample Data'].iloc[:, 0],
        hydrometer_tables['Hydrometer Test Sample Data'].iloc[:, 1]
    ))

    # Process the pre-hydrometer sieve data to get the coarse gradation curve
    coarse             = sa_sieve.process_coarse(tables['Sieve Analysis Before Hydrometer Testing'], total_exp_mass)
    percent_passing_2mm = coarse.loc[coarse['Sieve Size [mm]'] == 2, '% Passing'].values[0]

    # Scale the hydrometer sub-sample mass to the oven-dry equivalent for the full
    # sample: apply the hygroscopic correction, then scale up via the 2 mm passing fraction
    hydrometer_sample_data['Tested Mass [g]'] = (
        moisture_data['Hygroscopic Correction Factor [-]'] * hydrometer_sample_data['Total Sample Mass [g]']
    ) / percent_passing_2mm * 100

    # Process the post-hydrometer sieve data (fine fraction) aligned to the coarse curve
    fine                = sa_sieve.process_fine(
        tables['Sieve Analysis After Hydrometer Testing'], coarse, hydrometer_sample_data['Tested Mass [g]']
    )
    percent_passing_75um = fine.loc[fine['Sieve Size [mm]'] == 0.075, '% Passing'].values[0]

    # Run the hydrometer analysis to compute equivalent particle diameters and percent finer
    hydrometer_test_data = sa_hydrometer.process(
        test_data            = hydrometer_tables['Hydrometer Test Data'],
        sample_data          = hydrometer_sample_data,
        percent_passing_75um = percent_passing_75um,
    )

    # Combine sieve and hydrometer data into a single gradation curve for D-value interpolation
    full_data = sa_sieve.combine_data(coarse, fine)

    D10 = sa_sieve.get_D_value(full_data, 10)
    D30 = sa_sieve.get_D_value(full_data, 30)
    D60 = sa_sieve.get_D_value(full_data, 60)

    # Cu and Cc require all three D-values; set to None if any are outside the tested range
    if D10 is not None and D30 is not None and D60 is not None:
        Cu = D60 / D10
        Cc = (D30 ** 2) / (D10 * D60)
    else:
        Cu = None
        Cc = None

    properties = sp.compute_properties(sample_data) if sample_data else None

    # Classify using the percent passing 75 µm as percent fines (from the hydrometer curve)
    result = sc.classify_uscs(
        percent_fines               = percent_passing_75um,
        percent_coarse_retained_no4 = coarse[coarse['Sieve Size [mm]'] == 4.75]['% Retained'].values[0],
        Cu                          = Cu,
        Cc                          = Cc,
        LL                          = sample_data.get('Liquid Limit [-]'),
        PL                          = sample_data.get('Plastic Limit [-]'),
        LL_oven_dried               = None,   # Not tested in this workflow
        is_highly_organic           = False,  # Not assessed in this workflow
    )
    return result, properties


def run_atterberg_limits(file: str, sheets: dict) -> dict:
    """
    Executes the Atterberg Limits workflow:
      1. Reads Liquid Limit and Plastic Limit tables from Excel.
      2. Computes LL, PL, and PI from the raw test data.
      3. Classifies the soil as fine-grained (100% fines assumed) using USCS.

    Args:
        file:   Path to the input Excel file.
        sheets: Dict with key 'atterberg_sheet'.

    Returns:
        The USCS classification result dict.
    """
    # Read the two Atterberg limits tables (LL blow count data and PL thread-rolling data)
    atterberg_tables = dr.read_tables(
        file,
        sheets["atterberg_sheet"],
        ['Liquid Limit', 'Plastic Limit'],
        has_header=[True, True]
    )

    # Fit the flow curve and compute LL, PL, and PI
    ll_data, pl_data, ll, pl, pi = sa_atterberg.process(
        atterberg_tables['Liquid Limit'],
        atterberg_tables['Plastic Limit']
    )

    # Atterberg limits are only performed on fine-grained soils, so percent_fines
    # is set to 100 to route directly to the fine-grained classification branch
    result = sc.classify_uscs(
        percent_fines     = 100,
        LL                = ll,
        PL                = pl,
        LL_oven_dried     = None,   # Not tested in this workflow
        is_highly_organic = False,  # Not assessed in this workflow
    )
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """
    Entry point for the soil classification CLI.
    Prompts the user for a file path and test type, runs the appropriate
    analysis workflow, and prints the USCS classification and sample
    properties to the console.
    """
    file      = prompt_file()
    test_type = prompt_test_type()

    # Dispatch to the appropriate analysis function based on the selected test type
    if test_type == "Sieve Analysis":
        sheets = prompt_sheets_sieve()
        result, properties = run_sieve_analysis(file, sheets)

    elif test_type == "Hydrometer Analysis":
        sheets = prompt_sheets_hydrometer()
        result, properties = run_hydrometer_analysis(file, sheets)

    elif test_type == "Atterberg Limits":
        sheets = prompt_sheets_atterberg()
        result = run_atterberg_limits(file, sheets)
        properties = None  # Atterberg-only workflow does not compute sample properties

    # Print USCS classification result, showing error details or full symbol/name/category
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

    # Print geotechnical properties only if they were computed (requires sample data)
    if properties:
        print("\n── Sample Properties ────────────────────")
        print(f"  Bulk Density [kg]    : {properties['Bulk Density [kg]']:.2f}")
        print(f"  Unit Weight [kN/m^3] : {properties['Unit Weight [kN/m^3]']:.2f}")
        print(f"  Moisture Content [%] : {properties['Moisture Content [%]']:.3f}")
        print(f"  Void Ratio [-]       : {properties['Void Ratio [-]']:.3f}")
        print(f"  Porosity [-]         : {properties['Porosity [-]']:.3f}")


if __name__ == "__main__":
    main()