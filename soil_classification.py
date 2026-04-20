"""
Unified Soil Classification System (USCS) - ASTM D2487

Expected inputs (all floats, use None if not applicable/tested):
    percent_fines                : % passing No. 200 sieve
    percent_coarse_retained_no4  : % of coarse fraction retained on No. 4 sieve
    Cu                           : coefficient of uniformity  = D60 / D10
    Cc                           : coefficient of curvature   = (D30)^2 / (D60 * D10)
    LL                           : liquid limit (%)
    PL                           : plastic limit (%)           → PI = LL - PL
    LL_oven_dried                : liquid limit after oven drying
    is_highly_organic            : bool — set True if dark color + organic odor

Return dict keys:
    'group_symbol'  : str | None   — None if classification could not be completed
    'group_name'    : str | None   — None if classification could not be completed
    'category'      : str | None   — 'Coarse-Grained' | 'Fine-Grained' | 'Highly Organic' | None
    'notes'         : list[str]    — informational messages, warnings, and error reasons
    'error'         : bool         — True if classification failed due to missing data
"""


def classify_uscs(
    percent_fines: float,
    percent_coarse_retained_no4: float | None = None,
    Cu: float | None = None,
    Cc: float | None = None,
    LL: float | None = None,
    PL: float | None = None,
    LL_oven_dried: float | None = None,
    is_highly_organic: bool = False,
) -> dict:
    """
    Entry point for USCS classification. Routes the soil to the appropriate
    classification branch based on organic flag and percent fines.

    Peat is identified first via the field observation flag, then the soil is
    split into coarse-grained (< 50% fines) or fine-grained (≥ 50% fines)
    before delegating to the relevant sub-classifier.
    """
    notes = []

    # Compute PI upfront if both Atterberg limits are available;
    # None is propagated safely through all downstream checks
    PI = (LL - PL) if (LL is not None and PL is not None) else None

    # Highly organic soils (Peat) are identified by field observation and
    # classified directly — no index property tests are needed or meaningful
    if is_highly_organic:
        return _result("Pt", "Peat", "Highly Organic", notes)

    # Route to coarse or fine classification based on the No. 200 sieve split
    if percent_fines < 50:
        return _classify_coarse(
            percent_fines, percent_coarse_retained_no4, Cu, Cc, LL, PI,
            LL_oven_dried, notes
        )
    else:
        return _classify_fine(LL, PI, LL_oven_dried, notes)


# ---------------------------------------------------------------------------
# COARSE-GRAINED  (< 50 % passing No. 200)
# ---------------------------------------------------------------------------

def _classify_coarse(percent_fines, pct_coarse_retained_no4, Cu, Cc, LL, PI,
                     LL_oven_dried, notes) -> dict:
    """
    Distinguishes gravel from sand using the No. 4 sieve split, then delegates
    to the appropriate gravel or sand classifier.

    The No. 4 split is applied to the coarse fraction only (material retained
    on the No. 200 sieve). More than 50% of the coarse fraction retained on
    the No. 4 sieve → Gravel; otherwise → Sand.
    """
    # pct_coarse_retained_no4 is required to make the gravel/sand call;
    # without it the classification cannot proceed
    if pct_coarse_retained_no4 is None:
        notes.append(
            "Cannot distinguish Gravel from Sand: "
            "'percent_coarse_retained_no4' (% of coarse fraction retained on No. 4 sieve) "
            "is required for coarse-grained soils."
        )
        return _error_result(notes)

    # More than half of the coarse fraction retained on the No. 4 sieve → Gravel
    is_gravel = pct_coarse_retained_no4 > 50

    if is_gravel:
        return _classify_gravel(percent_fines, Cu, Cc, LL, PI, notes)
    else:
        return _classify_sand(percent_fines, Cu, Cc, LL, PI, notes)


