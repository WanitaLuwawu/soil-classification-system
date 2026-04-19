"""
Unified Soil Classification System (USCS) - ASTM D2487

Expected inputs (all floats, use None if not applicable/tested):
    percent_fines                : % passing No. 200 sieve
    percent_coarse_retained_no4  : % of coarse fraction retained on No. 4 sieve
    Cu                           : coefficient of uniformity  = D60 / D10
    Cc                           : coefficient of curvature   = (D30)^2 / (D60 * D10)
    LL                           : liquid limit (%)
    PL                           : plastic limit (%)           → PI = LL - PL
    LL_oven_dried                : liquid limit after oven drying (for organic check)
    is_highly_organic            : bool — set True if dark color + organic odor (field call)

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
):
    notes = []
    PI = (LL - PL) if (LL is not None and PL is not None) else None

    # Highly Organic (Peat)
    if is_highly_organic:
        return _result("Pt", "Peat", "Highly Organic", notes)

    # Split coarse vs fine
    if percent_fines < 50:
        return _classify_coarse(
            percent_fines, percent_coarse_retained_no4, Cu, Cc, LL, PI,
            LL_oven_dried, notes
        )
    else:
        return _classify_fine(LL, PI, LL_oven_dried, notes)


# COARSE-GRAINED  (< 50 % passing No. 200)

def _classify_coarse(percent_fines, pct_coarse_retained_no4, Cu, Cc, LL, PI,
                     LL_oven_dried, notes):
    if pct_coarse_retained_no4 is None:
        notes.append(
            "Cannot distinguish Gravel from Sand: "
            "'percent_coarse_retained_no4' (% of coarse fraction retained on No. 4 sieve) "
            "is required for coarse-grained soils."
        )
        return _error_result(notes)

    is_gravel = pct_coarse_retained_no4 > 50

    if is_gravel:
        return _classify_gravel(percent_fines, Cu, Cc, LL, PI, notes)
    else:
        return _classify_sand(percent_fines, Cu, Cc, LL, PI, notes)


def _classify_gravel(percent_fines, Cu, Cc, LL, PI, notes):
    if percent_fines < 5: # Clean gravel
        symbol, err = _clean_gravel_symbol(Cu, Cc)
        if err:
            notes.append(err)
            return _error_result(notes)
        name = {"GW": "Well-graded gravel", "GP": "Poorly graded gravel"}[symbol]

    elif percent_fines > 12: # Gravel with fines
        symbol, err = _gravel_with_fines_symbol(LL, PI, notes)
        if err:
            notes.append(err)
            return _error_result(notes)
        name = {"GM": "Silty gravel", "GC": "Clayey gravel", "GC-GM": "Silty/clayey gravel"}.get(symbol, symbol)

    else: # 5–12 %: dual symbol required
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


def _classify_sand(percent_fines, Cu, Cc, LL, PI, notes):
    if percent_fines < 5: # Clean sand
        symbol, err = _clean_sand_symbol(Cu, Cc)
        if err:
            notes.append(err)
            return _error_result(notes)
        name = {"SW": "Well-graded sand", "SP": "Poorly graded sand"}[symbol]

    elif percent_fines > 12: # Sand with fines
        symbol, err = _sand_with_fines_symbol(LL, PI, notes)
        if err:
            notes.append(err)
            return _error_result(notes)
        name = {"SM": "Silty sand", "SC": "Clayey sand", "SC-SM": "Silty/clayey sand"}.get(symbol, symbol)

    else: # 5–12 %: dual symbol required
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

def _clean_gravel_symbol(Cu, Cc):
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
    return ("GW" if Cu >= 4 and 1 <= Cc <= 3 else "GP"), None


def _gravel_with_fines_symbol(LL, PI, notes):
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
        return "GC", None
    if PI < 4 or not _above_a_line(LL, PI):
        return "GM", None
    # 4 ≤ PI ≤ 7 hatched zone
    notes.append("PI is 4–7 and plots in the hatched zone (Fig. 3.16): dual symbol GC-GM assigned.")
    return "GC-GM", None

def _clean_sand_symbol(Cu, Cc):
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
    return ("SW" if Cu >= 6 and 1 <= Cc <= 3 else "SP"), None


def _sand_with_fines_symbol(LL, PI, notes):
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
        return "SC", None
    if PI < 4 or not _above_a_line(LL, PI):
        return "SM", None
    # 4 ≤ PI ≤ 7 hatched zone
    notes.append("PI is 4–7 and plots in the hatched zone (Fig. 3.16): dual symbol SC-SM assigned.")
    return "SC-SM", None

# FINE-GRAINED  (≥ 50 % passing No. 200)

def _classify_fine(LL, PI, LL_oven_dried, notes):
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

    ll_less_50 = LL < 50

    # Organic check (ratio test)
    if LL_oven_dried is not None:
        is_organic = (LL_oven_dried / LL) < 0.75
    else:
        is_organic = False
        notes.append(
            "LL_oven_dried was not provided: organic soils (OL/OH) cannot be identified. "
            "If organic content is suspected, run an oven-dried liquid limit test."
        )

    if ll_less_50:
        if is_organic:
            symbol, name = "OL", "Organic clay or silt of low plasticity"
        elif _above_a_line(LL, PI):
            if PI >= 7:
                symbol, name = "CL", "Lean clay"
            else:
                notes.append(
                    "PI is 4–7 and plots in the CL-ML zone (Fig. 3.16): dual symbol CL-ML assigned."
                )
                symbol, name = "CL-ML", "Silty clay"
        else:
            symbol, name = "ML", "Silt"
    else:
        if is_organic:
            symbol, name = "OH", "Organic clay or silt of high plasticity"
        elif _above_a_line(LL, PI):
            symbol, name = "CH", "Fat clay"
        else:
            symbol, name = "MH", "Elastic silt"

    return _result(symbol, name, "Fine-Grained", notes)

def _above_a_line(LL, PI):
    return PI >= 0.73 * (LL - 20)


def _result(symbol, name, category, notes):
    return {
        "group_symbol": symbol,
        "group_name":   name,
        "category":     category,
        "notes":        notes,
        "error":        False,
    }


def _error_result(notes):
    return {
        "group_symbol": None,
        "group_name":   None,
        "category":     None,
        "notes":        notes,
        "error":        True,
    }