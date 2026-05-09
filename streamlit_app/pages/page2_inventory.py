"""Page 2 — Inventory Health"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_all_data, get_inventory_turnover

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
SLATE = '#475569'
INDIGO = '#6366F1'


def axis_style():
    return dict(
        color=TEXT_AXIS,
        tickfont=dict(size=12, color=TEXT_AXIS, family='Inter'),
        title_font=dict(size=12, color=TEXT_DARK, family='Inter'),
        linecolor='#CBD5E1', linewidth=1
    )


def show_page():
    data = load_all_data()
    df_inv = data['inventory']
    turnover = get_inventory_turnover(data)

    st.markdown("<div class='page-title'>Inventory Health</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>SKU-level stock monitoring & turnover analysis</div>",
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        sel_cat = st.selectbox("CATEGORY",
            ['All'] + sorted(df_inv['Category'].unique().tolist()))
    with c2:
        sel_wh = st.selectbox("WAREHOUSE",
            ['All'] + sorted(df_inv['Warehouse_Location'].unique().tolist()))
    with c3:
        sel_st = st.selectbox("STATUS",
            ['All', 'Stockout Risk', 'Overstock', 'Healthy'])

    filt = df_inv.copy()
    if sel_cat != 'All':
        filt = filt[filt['Category'] == sel_cat]
    if sel_wh != 'All':
        filt = filt[filt['Warehouse_Location'] == sel_wh]
    if sel_st != 'All':
        filt = filt[filt['Stock_Status'] == sel_st]

    latest = filt.sort_values('Date').groupby('SKU_ID').last().reset_index()

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total SKUs", latest['SKU_ID'].nunique())
    with c2:
        st.metric("Stockout Risk",
                  len(latest[latest['Stock_Status'] == 'Stockout Risk']),
                  delta_color="inverse")
    with c3:
        st.metric("Overstocked",
                  len(latest[latest['Stock_Status'] == 'Overstock']),
                  delta_color="inverse")
    with c4:
        st.metric("Healthy",
                  len(latest[latest['Stock_Status'] == 'Healthy']))

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='chart-card'>
        <div class='chart-title'>SKU Inventory Status</div>
        <div class='chart-subtitle'>Detailed stock levels with health indicators</div>
    </div>
    """, unsafe_allow_html=True)

    disp = latest[['SKU_ID','Product_Name','Category','Opening_Stock',
                    'Closing_Stock','Safety_Stock','Reorder_Point',
                    'Warehouse_Location','Stock_Status']].copy()
    disp['Inv. Value'] = (latest['Closing_Stock'] * latest['Unit_Cost']).apply(
        lambda x: f"₹{x:,.0f}")
    disp.columns = ['SKU ID','Product','Category','Opening','Closing',
                    'Safety','Reorder','Warehouse','Status','Value']

    def cs(val):
        if val == 'Stockout Risk':
            return 'background-color:#FEE2E2;color:#991B1B;font-weight:600'
        elif val == 'Overstock':
            return 'background-color:#FEF3C7;color:#92400E;font-weight:600'
        return 'background-color:#D1FAE5;color:#065F46;font-weight:600'

    st.dataframe(disp.style.map(cs, subset=['Status']),
                 use_container_width=True, height=320, hide_index=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Inventory Turnover by Category</div>
            <div class='chart-subtitle'>Higher ratio = faster movement</div>
        </div>
        """, unsafe_allow_html=True)

        tc = turnover.groupby('Category').agg(Avg=('Turnover_Ratio','mean')).reset_index()
        tc = tc.sort_values('Avg', ascending=True)

        fig1 = go.Figure(go.Bar(
            x=tc['Avg'], y=tc['Category'], orientation='h',
            marker=dict(color=[STEEL,INDIGO,SLATE,ORANGE,AMBER][:len(tc)], cornerradius=4),
            text=[f'{v:.1f}x' for v in tc['Avg']],
            textposition='outside',
            textfont=dict(color=TEXT_DARK, size=12, family='Inter'),
            hovertemplate='<b>%{y}</b><br>%{x:.2f}x<extra></extra>'))
        fig1.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_AXIS, size=12),
            xaxis=dict(showgrid=True, gridcolor=GRID, **axis_style()),
            yaxis=dict(showgrid=False, **axis_style()),
            height=280, margin=dict(l=10, r=60, t=10, b=10), showlegend=False)
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Opening vs Closing Stock</div>
            <div class='chart-subtitle'>Average across categories</div>
        </div>
        """, unsafe_allow_html=True)

        sc = df_inv.groupby('Category').agg(
            Opening=('Opening_Stock','mean'),
            Closing=('Closing_Stock','mean')).reset_index()

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name='Opening', x=sc['Category'], y=sc['Opening'],
                              marker=dict(color=STEEL, cornerradius=4)))
        fig2.add_trace(go.Bar(name='Closing', x=sc['Category'], y=sc['Closing'],
                              marker=dict(color=ORANGE, cornerradius=4)))
        fig2.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_AXIS, size=12),
            xaxis=dict(showgrid=False, **axis_style()),
            yaxis=dict(showgrid=True, gridcolor=GRID, **axis_style()),
            barmode='group', height=280,
            legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center',
                        bgcolor=WHITE, font=dict(color=TEXT_DARK, size=12)),
            margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    # Health Score
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    total = len(latest)
    healthy = len(latest[latest['Stock_Status'] == 'Healthy'])
    score = (healthy / total * 100) if total > 0 else 0
    sn = len(latest[latest['Stock_Status'] == 'Stockout Risk'])
    on = len(latest[latest['Stock_Status'] == 'Overstock'])

    cg, ci = st.columns([1, 2])

    with cg:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Health Score</div>
            <div class='chart-subtitle'>Overall inventory health</div>
        </div>
        """, unsafe_allow_html=True)

        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            number={'font': {'color': TEXT_DARK, 'size': 36, 'family': 'Inter'}, 'suffix': '%'},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': TEXT_AXIS,
                         'tickfont': {'color': TEXT_AXIS, 'size': 11, 'family': 'Inter'}},
                'bar': {'color': STEEL, 'thickness': 0.7},
                'bgcolor': '#F1F5F9', 'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': '#FEE2E2'},
                    {'range': [50, 75], 'color': '#FEF3C7'},
                    {'range': [75, 100], 'color': '#D1FAE5'}
                ],
                'threshold': {'line': {'color': ORANGE, 'width': 3},
                              'thickness': 0.75, 'value': 80}
            }))
        fig_g.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                            height=240, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_g, use_container_width=True, config={'displayModeBar': False})

    with ci:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Status Breakdown</div>
            <div class='chart-subtitle'>Action items by category</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='alert-card alert-green'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='color:#059669;font-weight:700;font-size:13px;'>Healthy Items</span>
                <span style='color:#0F172A;font-weight:700;font-size:13px;'>{healthy} SKUs ({healthy/max(total,1)*100:.0f}%)</span>
            </div>
        </div>
        <div class='alert-card alert-red'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='color:#DC2626;font-weight:700;font-size:13px;'>Stockout Risk</span>
                <span style='color:#0F172A;font-weight:700;font-size:13px;'>{sn} SKUs · Reorder needed</span>
            </div>
        </div>
        <div class='alert-card alert-amber'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='color:#D97706;font-weight:700;font-size:13px;'>Overstocked</span>
                <span style='color:#0F172A;font-weight:700;font-size:13px;'>{on} SKUs · Reduce procurement</span>
            </div>
        </div>
        """, unsafe_allow_html=True)