def _classify_gravel(percent_fines, Cu, Cc, LL, PI, notes) -> dict:
    """
    Assigns a gravel group symbol based on fines content thresholds:
        < 5%   → Clean gravel (GW / GP) — requires Cu and Cc
        > 12%  → Gravel with fines (GM / GC / GC-GM) — requires LL and PI
        5–12%  → Dual symbol required (e.g. GW-GM, GP-GC) — requires all of the above
    """
    if percent_fines < 5:
        # Clean gravel: well-graded vs. poorly graded determined by Cu and Cc criteria
        symbol, err = _clean_gravel_symbol(Cu, Cc)
        if err:
            notes.append(err)
            return _error_result(notes)
        name = {"GW": "Well-graded gravel", "GP": "Poorly graded gravel"}[symbol]

    elif percent_fines > 12:
        # Gravel with significant fines: Atterberg limits determine silt vs. clay character
        symbol, err = _gravel_with_fines_symbol(LL, PI, notes)
        if err:
            notes.append(err)
            return _error_result(notes)
        name = {"GM": "Silty gravel", "GC": "Clayey gravel", "GC-GM": "Silty/clayey gravel"}.get(symbol, symbol)

    else:
        # Borderline fines content (5–12%): both gradation and plasticity criteria apply,
        # so a dual symbol combining a clean and a fines-based symbol is required
        notes.append("Fines 5–12 %: dual symbol required (e.g. GW-GM, GP-GC).")
        clean, err1 = _clean_gravel_symbol(Cu, Cc)
        fines, err2 = _gravel_with_fines_symbol(LL, PI, notes)
        if err1:
            notes.append(err1)
        if err2:
            notes.append(err2)
        if err1 or err2:
            return _error_result(notes)
        symbol = f"{clean}-{fines}"
        name   = f"Dual symbol gravel: {symbol}"

    return _result(symbol, name, "Coarse-Grained", notes)


def _classify_sand(percent_fines, Cu, Cc, LL, PI, notes) -> dict:
    """
    Assigns a sand group symbol based on fines content thresholds:
        < 5%   → Clean sand (SW / SP) — requires Cu and Cc
        > 12%  → Sand with fines (SM / SC / SC-SM) — requires LL and PI
        5–12%  → Dual symbol required (e.g. SW-SM, SP-SC) — requires all of the above
    """
    if percent_fines < 5:
        # Clean sand: well-graded vs. poorly graded determined by Cu and Cc criteria
        symbol, err = _clean_sand_symbol(Cu, Cc)
        if err:
            notes.append(err)
            return _error_result(notes)
        name = {"SW": "Well-graded sand", "SP": "Poorly graded sand"}[symbol]

    elif percent_fines > 12:
        # Sand with significant fines: Atterberg limits determine silt vs. clay character
        symbol, err = _sand_with_fines_symbol(LL, PI, notes)
        if err:
            notes.append(err)
            return _error_result(notes)
        name = {"SM": "Silty sand", "SC": "Clayey sand", "SC-SM": "Silty/clayey sand"}.get(symbol, symbol)

    else:
        # Borderline fines content (5–12%): both gradation and plasticity criteria apply,
        # so a dual symbol combining a clean and a fines-based symbol is required
        notes.append("Fines 5–12 %: dual symbol required (e.g. SW-SM, SP-SC).")
        clean, err1 = _clean_sand_symbol(Cu, Cc)
        fines, err2 = _sand_with_fines_symbol(LL, PI, notes)
        if err1:
            notes.append(err1)
        if err2:
            notes.append(err2)
        if err1 or err2:
            return _error_result(notes)
        symbol = f"{clean}-{fines}"
        name   = f"Dual symbol sand: {symbol}"

    return _result(symbol, name, "Coarse-Grained", notes)


def _clean_gravel_symbol(Cu, Cc) -> str:
    """
    Returns the GW / GP group symbol for a clean gravel (< 5% fines).

    ASTM D2487 well-graded criteria for gravel: Cu ≥ 4 AND 1 ≤ Cc ≤ 3.
    Both Cu and Cc must be available; missing either returns an error string.

    Returns:
        (symbol, None) on success, or (None, error_message) if data is missing.
    """
    # Both parameters are missing — give a combined error to avoid two separate messages
    if Cu is None and Cc is None:
        return None, (
            "Cu and Cc are both required to classify a clean gravel (< 5% fines). "
            "Run a grain-size analysis to obtain D10, D30, and D60."
        )
    if Cu is None:
        return None, (
            "Cu (= D60 / D10) is required to classify a clean gravel (< 5% fines) "
            "but was not provided."
        )
    if Cc is None:
        return None, (
            "Cc (= D30² / (D60 × D10)) is required to classify a clean gravel (< 5% fines) "
            "but was not provided."
        )

    # GW if both well-graded criteria are met; GP otherwise
    return ("GW" if Cu >= 4 and 1 <= Cc <= 3 else "GP"), None


