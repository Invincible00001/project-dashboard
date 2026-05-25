# ==========================================================
# STREAMLIT PROJECT DASHBOARD GENERATOR
# ==========================================================
#
# INSTALL:
# pip install streamlit pandas plotly openpyxl
#
# RUN:
# streamlit run app.py
#
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Project Timeline Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.main {
    background-color: #F1F5F9;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.dashboard-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
}

.dashboard-subtitle {
    color: #CBD5E1;
    font-size: 16px;
}

.metric-card {
    background: white;
    padding: 24px;
    border-radius: 20px;
    box-shadow: 0px 6px 24px rgba(0,0,0,0.08);
    text-align: center;
}

.metric-value {
    font-size: 36px;
    font-weight: 700;
    color: #0F172A;
}

.metric-label {
    color: #64748B;
    margin-top: 8px;
}

.header-container {
    background: linear-gradient(135deg,#0F172A,#1E293B);
    padding: 40px;
    border-radius: 24px;
    margin-bottom: 30px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="header-container">
    <div class="dashboard-title">
        2026 Project Timeline Dashboard
    </div>

    <div class="dashboard-subtitle">
        Interactive Executive Program Visualization
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# FILE UPLOAD
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx", "xls"]
)

# ==========================================================
# PROCESS ONLY AFTER UPLOAD
# ==========================================================

if uploaded_file:

    # ======================================================
    # READ EXCEL
    # ======================================================

    df = pd.read_excel(uploaded_file)

    # ======================================================
    # COLUMN DETECTION
    # ======================================================

    def find_column(columns, keywords):

        for col in columns:
            lower = col.lower()

            for key in keywords:
                if key in lower:
                    return col

        return None

    pidtc_col = find_column(df.columns, ["pidtc", "project"])
    type_col = find_column(df.columns, ["type"])
    stage_col = find_column(df.columns, ["stage"])
    experiment_col = find_column(df.columns, ["experiment"])
    start_col = find_column(df.columns, ["start"])
    end_col = find_column(df.columns, ["end"])

    samples_col = find_column(df.columns, ["sample"])
    plants_col = find_column(df.columns, ["plant"])
    datapoints_col = find_column(df.columns, ["datapoint"])

    # ======================================================
    # VALIDATION
    # ======================================================

    required = [pidtc_col, start_col, end_col]

    if any(v is None for v in required):

        st.error("""
        Missing required columns.

        Required:
        - PIDTC / Project
        - Start Date
        - End Date
        """)

        st.stop()

    # ======================================================
    # DATE CLEANING
    # ======================================================

    df[start_col] = pd.to_datetime(df[start_col])
    df[end_col] = pd.to_datetime(df[end_col])

    # ======================================================
    # PHASE LABEL
    # ======================================================

    def phase_label(row):

        stage = str(row[stage_col]) if stage_col else ""
        exp = str(row[experiment_col]) if experiment_col else ""

        if stage and exp:
            return f"{stage} | {exp}"

        if stage:
            return stage

        return exp

    df["PhaseLabel"] = df.apply(phase_label, axis=1)

    # ======================================================
    # SUMMARY METRICS
    # ======================================================

    today = pd.Timestamp.today()

    total_projects = df[pidtc_col].nunique()

    active_projects = df[
        (df[start_col] <= today) &
        (df[end_col] >= today)
    ][pidtc_col].nunique()

    completed_projects = df[
        df[end_col] < today
    ][pidtc_col].nunique()

    total_samples = (
        int(df[samples_col].sum())
        if samples_col else "N/A"
    )

    total_plants = (
        int(df[plants_col].sum())
        if plants_col else "N/A"
    )

    total_datapoints = (
        int(df[datapoints_col].sum())
        if datapoints_col else "N/A"
    )

    # ======================================================
    # METRICS UI
    # ======================================================

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    metrics = [
        ("Total Projects", total_projects),
        ("Active", active_projects),
        ("Completed", completed_projects),
        ("Samples", total_samples),
        ("Plants", total_plants),
        ("Datapoints", total_datapoints)
    ]

    for col, (label, value) in zip(
        [c1, c2, c3, c4, c5, c6],
        metrics
    ):

        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================================================
    # COLORS
    # ======================================================

    palette = [
        "#2563EB",
        "#7C3AED",
        "#EC4899",
        "#F97316",
        "#10B981",
        "#DC2626",
        "#0891B2",
        "#CA8A04",
    ]

    color_map = {}

    if type_col:

        unique_types = df[type_col].dropna().unique()

        for i, t in enumerate(unique_types):
            color_map[t] = palette[i % len(palette)]

    # ======================================================
    # GANTT CHART
    # ======================================================

    fig = px.timeline(
        df,
        x_start=start_col,
        x_end=end_col,
        y=pidtc_col,
        color=type_col if type_col else pidtc_col,
        text="PhaseLabel",
        color_discrete_map=color_map,
        hover_data={
            pidtc_col: True,
            start_col: True,
            end_col: True,
            stage_col: True if stage_col else False,
            experiment_col: True if experiment_col else False,
        }
    )

    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_yaxes(
        autorange="reversed"
    )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        marker_line_color="white",
        marker_line_width=1
    )

    fig.update_layout(

        height=max(900, len(df) * 55),

        paper_bgcolor="#F1F5F9",
        plot_bgcolor="white",

        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        ),

        font=dict(
            family="Segoe UI",
            size=13,
            color="#0F172A"
        ),

        xaxis=dict(
            title="Timeline",
            showgrid=True,
            gridcolor="#E2E8F0",
            dtick="M1",
            tickformat="%b\n%Y"
        ),

        yaxis=dict(
            title="Projects",
            showgrid=False
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # ======================================================
    # DISPLAY
    # ======================================================

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================================
    # DOWNLOAD HTML
    # ======================================================

    html_buffer = io.StringIO()

    fig.write_html(
        html_buffer,
        include_plotlyjs="cdn"
    )

    st.download_button(
        label="Download Interactive HTML Dashboard",
        data=html_buffer.getvalue(),
        file_name="project_dashboard.html",
        mime="text/html"
    )

else:

    st.info("""
    Upload an Excel sheet to generate the dashboard.

    Recommended columns:
    - PIDTC / Project
    - Project Type
    - Stage
    - Experiment
    - Start Date
    - End Date
    """)