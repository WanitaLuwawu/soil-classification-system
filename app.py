import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import atterberg_limits_analysis as sa_atterberg
import data_reader as dr
import hydrometer_analysis as sa_hydrometer
import sieve_analysis as sa_sieve
import soil_classification as sc
import soil_properties as sp

# ─────────────────────────────────────────────────────────────────────────────
# Page config & styling
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Soil Classification System",
    page_icon="🪨",
    layout="wide",
)

# Inject global CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700;
    letter-spacing: -0.3px;
}

.stApp {
    background-color: #F9F7F2;
}

/* Cards */
.result-card {
    background: #ffffff;
    border: 1px solid #ddd8cc;
    border-left: 5px solid #2D5A27;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 0.5rem 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.result-symbol {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2D5A27;
    letter-spacing: 2px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.result-name {
    font-size: 1rem;
    color: #4a3f30;
    margin-top: 0.25rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.result-category {
    font-size: 0.7rem;
    color: #D46A3C;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 0.5rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
}

/* Notes */
.note-info {
    background: #eef4ed;
    border-left: 3px solid #2D5A27;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    font-size: 0.75rem;
    color: #1e3d1a;
    margin: 0.25rem 0;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.note-error {
    background: #fdf1eb;
    border-left: 3px solid #D46A3C;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    font-size: 0.75rem;
    color: #7a3010;
    margin: 0.25rem 0;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Property boxes */
.prop-box {
    background: #ffffff;
    border: 1px solid #ddd8cc;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

.prop-label {
    font-size: 0.8rem;
    color: #D46A3C;
    letter-spacing: 1px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
}

.prop-value {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1e2d1f;
    font-family: 'Plus Jakarta Sans', sans-serif;
    margin-top: 0.15rem;
}

/* Section labels */
.section-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #D46A3C;
    margin: 1.5rem 0 0.5rem 0;
    border-bottom: 1px solid #ddd8cc;
    padding-bottom: 0.4rem;
}

/* Table headers */
div[data-testid="stTable"] th {
    background-color: #2D5A27 !important;
    color: #F9F7F2 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    padding: 0.6rem 1rem !important;
    border: none !important;
    text-align: center !important;
}

/* Table rows */
div[data-testid="stTable"] td {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.7rem !important;
    color: #2c2c2c !important;
    padding: 0.5rem 1rem !important;
    border-bottom: 1px solid #ede8df !important;
}

/* Alternating row colour */
div[data-testid="stTable"] tr:nth-child(even) td {
    background-color: #f5f2ec !important;
}

/* Row hover */
div[data-testid="stTable"] tr:hover td {
    background-color: #eef4ed !important;
}

/* Sidebar */

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #1e2d1f !important;
}

div[data-testid="stMarkdownContainer"] h2 {
    color: #F9F7F2 !important;
}

/* Sidebar text — specific tags only, not inside widgets */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #c8dbc5 !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] p,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span {
    color: #000000 !important;
}

/* Section labels */
section[data-testid="stSidebar"] .section-label {
    color: #E29578 !important;
    border-bottom-color: #3d5c3e !important;
}

/* Input fields */
section[data-testid="stSidebar"] input {
    background-color: #2a3d2b !important;
    border-color: #3d5c3e !important;
    border-radius: 6px !important;
    color: #e8f0e8 !important;
    caret-color: #e8f0e8 !important;
}

div[data-baseweb="select"] input {
    color: transparent !important;
    background-color: transparent !important;
    border-color: transparent !important;
}

input[role="combobox"],
input[role="combobox"]:focus {
    caret-color: transparent !important;
}

/* Button */
.stButton > button {
    background: #2D5A27 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    letter-spacing: 1px !important;
    padding: 0.5rem 1.5rem !important;
    transition: background 0.15s;
}
.stButton > button p {
    color: #FFFFFF !important;
}

.stButton > button:hover {
    background: #D46A3C !important;
}

/* Scrollbar */
@supports (scrollbar-color: transparent transparent) {
    div[data-testid="stSidebarContent"]:hover {
        scrollbar-color: #88A47C #1e2d1f !important;
    }
}

div[data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
    background: #88A47C !important;
    border-radius: 4px;
}

div[data-testid="stSidebarContent"]::-webkit-scrollbar-track {
    background: #1e2d1f !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] p {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    color: #6b5f4e !important;
}

.stTabs [aria-selected="true"] {
    color: #2D5A27 !important;
    border-bottom-color: #2D5A27 !important;
}

/* File uploader */
div[data-testid="stFileUploader"] {
    background: #ffffff;
    border: None;
    border-radius: 10px;
    padding: 0.5rem;
}

/* Info box — green */
div[data-baseweb="notification"] {
    background-color: #eef4ed !important;
    border: 1px solid #c2d4c0 !important;
    border-left: 4px solid #2D5A27 !important;
    border-radius: 8px !important;
}

div[data-baseweb="notification"] p,
div[data-baseweb="notification"] svg {
    color: #1e3d1a !important;
    fill: #2D5A27 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.8rem !important;
}

/* Warning box — amber */
div[data-testid="stAlert"][kind="warning"] {
    background-color: #fdf8ed !important;
    border: 1px solid #e8d8a0 !important;
    border-left: 4px solid #D46A3C !important;
    border-radius: 8px !important;
}

div[data-testid="stAlert"][kind="warning"] p,
div[data-testid="stAlert"][kind="warning"] svg {
    color: #7a3010 !important;
    fill: #D46A3C !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.8rem !important;
}

/* Error box — red */
div[data-testid="stAlert"][kind="error"] {
    background-color: #fdf1f1 !important;
    border: 1px solid #e8c2c2 !important;
    border-left: 4px solid #c0392b !important;
    border-radius: 8px !important;
}

div[data-testid="stAlert"][kind="error"] p,
div[data-testid="stAlert"][kind="error"] svg {
    color: #7a1010 !important;
    fill: #c0392b !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def safe_read_sample_data(file_bytes, sheet_name) -> dict:
    """
    Attempts to read sample metadata from the given sheet, returning an empty
    dict if the sheet name is blank, missing, or raises any read error.
    This allows the sample data sheet to be optional without crashing the app.
    """
    if not sheet_name:
        return {}
    try:
        return dr.read_sample_data(file_bytes, sheet_name)
    except Exception:
        return {}


def safe_compute_cu_cc(full_data) -> tuple[float, float, float, float, float] | tuple[float, float, float, None, None]:
    """
    Interpolates D10, D30, and D60 from the combined gradation curve and
    computes Cu and Cc. Returns None for Cu and Cc if any D-value falls
    outside the tested sieve range and cannot be interpolated.

    Returns:
        (D10, D30, D60, Cu, Cc) — any value may be None if not determinable.
    """
    D10 = sa_sieve.get_D_value(full_data, 10)
    D30 = sa_sieve.get_D_value(full_data, 30)
    D60 = sa_sieve.get_D_value(full_data, 60)
    if D10 and D30 and D60:
        return D10, D30, D60, D60 / D10, (D30 ** 2) / (D10 * D60)
    return D10, D30, D60, None, None


# Shared Plotly layout applied to all charts via unpacking (**PLOTLY_LAYOUT)
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#F9F7F2",
    plot_bgcolor="#ffffff",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#4a3f30", size=11),
    margin=dict(l=60, r=30, t=40, b=60),
)

# Shared axis style applied to individual xaxis/yaxis dicts via unpacking (**AXIS_STYLE)
AXIS_STYLE = dict(gridcolor="#ede8df", linecolor="#ddd8cc", zerolinecolor="#ddd8cc")


# ─────────────────────────────────────────────────────────────────────────────
# Chart builders
# ─────────────────────────────────────────────────────────────────────────────

def plot_gradation_curve(full_data, D10=None, D30=None, D60=None, title="Gradation Curve"):
    """
    Builds a Plotly log-scale gradation curve with optional D10/D30/D60 markers
    and drop lines showing each characteristic diameter and its percent passing.

    Args:
        full_data: Combined coarse + fine sieve DataFrame with 'Sieve Size [mm]'
                   and '% Passing' columns.
        D10, D30, D60: Characteristic diameters [mm] to annotate; omitted if None.
        title: Chart title string.

    Returns:
        A Plotly Figure object ready for st.plotly_chart().
    """
    fig = go.Figure()

    # Main gradation trace — spline smoothing for a continuous-looking curve
    fig.add_trace(go.Scatter(
        x=full_data["Sieve Size [mm]"],
        y=full_data["% Passing"],
        mode="lines+markers",
        name="Gradation",
        line=dict(color="#2D5A27", width=2, shape="spline", smoothing=0.85),
        marker=dict(size=5, color="#2D5A27"),
    ))

    # Add a diamond marker and horizontal + vertical drop lines for each D-value
    for d_val, label, color in [(D10, "D₁₀", "#D46A3C"), (D30, "D₃₀", "#2D5A27"), (D60, "D₆₀", "#8a4a1a")]:
        if d_val is not None:
            pct = {"D₁₀": 10, "D₃₀": 30, "D₆₀": 60}[label]
            fig.add_trace(go.Scatter(
                x=[d_val], y=[pct],
                mode="markers+text",
                name=f"{label} = {d_val:.4f} mm",
                marker=dict(size=10, color=color, symbol="diamond"),
                text=[f" {label}"], textposition="top left",
                textfont=dict(color=color, size=13),
            ))
            # Vertical drop line from the D-value marker down to the x-axis
            fig.add_shape(type="line", x0=d_val, x1=d_val, y0=0, y1=pct,
                          line=dict(color=color, width=1, dash="dot"))
            # Horizontal drop line from the y-axis across to the D-value marker
            fig.add_shape(type="line", x0=0.01, x1=d_val, y0=pct, y1=pct,
                          line=dict(color=color, width=1, dash="dot"))

    fig.update_layout(
        **{**PLOTLY_LAYOUT, "margin": dict(l=60, r=30, t=80, b=60)},
        title=dict(
            text=title,
            font=dict(size=17, color="#2c2c2c"),
            y=0.95,
            yanchor="top",
        ),
        xaxis=dict(
            **AXIS_STYLE,
            type="log",
            title="Particle Size (mm)",
            range=[-2, 2],  # log10 range: 10⁻² = 0.01 mm → 10² = 100 mm
            dtick=1,  # major gridlines at each power of 10 only
            tickformat=".3g",  # clean tick labels: 100, 10, 1, 0.1, 0.01
        ),
        yaxis=dict(
            **AXIS_STYLE,
            title="% Passing",
            range=[0, 100],
        ),
        legend=dict(
            bgcolor="#ffffff", bordercolor="#ddd8cc", borderwidth=1,
            font=dict(size=13),
        ),
    )
    return fig


def plot_casagrande(ll=None, pi=None, label="Sample"):
    """
    Builds a Plotly Casagrande plasticity chart including the A-line, U-line,
    zone labels, the CL-ML hatched zone, the LL=50 divider, and an optional
    sample marker.

    Args:
        ll: Liquid Limit [%] of the sample to plot; omitted if None.
        pi: Plasticity Index [%] of the sample to plot; omitted if None.
        label: Legend label for the sample marker.

    Returns:
        A Plotly Figure object ready for st.plotly_chart().
    """
    ll_range = np.linspace(0, 100, 300)

    fig = go.Figure()

    # A-line: PI = 0.73(LL - 20) — separates clay (above) from silt (below)
    a_line_pi = 0.73 * (ll_range - 20)
    fig.add_trace(go.Scatter(
        x=ll_range, y=np.maximum(a_line_pi, 0),
        mode="lines", name="A-line",
        line=dict(color="#8a9e85", width=1.5, dash="solid"),
    ))

    # U-line: PI = 0.9(LL - 8) — empirical upper boundary; no natural soil plots above it
    u_line_pi = 0.9 * (ll_range - 8)
    fig.add_trace(go.Scatter(
        x=ll_range, y=np.maximum(u_line_pi, 0),
        mode="lines", name="U-line",
        line=dict(color="#c8b89a", width=1.5, dash="dash"),
    ))

    # Plasticity chart zone labels (rendered at fixed coordinates, low opacity)
    zone_annotations = [
        dict(x=69, y=45, text="CH", font=dict(color="#5a4f42", size=13)),
        dict(x=69, y=30, text="MH-OH", font=dict(color="#5a4f42", size=13)),
        dict(x=32, y=15, text="CL", font=dict(color="#5a4f42", size=13)),
        dict(x=16.5, y=2, text="ML", font=dict(color="#5a4f42", size=13)),
        dict(x=40.5, y=10, text="ML-OL", font=dict(color="#5a4f42", size=13)),
        dict(x=20.5, y=5.5, text="CL-ML", font=dict(color="#5a4f42", size=13)),
    ]
    for ann in zone_annotations:
        fig.add_annotation(
            x=ann["x"], y=ann["y"], text=ann["text"],
            showarrow=False, font=ann["font"],
            opacity=0.6,
        )

    # CL-ML hatched zone: bounded by A-line (top), PI=4 (bottom), and the U-line (left);
    # the four corner coordinates are computed from the intersection of these boundaries
    fig.add_trace(go.Scatter(
        x=[12.44, 25.48, 29.58, 15.78, 12.44],
        y=[4, 4, 7, 7, 4],
        fill="toself",
        fillcolor="rgba(180, 160, 130, 0.25)",
        line=dict(color="rgba(180, 160, 130, 0.6)", width=1, dash="dot"),
        mode="lines",
        name="CL-ML zone",
        showlegend=False,
        hoverinfo="skip",
    ))

    # LL = 50 divider — separates low plasticity (L) from high plasticity (H) soils
    fig.add_shape(type="line", x0=50, x1=50, y0=0, y1=60,
                  line=dict(color="#c8b89a", width=1, dash="dot"))

    # Sample marker — rendered only when both LL and PI are provided
    if ll is not None and pi is not None:
        fig.add_trace(go.Scatter(
            x=[ll], y=[pi],
            mode="markers+text",
            name=f"{label}  (LL={ll:.1f}, PI={pi:.1f})",
            marker=dict(size=12, color="#D46A3C", symbol="star",
                        line=dict(color="#2D5A27", width=1)),
            text=[f"  {label}"], textposition="top right",
            textfont=dict(color="#D46A3C", size=13),
        ))

    fig.update_layout(
        **{**PLOTLY_LAYOUT, "margin": dict(l=60, r=30, t=80, b=60)},
        title=dict(
            text="Casagrande Plasticity Chart",
            font=dict(size=17, color="#2c2c2c"),
            y=0.95,
            yanchor="top",
        ),
        xaxis=dict(
            **AXIS_STYLE,
            title="Liquid Limit (%)",
            range=[0, 100]
        ),
        yaxis=dict(
            **AXIS_STYLE,
            title="Plasticity Index (%)",
            range=[0, 70]
        ),
        legend=dict(bgcolor="#ffffff", bordercolor="#ddd8cc", borderwidth=1, font=dict(size=13)),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Result display helpers
# ─────────────────────────────────────────────────────────────────────────────

def show_classification_result(result, label=""):
    """
    Renders the USCS classification result as a styled card (on success) or
    a list of error banners (on failure). An optional section label is shown above.

    Args:
        result: The classification result dict returned by sc.classify_uscs().
        label:  Optional section heading string; omitted if empty.
    """
    if label:
        st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)

    if result["error"]:
        # Render each error message as a red-bordered note banner
        for note in result["notes"]:
            st.markdown(f'<div class="note-error">✗ {note}</div>', unsafe_allow_html=True)
    else:
        # Render the group symbol, name, and category in a green-bordered result card
        st.markdown(f"""
        <div class="result-card">
            <div class="result-symbol">{result['group_symbol']}</div>
            <div class="result-name">{result['group_name']}</div>
            <div class="result-category">{result['category']}</div>
        </div>
        """, unsafe_allow_html=True)
        # Render any informational notes (e.g. dual symbol warnings) below the card
        for note in result["notes"]:
            st.markdown(f'<div class="note-info">ⓘ {note}</div>', unsafe_allow_html=True)


def show_properties(properties):
    """
    Renders computed geotechnical properties as a row of styled property boxes.
    Shows an info message if no sample data was provided.

    Args:
        properties: Dict of property name → float value, or None.
    """
    if not properties:
        st.info("No sample data sheet provided — soil properties not computed.")
        return

    st.markdown('<div class="section-label">Computed Soil Properties</div>', unsafe_allow_html=True)
    items = [(k, v) for k, v in properties.items() if v is not None]
    if not items:
        st.write("No properties computed.")
        return

    # Cap at 4 columns per row; wrap by cycling the column index with modulo
    cols = st.columns(min(len(items), 4), gap="medium")
    for i, (key, val) in enumerate(items):
        with cols[i % 4]:
            # Replace square brackets with parentheses for cleaner display in HTML
            disp_key = key.replace("[", "(").replace("]", ")")
            disp_val = f"{val:.3f}" if isinstance(val, float) else str(val)
            st.markdown(f"""
            <div class="prop-box">
                <div class="prop-label">{disp_key}</div>
                <div class="prop-value">{disp_val}</div>
            </div>
            """, unsafe_allow_html=True)


def show_gradation_metrics(D10, D30, D60, Cu, Cc):
    """
    Renders D10, D30, D60, Cu, and Cc as a fixed row of five property boxes.
    Displays 'N/A' for any value that could not be determined.

    Args:
        D10, D30, D60: Characteristic diameters [mm], or None.
        Cu, Cc:        Uniformity and curvature coefficients, or None.
    """
    st.markdown('<div class="section-label">Gradation Parameters</div>', unsafe_allow_html=True)
    metrics = [
        ("D₁₀ (mm)", D10), ("D₃₀ (mm)", D30), ("D₆₀ (mm)", D60),
        ("Cᵤ", Cu), ("Cᶜ", Cc),
    ]
    cols = st.columns(5)
    for col, (label, val) in zip(cols, metrics):
        with col:
            display = f"{val:.4f}" if val is not None else "N/A"
            st.markdown(f"""
            <div class="prop-box">
                <div class="prop-label" style="font-size: 0.82rem;">{label}</div>
                <div class="prop-value">{display}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Excel export
# ─────────────────────────────────────────────────────────────────────────────

def build_excel_export(results: dict) -> bytes:
    """
    Serialises all processed tables to a multi-sheet Excel workbook in memory.

    Dict-type entries are converted to two-column (Description / Value) sheets;
    DataFrame entries are written as-is. None values and empty DataFrames are
    skipped. Sheet names are truncated to 31 characters to satisfy Excel limits.

    Args:
        results: Dict mapping sheet name strings to DataFrames or dicts.

    Returns:
        The workbook as a raw bytes object suitable for st.download_button().
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet_name, data in results.items():
            if data is None:
                continue
            if isinstance(data, dict):
                # Convert scalar metadata dicts to a two-column table for readability
                df = pd.DataFrame({
                    "Description": list(data.keys()),
                    "Value": list(data.values()),
                })
            elif isinstance(data, pd.DataFrame) and not data.empty:
                df = data
            else:
                continue
            # Excel sheet names are limited to 31 characters
            safe_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_name, index=False)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# UI — Sidebar inputs
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🪨 Soil Classification")
    st.markdown(
        '<div style="font-family: Plus Jakarta Sans, sans-serif; font-size: 0.7rem; color: #88A47C; letter-spacing: 2px; text-transform: uppercase; font-weight: 500;">USCS · ASTM D2487</div>',
        unsafe_allow_html=True
    )
    st.divider()

    uploaded_file = st.file_uploader("Excel Data File", type=["xlsx"])

    test_type = st.selectbox(
        "Test Type",
        ["Sieve Analysis", "Hydrometer Analysis", "Atterberg Limits"],
    )

    st.divider()
    st.markdown('<div class="section-label">Sheet Names</div>', unsafe_allow_html=True)

    # Render only the sheet name inputs relevant to the selected test type
    sheets = {}

    if test_type == "Sieve Analysis":
        sheets["sieve_sheet"] = st.text_input("Sieve Analysis Sheet")
        sheets["data_sheet"] = st.text_input("Sample Data Sheet (optional)")

    elif test_type == "Hydrometer Analysis":
        sheets["sieve_sheet"] = st.text_input("Sieve Analysis Sheet")
        sheets["hydrometer_sheet"] = st.text_input("Hydrometer Analysis Sheet")
        sheets["data_sheet"] = st.text_input("Sample Data Sheet (optional)")

    elif test_type == "Atterberg Limits":
        sheets["atterberg_sheet"] = st.text_input("Atterberg Limits Sheet")

    st.divider()
    run_button = st.button("▶  RUN ANALYSIS", use_container_width=True)

# Normalise any "none" / blank optional sheet entries to None so downstream
# helpers can treat them consistently with a simple truthiness check
for k in sheets:
    if sheets[k] and sheets[k].strip().lower() in ("", "none"):
        sheets[k] = None

# ─────────────────────────────────────────────────────────────────────────────
# Main panel — header
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("# Soil Classification System")
st.markdown(
    '<div style="font-family: Plus Jakarta Sans, sans-serif; font-size: 0.85rem; color: #D46A3C; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 1.5rem; font-weight: 600;">Unified Soil Classification System · ASTM D2487</div>',
    unsafe_allow_html=True
)

# Gate rendering on file upload and run button — st.stop() halts execution cleanly
if not uploaded_file:
    st.info("Upload an Excel file and configure the test in the sidebar to begin.")
    st.stop()

if not run_button:
    st.info("Configure the test in the sidebar and click **▶ RUN ANALYSIS**.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────────────────────────────────────────

# Wrap the uploaded file in BytesIO so it can be read multiple times by pandas
file_bytes = io.BytesIO(uploaded_file.read())
export_tables = {}  # Accumulates processed DataFrames/dicts for Excel export

try:
    # ── Sieve Analysis ────────────────────────────────────────────────────────
    if test_type == "Sieve Analysis":

        # Read the three stacked tables; Experimental Mass has no header row
        tables = dr.read_tables(
            file_bytes, sheets["sieve_sheet"],
            ['Experimental Mass', 'Coarse Portion', 'Fine Portion'],
            has_header=[False, True, True],
        )
        sample_data = safe_read_sample_data(file_bytes, sheets.get("data_sheet"))

        # Unpack the two key mass measurements from the Experimental Mass table
        exp_mass = dict(zip(tables['Experimental Mass'].iloc[:, 0], tables['Experimental Mass'].iloc[:, 1]))
        initial_total_weight = exp_mass['Initial Total Weight [g]']
        fines_weight = exp_mass['Fines Total Weight Before Wash [g]']

        # Compute percent retained / passing for coarse and fine fractions
        coarse = sa_sieve.process_coarse(tables['Coarse Portion'], initial_total_weight)
        fine = sa_sieve.process_fine(tables['Fine Portion'], tables['Coarse Portion'], fines_weight)
        full_data = sa_sieve.combine_data(coarse, fine)

        D10, D30, D60, Cu, Cc = safe_compute_cu_cc(full_data)
        properties = sp.compute_properties(sample_data) if sample_data else None

        # Extract the key sieve fractions used for USCS classification and display
        pf = fine[fine['Sieve Size [mm]'] == 0.075]['% Passing'].values[0]  # % fines (No. 200)
        pcr = coarse[coarse['Sieve Size [mm]'] == 4.75]['% Retained'].values[0]  # % gravel (No. 4)
        pct_sand = 100 - pcr - pf  # Remainder after gravel and fines

        result = sc.classify_uscs(
            percent_fines=pf,
            percent_coarse_retained_no4=pcr,
            Cu=Cu, Cc=Cc,
            LL=sample_data.get('Liquid Limit [-]') if sample_data else None,
            PL=sample_data.get('Plastic Limit [-]') if sample_data else None,
        )

        # Register tables for Excel export
        export_tables["Coarse Sieve"] = coarse
        export_tables["Fine Sieve"] = fine
        export_tables["Sample Properties"] = properties if properties else None

        # ── Display ──
        tab_class, tab_curve, tab_props, tab_tables, tab_export = st.tabs([
            "Classification", "Gradation Curve", "Soil Properties", "Data Tables", "Export"
        ])

        with tab_class:
            show_classification_result(result, label="USCS Classification")
            show_gradation_metrics(D10, D30, D60, Cu, Cc)
            # Gravel / Sand / Fines breakdown boxes
            st.markdown('<div class="section-label">Key Values</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(
                    f'<div class="prop-box"><div class="prop-label">% Gravel</div><div class="prop-value">{pcr:.2f}%</div></div>',
                    unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div class="prop-box"><div class="prop-label">% Sand</div><div class="prop-value">{pct_sand:.2f}%</div></div>',
                    unsafe_allow_html=True)
            with c3:
                st.markdown(
                    f'<div class="prop-box"><div class="prop-label">% Fines</div><div class="prop-value">{pf:.2f}%</div></div>',
                    unsafe_allow_html=True)

        with tab_curve:
            st.plotly_chart(
                plot_gradation_curve(full_data, D10, D30, D60, title=f"Gradation Curve — {sheets['sieve_sheet']}"),
                use_container_width=True,
            )

        with tab_props:
            show_properties(properties)

        with tab_tables:
            # Rename columns to replace square brackets with parentheses for display
            st.markdown('<div class="section-label">Coarse Sieve Analysis</div>', unsafe_allow_html=True)
            st.table(coarse.rename(columns={
                "Sieve Size [mm]": "Sieve Size (mm)",
                "Non-Cumulative Weight [g]": "Non-Cumulative Weight (g)",
                "Cumulative Weight [g]": "Cumulative Weight (g)",
            }))
            st.markdown('<div class="section-label">Fine Sieve Analysis</div>', unsafe_allow_html=True)
            st.table(fine.rename(columns={
                "Sieve Size [mm]": "Sieve Size (mm)",
                "Non-Cumulative Weight [g]": "Non-Cumulative Weight (g)",
                "Cumulative Weight [g]": "Cumulative Weight (g)",
            }))

        with tab_export:
            st.download_button(
                label="🡇 Download Processed Tables (.xlsx)",
                data=build_excel_export(export_tables),
                file_name=f"{sheets['sieve_sheet']}_processed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ── Hydrometer Analysis ───────────────────────────────────────────────────
    elif test_type == "Hydrometer Analysis":

        # Read pre- and post-hydrometer sieve tables from the sieve sheet
        tables = dr.read_tables(
            file_bytes, sheets["sieve_sheet"],
            ['Experimental Mass', 'Sieve Analysis Before Hydrometer Testing',
             'Sieve Analysis After Hydrometer Testing'],
            has_header=[False, True, True],
        )
        # Read hygroscopic moisture content, hydrometer sample metadata, and time-series readings
        hydrometer_tables = dr.read_tables(
            file_bytes, sheets["hydrometer_sheet"],
            ['Hygroscopic Moisture Content Data', 'Hydrometer Test Sample Data', 'Hydrometer Test Data'],
            has_header=[False, False, True],
        )
        sample_data = safe_read_sample_data(file_bytes, sheets.get("data_sheet"))

        exp_mass = dict(zip(tables['Experimental Mass'].iloc[:, 0], tables['Experimental Mass'].iloc[:, 1]))
        total_exp_mass = exp_mass['Initial Total Weight [g]']

        # Compute hygroscopic moisture content and the air-dried → oven-dry correction factor
        moisture_data = dict(zip(
            hydrometer_tables['Hygroscopic Moisture Content Data'].iloc[:, 0],
            hydrometer_tables['Hygroscopic Moisture Content Data'].iloc[:, 1]
        ))
        moisture_data['Mass of Air Dried Soil [g]'] = moisture_data['Air Dried Mass + Pan [g]'] - moisture_data[
            'Mass of Pan [g]']
        moisture_data['Mass of Oven Dried Soil [g]'] = moisture_data['Oven Dried Mass + Pan [g]'] - moisture_data[
            'Mass of Pan [g]']
        moisture_data['Mass of Water [g]'] = moisture_data['Mass of Air Dried Soil [g]'] - moisture_data[
            'Mass of Oven Dried Soil [g]']
        moisture_data['Hygroscopic Moisture Content [%]'] = moisture_data['Mass of Water [g]'] / moisture_data[
            'Mass of Oven Dried Soil [g]'] * 100
        moisture_data['Hygroscopic Correction Factor [-]'] = moisture_data['Mass of Oven Dried Soil [g]'] / \
                                                             moisture_data['Mass of Air Dried Soil [g]']

        hydrometer_sample = dict(zip(
            hydrometer_tables['Hydrometer Test Sample Data'].iloc[:, 0],
            hydrometer_tables['Hydrometer Test Sample Data'].iloc[:, 1]
        ))

        # Process the pre-hydrometer coarse sieve data and retrieve the 2 mm passing value;
        # this is used to scale the hydrometer sub-sample mass back to the full sample
        coarse = sa_sieve.process_coarse(tables['Sieve Analysis Before Hydrometer Testing'], total_exp_mass)
        pct_passing_2mm = coarse.loc[coarse['Sieve Size [mm]'] == 2, '% Passing'].values[0]

        # Derive the oven-dry tested mass: apply hygroscopic correction, then scale to full sample
        hydrometer_sample['Tested Mass [g]'] = round(
            (moisture_data['Hygroscopic Correction Factor [-]'] * hydrometer_sample['Total Sample Mass [g]'])
            / pct_passing_2mm * 100,
            2
        )

        # Process the post-hydrometer fine sieve data aligned to the coarse curve
        fine = sa_sieve.process_fine(tables['Sieve Analysis After Hydrometer Testing'], coarse,
                                     hydrometer_sample['Tested Mass [g]'])
        pct_passing_75um = fine.loc[fine['Sieve Size [mm]'] == 0.075, '% Passing'].values[0]

        # Run the hydrometer analysis to compute equivalent particle diameters and percent finer
        hydrometer_data = sa_hydrometer.process(
            test_data=hydrometer_tables['Hydrometer Test Data'],
            sample_data=hydrometer_sample,
            percent_passing_75um=pct_passing_75um,
        )

        full_data = sa_sieve.combine_data(coarse, fine)
        D10, D30, D60, Cu, Cc = safe_compute_cu_cc(full_data)
        properties = sp.compute_properties(sample_data) if sample_data else None

        pcr = coarse[coarse['Sieve Size [mm]'] == 4.75]['% Retained'].values[0]
        result = sc.classify_uscs(
            percent_fines=pct_passing_75um,
            percent_coarse_retained_no4=pcr,
            Cu=Cu, Cc=Cc,
            LL=sample_data.get('Liquid Limit [-]') if sample_data else None,
            PL=sample_data.get('Plastic Limit [-]') if sample_data else None,
        )

        # Register tables for Excel export
        export_tables["Coarse Sieve"] = coarse
        export_tables["Fine Sieve"] = fine
        export_tables["Hygroscopic Moisture Content"] = moisture_data
        export_tables["Hydrometer Sample"] = hydrometer_sample
        export_tables["Hydrometer Data"] = hydrometer_data if isinstance(hydrometer_data, pd.DataFrame) else None
        export_tables["Sample Properties"] = properties if properties else None

        # ── Display ──
        tab_class, tab_curve, tab_props, tab_tables, tab_export = st.tabs([
            "Classification", "Gradation Curve", "Soil Properties", "Data Tables", "Export"
        ])

        with tab_class:
            show_classification_result(result, label="USCS Classification")
            show_gradation_metrics(D10, D30, D60, Cu, Cc)
            st.markdown('<div class="section-label">Key Values</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f'<div class="prop-box"><div class="prop-label">% Passing 2 mm</div><div class="prop-value">{pct_passing_2mm:.2f}%</div></div>',
                    unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div class="prop-box"><div class="prop-label">% Passing 0.075 mm</div><div class="prop-value">{pct_passing_75um:.2f}%</div></div>',
                    unsafe_allow_html=True)

        with tab_curve:
            st.plotly_chart(
                plot_gradation_curve(full_data, D10, D30, D60, title=f"Gradation Curve — {sheets['sieve_sheet']}"),
                use_container_width=True,
            )

        with tab_props:
            show_properties(properties)

        with tab_tables:
            st.markdown('<div class="section-label">Hygroscopic Moisture Content Data</div>', unsafe_allow_html=True)
            # Replace square brackets with parentheses before rendering in HTML table
            disp_moisture = {
                k.replace("[", "(").replace("]", ")"): v
                for k, v in moisture_data.items()
            }
            st.table(pd.DataFrame({
                "Description": list(disp_moisture.keys()),
                "Value": list(disp_moisture.values()),
            }))

            st.markdown('<div class="section-label">Hydrometer Test Sample Data</div>', unsafe_allow_html=True)
            disp_hydrometer_sample = {
                k.replace("[", "(").replace("]", ")"): v
                for k, v in hydrometer_sample.items()
            }
            st.table(pd.DataFrame({
                "Description": list(disp_hydrometer_sample.keys()),
                "Value": list(disp_hydrometer_sample.values()),
            }))

            if isinstance(hydrometer_data, pd.DataFrame):
                # Split the hydrometer DataFrame into raw measurements and calculated values
                # to avoid presenting a very wide table in a single view
                raw_cols = [
                    "Date", "Time", "Elapsed Time [min]", "Hydrometer Reading [mm]",
                    "Temperature [°C]", "Meniscus Corrected Hydrometer Reading [mm]",
                ]
                calc_cols = [
                    "Date", "Time", "Effective Depth [cm]", "K [-]",
                    "Equivalent Particle Diameter [mm]", "Temperature Correction Factor [-]",
                    "Unit Weight Correction Factor [-]", "Corrected Hydrometer Reading [g/L]",
                    "Percent Finer", "Percent Finer Adj.",
                ]

                st.markdown('<div class="section-label">Hydrometer Test Results (Raw Measurements)</div>',
                            unsafe_allow_html=True)
                st.table(hydrometer_data[raw_cols].rename(columns={
                    "Elapsed Time [min]": "Elapsed Time (min)",
                    "Hydrometer Reading [mm]": "Hydro Reading (mm)",
                    "Temperature [°C]": "Temp. (°C)",
                    "Meniscus Corrected Hydrometer Reading [mm]": "Ra (mm)",
                }))

                st.markdown('<div class="section-label">Hydrometer Test Results (Calculated Values)</div>',
                            unsafe_allow_html=True)
                st.table(hydrometer_data[calc_cols].rename(columns={
                    "Effective Depth [cm]": "L (cm)",
                    "K [-]": "K (-)",
                    "Equivalent Particle Diameter [mm]": "D (mm)",
                    "Temperature Correction Factor [-]": "CT (-)",
                    "Unit Weight Correction Factor [-]": "A (-)",
                    "Corrected Hydrometer Reading [g/L]": "Rc (g/L)",
                    "Percent Finer": "% Finer (P)",
                    "Percent Finer Adj.": "% Finer (PA)",
                }))
            else:
                st.write(hydrometer_data)

            st.markdown('<div class="section-label">Coarse Sieve Analysis</div>', unsafe_allow_html=True)
            st.table(coarse.rename(columns={
                "Sieve Size [mm]": "Sieve Size (mm)",
                "Non-Cumulative Weight [g]": "Non-Cumulative Weight (g)",
                "Cumulative Weight [g]": "Cumulative Weight (g)",
            }))
            st.markdown('<div class="section-label">Fine Sieve Analysis</div>', unsafe_allow_html=True)
            st.table(fine.rename(columns={
                "Sieve Size [mm]": "Sieve Size (mm)",
                "Non-Cumulative Weight [g]": "Non-Cumulative Weight (g)",
                "Cumulative Weight [g]": "Cumulative Weight (g)",
            }))

        with tab_export:
            st.download_button(
                label="🡇 Download Processed Tables (.xlsx)",
                data=build_excel_export(export_tables),
                file_name=f"{sheets['hydrometer_sheet']}_processed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ── Atterberg Limits ──────────────────────────────────────────────────────
    elif test_type == "Atterberg Limits":

        atterberg_tables = dr.read_tables(
            file_bytes, sheets["atterberg_sheet"],
            ['Liquid Limit', 'Plastic Limit'],
            has_header=[True, True],
        )

        # Fit the semi-log flow curve and compute LL, PL, and PI
        ll_data, pl_data, ll, pl, pi = sa_atterberg.process(
            atterberg_tables['Liquid Limit'],
            atterberg_tables['Plastic Limit'],
        )

        # Atterberg limits are only run on fine-grained soils, so percent_fines = 100
        # routes directly to the fine-grained classification branch in classify_uscs
        result = sc.classify_uscs(
            percent_fines=100,
            LL=ll, PL=pl,
        )

        export_tables["Liquid Limit Data"] = ll_data if isinstance(ll_data, pd.DataFrame) else None
        export_tables["Plastic Limit Data"] = pl_data if isinstance(pl_data, pd.DataFrame) else None

        # ── Display ──
        tab_class, tab_chart, tab_tables, tab_export = st.tabs([
            "Classification", "Casagrande Chart", "Data Tables", "Export"
        ])

        with tab_class:
            show_classification_result(result, label="USCS Classification")
            # Display the three computed Atterberg limit values side by side
            st.markdown('<div class="section-label">Atterberg Limits</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            for col, label, val in [(c1, "Liquid Limit (%)", ll), (c2, "Plastic Limit (%)", pl),
                                    (c3, "Plasticity Index (%)", pi)]:
                with col:
                    st.markdown(
                        f'<div class="prop-box"><div class="prop-label">{label}</div><div class="prop-value">{val:.1f}</div></div>',
                        unsafe_allow_html=True
                    )

        with tab_chart:
            st.plotly_chart(
                plot_casagrande(ll=ll, pi=pi, label=sheets["atterberg_sheet"]),
                use_container_width=True,
            )

        with tab_tables:
            st.markdown('<div class="section-label">Liquid Limit Test Data</div>', unsafe_allow_html=True)
            if isinstance(ll_data, pd.DataFrame):
                st.table(ll_data.rename(columns={
                    "Trial Number": "Trial No.",
                    "Number of Blows": "No. of Blows",
                    "Tin Number": "Tin No.",
                    "Mass of Tin + Wet Soil [g]": "Total Wet Wt. (g)",
                    "Mass of Tin + Dry Soil [g]": "Total Dry Wt. (g)",
                    "Mass of Tin [g]": "Tin Wt. (g)",
                    "Mass of Water [g]": "Water Wt. (g)",
                    "Mass of Dry Soil [g]": "Dry Soil Wt. (g)"
                }))
            st.markdown('<div class="section-label">Plastic Limit Test Data</div>', unsafe_allow_html=True)
            if isinstance(pl_data, pd.DataFrame):
                st.table(pl_data.rename(columns={
                    "Trial Number": "Trial No.",
                    "Tin Number": "Tin No.",
                    "Mass of Tin + Wet Soil [g]": "Total Wet Wt. (g)",
                    "Mass of Tin + Dry Soil [g]": "Total Dry Wt. (g)",
                    "Mass of Tin [g]": "Tin Wt. (g)",
                    "Mass of Water [g]": "Water Wt. (g)",
                    "Mass of Dry Soil [g]": "Dry Soil Wt. (g)"
                }))

        with tab_export:
            st.download_button(
                label="🡇  Download Processed Tables (.xlsx)",
                data=build_excel_export(export_tables),
                file_name=f"{sheets['atterberg_sheet']}_processed.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# Catch-all: display the error and full traceback in the Streamlit UI rather
# than crashing silently or showing a generic Streamlit error page
except Exception as e:
    st.error(f"An error occurred during analysis: {e}")
    st.exception(e)