def _gravel_with_fines_symbol(LL, PI, notes) -> str:
    """
    Returns the GM / GC / GC-GM group symbol for a gravel with fines (> 12% fines),
    based on where the soil plots relative to the A-line on the plasticity chart.

    GC  → PI > 7 and plots above A-line (clayey character)
    GM  → PI < 4 or plots below A-line (silty character)
    GC-GM → PI 4–7, plots in the shaded zone (dual symbol)

    Returns:
        (symbol, None) on success, or (None, error_message) if data is missing.
    """
    # PI requires both LL and PL; provide the most specific error message possible
    if PI is None:
        if LL is None:
            return None, (
                "LL and PL (to compute PI) are both required to classify a gravel "
                "with fines (> 12% fines). Run Atterberg limits tests."
            )
        return None, (
            "PL is required to compute PI for classifying a gravel with fines "
            "(> 12% fines) but was not provided."
        )

    if PI > 7 and _above_a_line(LL, PI):
        return "GC", None                              # Clearly above A-line → clayey gravel
    if PI < 4 or not _above_a_line(LL, PI):
        return "GM", None                              # Below A-line or low PI → silty gravel

    # PI 4–7 falls in the shaded zone between GM and GC on the plasticity chart
    notes.append("PI is 4–7 and plots in the shaded zone (Casagrande chart): dual symbol GC-GM assigned.")
    return "GC-GM", None


def _clean_sand_symbol(Cu, Cc) -> str:
    """
    Returns the SW / SP group symbol for a clean sand (< 5% fines).

    ASTM D2487 well-graded criteria for sand: Cu ≥ 6 AND 1 ≤ Cc ≤ 3.
    (Note: Cu threshold is 6 for sand vs. 4 for gravel.)
    Both Cu and Cc must be available; missing either returns an error string.

    Returns:
        (symbol, None) on success, or (None, error_message) if data is missing.
    """
    if Cu is None and Cc is None:
        return None, (
            "Cu and Cc are both required to classify a clean sand (< 5% fines). "
            "Run a grain-size analysis to obtain D10, D30, and D60."
        )
    if Cu is None:
        return None, (
            "Cu (= D60 / D10) is required to classify a clean sand (< 5% fines) "
            "but was not provided."
        )
    if Cc is None:
        return None, (
            "Cc (= D30² / (D60 × D10)) is required to classify a clean sand (< 5% fines) "
            "but was not provided."
        )

    # SW if both well-graded criteria are met; SP otherwise
    return ("SW" if Cu >= 6 and 1 <= Cc <= 3 else "SP"), None


def _sand_with_fines_symbol(LL, PI, notes) -> str:
    """
    Returns the SM / SC / SC-SM group symbol for a sand with fines (> 12% fines),
    based on where the soil plots relative to the A-line on the plasticity chart.

    SC    → PI > 7 and plots above A-line (clayey character)
    SM    → PI < 4 or plots below A-line (silty character)
    SC-SM → PI 4–7, plots in the shaded zone (dual symbol)

    Returns:
        (symbol, None) on success, or (None, error_message) if data is missing.
    """
    if PI is None:
        if LL is None:
            return None, (
                "LL and PL (to compute PI) are both required to classify a sand "
                "with fines (> 12% fines). Run Atterberg limits tests."
            )
        return None, (
            "PL is required to compute PI for classifying a sand with fines "
            "(> 12% fines) but was not provided."
        )

    if PI > 7 and _above_a_line(LL, PI):
        return "SC", None                              # Clearly above A-line → clayey sand
    if PI < 4 or not _above_a_line(LL, PI):
        return "SM", None                              # Below A-line or low PI → silty sand

    # PI 4–7 falls in the shaded zone between SM and SC on the plasticity chart
    notes.append("PI is 4–7 and plots in the shaded zone (Casagrande chart): dual symbol SC-SM assigned.")
    return "SC-SM", None


# ---------------------------------------------------------------------------
# FINE-GRAINED  (≥ 50 % passing No. 200)
# ---------------------------------------------------------------------------

