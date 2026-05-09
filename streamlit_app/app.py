"""
Sarovar Enterprises — Supply Chain Analytics
Stripe/Linear Inspired | Industrial Theme | Compact Layout
"""

import streamlit as st
import sys
import os

st.set_page_config(
    page_title="Sarovar Enterprises | Supply Chain Analytics",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Hide Sidebar Completely ── */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* ── Reduce Top Padding ── */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* ── Global ── */
    html, body, .main, [data-testid="stAppViewContainer"], .stApp {
        background-color: #F9FAFB !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
        color: #0F172A;
    }

    * {
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Top Brand Bar ── */
    .brand-bar {
        background: #FFFFFF;
        padding: 12px 24px;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }
    .brand-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-logo {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #1E40AF 0%, #EA580C 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 16px;
    }
    .brand-name {
        font-size: 14px;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.2px;
        line-height: 1.2;
    }
    .brand-tag {
        font-size: 11px;
        color: #64748B;
        font-weight: 500;
        margin-top: 2px;
    }
    .brand-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .brand-meta {
        font-size: 11px;
        color: #64748B;
        font-weight: 500;
    }
    .brand-status {
        background: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    /* ── Tabs (Top Pills) ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 4px;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 13px;
        font-weight: 500;
        color: #64748B;
        padding: 8px 16px;
        border-radius: 6px;
        background: transparent;
        transition: all 0.15s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #F1F5F9;
        color: #0F172A;
    }
    .stTabs [aria-selected="true"] {
        background: #1E40AF !important;
        color: #FFFFFF !important;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 16px;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background: transparent;
    }
    .stTabs [data-baseweb="tab-border"] {
        background: transparent;
    }

        /* ── KPI Cards (Uniform Height) ── */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
        transition: all 0.2s;
        min-height: 110px !important;
        max-height: 110px !important;
        height: 110px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        overflow: hidden !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(15,23,42,0.06);
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricLabel"] p {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        margin-top: 4px;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 11px !important;
        font-weight: 500 !important;
        margin-top: 2px;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(15,23,42,0.06);
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricLabel"] p {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #64748B !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        margin-top: 4px;
    }
    [data-testid="stMetricDelta"] {
        font-size: 11px !important;
        font-weight: 500 !important;
        margin-top: 2px;
    }

    /* ── Section Header ── */
    .sec-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 20px 0 12px 0;
    }
    .sec-title {
        font-size: 13px;
        font-weight: 600;
        color: #0F172A;
        letter-spacing: -0.2px;
    }
    .sec-meta {
        font-size: 11px;
        color: #64748B;
        font-weight: 500;
    }

    /* ── Chart Container ── */
    .chart-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }
    .chart-title {
        font-size: 13px;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 12px;
        letter-spacing: -0.2px;
    }
    .chart-subtitle {
        font-size: 11px;
        color: #64748B;
        margin-bottom: 12px;
    }

    /* ── Page Title ── */
    .page-title {
        font-size: 18px;
        font-weight: 700;
        color: #0F172A;
        margin: 12px 0 4px 0;
        letter-spacing: -0.3px;
    }
    .page-subtitle {
        font-size: 12px;
        color: #64748B;
        font-weight: 500;
        margin-bottom: 16px;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] label {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stSelectbox"] > div > div {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
    }

    /* ── DataFrame ── */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        overflow: hidden;
        background: #FFFFFF;
    }

    /* ── Alert Boxes ── */
    .alert-card {
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0;
        border-left-width: 3px;
        border-left-style: solid;
        font-size: 12px;
        line-height: 1.5;
    }
    .alert-red {
        background: #FEF2F2;
        border-left-color: #DC2626;
    }
    .alert-amber {
        background: #FFFBEB;
        border-left-color: #D97706;
    }
    .alert-green {
        background: #F0FDF4;
        border-left-color: #059669;
    }
    .alert-blue {
        background: #EFF6FF;
        border-left-color: #1E40AF;
    }
    .alert-orange {
        background: #FFF7ED;
        border-left-color: #EA580C;
    }
    .alert-title {
        font-size: 12px;
        font-weight: 700;
        margin: 0 0 4px 0;
    }
    .alert-body {
        font-size: 12px;
        color: #475569;
        margin: 0;
        line-height: 1.5;
    }

    /* ── Hide Streamlit Defaults ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Dividers ── */
    hr {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Top Brand Bar ──
st.markdown("""
<div class='brand-bar'>
    <div class='brand-left'>
        <div class='brand-logo'>S</div>
        <div>
            <div class='brand-name'>SAROVAR ENTERPRISES</div>
            <div class='brand-tag'>Supply Chain Analytics Platform</div>
        </div>
    </div>
    <div class='brand-right'>
        <div class='brand-meta'>📍 Mumbai, India</div>
        <div class='brand-meta'>📅 Jan 2022 — Dec 2023</div>
        <div class='brand-status'>● LIVE</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation Tabs ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Inventory",
    "Forecasting",
    "Vendors",
    "Alerts"
])

with tab1:
    from pages.page1_executive import show_page
    show_page()

with tab2:
    from pages.page2_inventory import show_page as show_inv
    show_inv()

with tab3:
    from pages.page3_forecast import show_page as show_fc
    show_fc()

with tab4:
    from pages.page4_vendor import show_page as show_vp
    show_vp()

with tab5:
    from pages.page5_alerts import show_page as show_alerts
    show_alerts()