"""Page 4 — Vendor Performance"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_all_data, get_vendor_performance

WHITE = '#FFFFFF'
TEXT_DARK = '#0F172A'
TEXT_AXIS = '#334155'
TEXT_MUTED = '#475569'
GRID = '#E2E8F0'
STEEL = '#1E40AF'
ORANGE = '#EA580C'
GREEN = '#059669'
RED = '#DC2626'
AMBER = '#D97706'


def axis_style():
    return dict(
        color=TEXT_AXIS,
        tickfont=dict(size=12, color=TEXT_AXIS, family='Inter'),
        title_font=dict(size=12, color=TEXT_DARK, family='Inter'),
        linecolor='#CBD5E1', linewidth=1
    )


def short_name(name, length=18):
    """Truncate long vendor names"""
    return name if len(name) <= length else name[:length-2] + '..'


def show_page():
    data = load_all_data()
    vp = get_vendor_performance(data)
    df_v = data['vendor']

    st.markdown("<div class='page-title'>Vendor Performance</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Composite scoring & quality analysis</div>",
                unsafe_allow_html=True)

    best = vp.iloc[0]
    worst = vp.iloc[-1]
    g = len(vp[vp['Performance_Flag'] == 'GREEN'])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Top Performer",
                  best['Vendor_Name'].split()[0],
                  f"Score {best['Composite_Score']:.0f}")
    with c2:
        st.metric("Needs Review",
                  worst['Vendor_Name'].split()[0],
                  f"Score {worst['Composite_Score']:.0f}",
                  delta_color="inverse")
    with c3:
        st.metric("Avg Lead Time", f"{df_v['Lead_Time'].mean():.0f} days")
    with c4:
        st.metric("Preferred Vendors", f"{g} / {len(vp)}")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='chart-card'>
        <div class='chart-title'>Vendor Scorecard</div>
        <div class='chart-subtitle'>Composite score: 50% On-Time + 30% Quality + 20% Price</div>
    </div>
    """, unsafe_allow_html=True)

    # Format scorecard properly
    sc = vp[['Vendor_Name','OnTime_Pct','Defect_Rate','Avg_Lead_Time',
             'Total_Volume','Composite_Score','Performance_Flag']].copy()
    sc['OnTime_Pct'] = sc['OnTime_Pct'].apply(lambda x: f"{x:.1f}%")
    sc['Defect_Rate'] = sc['Defect_Rate'].apply(lambda x: f"{x:.2f}%")
    sc['Avg_Lead_Time'] = sc['Avg_Lead_Time'].apply(lambda x: f"{x:.1f} days")
    sc['Total_Volume'] = sc['Total_Volume'].apply(lambda x: f"{x:,}")
    sc['Composite_Score'] = sc['Composite_Score'].apply(lambda x: f"{x:.1f}")
    sc['Performance_Flag'] = sc['Performance_Flag'].map({
        'GREEN': 'Preferred', 'YELLOW': 'Approved', 'RED': 'Under Review'})

    sc.columns = ['Vendor','On-Time %','Defect %','Lead Time','Volume','Score','Status']

    def cstatus(val):
        if val == 'Preferred':
            return 'background-color:#D1FAE5;color:#065F46;font-weight:600'
        elif val == 'Approved':
            return 'background-color:#FEF3C7;color:#92400E;font-weight:600'
        return 'background-color:#FEE2E2;color:#991B1B;font-weight:600'

    st.dataframe(sc.style.map(cstatus, subset=['Status']),
                 use_container_width=True, height=380, hide_index=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>On-Time Delivery Rate</div>
            <div class='chart-subtitle'>Color-coded performance</div>
        </div>
        """, unsafe_allow_html=True)

        vs = vp.sort_values('OnTime_Pct', ascending=True).copy()
        vs['Short_Name'] = vs['Vendor_Name'].apply(lambda x: short_name(x, 16))
        bc = [RED if x < 70 else AMBER if x < 85 else GREEN for x in vs['OnTime_Pct']]

        fig1 = go.Figure(go.Bar(
            x=vs['OnTime_Pct'], y=vs['Short_Name'], orientation='h',
            marker=dict(color=bc, cornerradius=4),
            text=[f'{v:.0f}%' for v in vs['OnTime_Pct']],
            textposition='outside',
            textfont=dict(color=TEXT_DARK, size=12, family='Inter'),
            customdata=vs['Vendor_Name'],
            hovertemplate='<b>%{customdata}</b><br>On-Time: %{x:.1f}%<extra></extra>'))
        fig1.add_vline(x=85, line_dash="dash", line_color=GREEN, line_width=1, opacity=0.6)
        fig1.add_vline(x=70, line_dash="dash", line_color=RED, line_width=1, opacity=0.6)
        fig1.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_AXIS, size=12),
            xaxis=dict(showgrid=True, gridcolor=GRID, range=[0, 110], **axis_style()),
            yaxis=dict(showgrid=False, **axis_style()),
            height=400, margin=dict(l=10, r=50, t=10, b=10), showlegend=False)
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Lead Time vs Defect Rate</div>
            <div class='chart-subtitle'>Bubble size = order volume</div>
        </div>
        """, unsafe_allow_html=True)

        fc = {'GREEN': GREEN, 'YELLOW': AMBER, 'RED': RED}
        fig2 = go.Figure()
        for flag, color in fc.items():
            fd = vp[vp['Performance_Flag'] == flag].copy()
            if len(fd) > 0:
                fd['Short'] = fd['Vendor_Name'].apply(lambda x: short_name(x, 10))
                fig2.add_trace(go.Scatter(
                    x=fd['Avg_Lead_Time'], y=fd['Defect_Rate'],
                    mode='markers+text', name=flag.title(),
                    marker=dict(
                        size=fd['Total_Volume']/fd['Total_Volume'].max()*30+12,
                        color=color, opacity=0.85,
                        line=dict(color='white', width=2)),
                    text=fd['Short'],
                    textposition='top center',
                    textfont=dict(color=TEXT_DARK, size=10, family='Inter'),
                    customdata=fd['Vendor_Name'],
                    hovertemplate='<b>%{customdata}</b><br>Lead: %{x:.1f} days<br>Defect: %{y:.2f}%<extra></extra>'))
        fig2.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_AXIS, size=12),
            xaxis=dict(showgrid=True, gridcolor=GRID, title='Lead Time (days)', **axis_style()),
            yaxis=dict(showgrid=True, gridcolor=GRID, title='Defect Rate %', **axis_style()),
            legend=dict(bgcolor=WHITE, font=dict(color=TEXT_DARK, size=12)),
            height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})