def _classify_fine(LL, PI, LL_oven_dried, notes) -> dict:
    """
    Assigns a fine-grained group symbol using the plasticity chart (Casagrande chart),
    splitting on LL = 50 for the low/high plasticity boundary and using the A-line
    to distinguish clay (C) from silt (M) character.

    Organic soils are identified by the oven-dried LL ratio test (< 0.75 → organic),
    yielding OL or OH. If LL_oven_dried is not provided, organic soils cannot be
    detected and a warning is added to notes.
    """
    # Both LL and PI are needed to plot on the plasticity chart; fail early with
    # the most informative error possible
    if LL is None and PI is None:
        notes.append(
            "LL and PL (to compute PI) are both required to classify a fine-grained soil. "
            "Run Atterberg limits tests."
        )
        return _error_result(notes)
    if LL is None:
        notes.append(
            "LL is required to classify a fine-grained soil but was not provided."
        )
        return _error_result(notes)
    if PI is None:
        notes.append(
            "PL is required to compute PI for classifying a fine-grained soil "
            "but was not provided."
        )
        return _error_result(notes)

    # LL < 50 → low plasticity (L suffix); LL ≥ 50 → high plasticity (H suffix)
    ll_less_50 = LL < 50

    # Organic check: if the oven-dried LL drops to less than 75% of the natural LL,
    # the soil contains significant organic matter (ASTM D2487 criterion)
    if LL_oven_dried is not None:
        is_organic = (LL_oven_dried / LL) < 0.75
    else:
        # Without the oven-dried LL, organic soils cannot be distinguished from
        # inorganic soils with similar index properties
        is_organic = False
        notes.append(
            "LL_oven_dried was not provided: organic soils (OL/OH) cannot be identified. "
            "If organic content is suspected, run an oven-dried liquid limit test."
        )

    if ll_less_50:
        # Low plasticity branch (LL < 50)
        if is_organic:
            symbol, name = "OL", "Organic clay or silt of low plasticity"
        elif _above_a_line(LL, PI):
            if PI >= 7:
                symbol, name = "CL", "Lean clay"         # Clearly above A-line → clay
            else:
                # PI 4–7 and above A-line: CL-ML shaded zone on plasticity chart
                notes.append(
                    "PI is 4–7 and plots in the CL-ML zone (Casagrande chart): dual symbol CL-ML assigned."
                )
                symbol, name = "CL-ML", "Silty clay"
        else:
            symbol, name = "ML", "Silt"                  # Below A-line → silt character
    else:
        # High plasticity branch (LL ≥ 50)
        if is_organic:
            symbol, name = "OH", "Organic clay or silt of high plasticity"
        elif _above_a_line(LL, PI):
            symbol, name = "CH", "Fat clay"              # Above A-line → fat clay
        else:
            symbol, name = "MH", "Elastic silt"          # Below A-line → elastic silt

    return _result(symbol, name, "Fine-Grained", notes)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _above_a_line(LL, PI) -> bool:
    """
    Returns True if the soil plots above the A-line on Casagrande's plasticity chart.

    The A-line equation is: PI = 0.73 × (LL − 20).
    Soils above the A-line exhibit clay-like behaviour (C symbols);
    soils below exhibit silt-like behaviour (M symbols).
    """

    return PI >= abs(0.73 * (LL - 20))


def _result(symbol, name, category, notes) -> dict:
    """
    Constructs a successful classification result dict.

    Args:
        symbol:   USCS group symbol string (e.g. 'GW', 'CL').
        name:     USCS group name string (e.g. 'Well-graded gravel').
        category: Broad soil category string ('Coarse-Grained', 'Fine-Grained',
                  or 'Highly Organic').
        notes:    List of informational messages accumulated during classification.

    Returns:
        A result dict with 'error' set to False.
    """
    return {
        "group_symbol": symbol,
        "group_name":   name,
        "category":     category,
        "notes":        notes,
        "error":        False,
    }


def _error_result(notes) -> dict:
    """
    Constructs a failed classification result dict.

    Called whenever a required input is missing and classification cannot proceed.
    All soil property fields are set to None and 'error' is set to True.

    Args:
        notes: List of error messages explaining why classification failed.

    Returns:
        A result dict with all classification fields set to None and 'error' True.
    """
    return {
        "group_symbol": None,
        "group_name":   None,
        "category":     None,
        "notes":        notes,
        "error":        True,
    }