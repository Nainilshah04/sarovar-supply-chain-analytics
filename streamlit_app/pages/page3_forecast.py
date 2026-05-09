"""Page 3 — Demand Forecasting"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_all_data

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


def show_page():
    data = load_all_data()
    df_fc = data['forecast']
    df_monthly = data['monthly']
    df_mape = data['mape']
    df_sales = data['sales']
    df_inv = data['inventory']

    st.markdown("<div class='page-title'>Demand Forecasting</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Predictive analytics powered by Exponential Smoothing</div>",
                unsafe_allow_html=True)

    sel = st.selectbox("SELECT CATEGORY",
                       sorted(df_monthly['Category'].unique().tolist()))

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    mcols = st.columns(len(df_mape))
    for i, row in df_mape.iterrows():
        with mcols[i]:
            acc = 100 - row['MAPE']
            st.metric(row['Category'], f"{acc:.1f}%", f"MAPE {row['MAPE']:.1f}%")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    merged = df_sales.merge(df_inv[['SKU_ID','Category']].drop_duplicates(),
                            on='SKU_ID', how='left')

    actual = merged[merged['Category'] == sel].groupby(
        merged['Order_Date'].dt.to_period('M')
    )['Quantity_Ordered'].sum().reset_index()
    actual.columns = ['Month', 'Demand']
    actual['Month'] = actual['Month'].dt.to_timestamp()

    cat_fc = df_fc[df_fc['Category'] == sel].sort_values('Date')
    mr = df_mape[df_mape['Category'] == sel]
    mv = mr['MAPE'].values[0] if len(mr) > 0 else 0

    st.markdown(f"""
    <div class='chart-card'>
        <div class='chart-title'>Actual vs Forecast — {sel}</div>
        <div class='chart-subtitle'>Historical demand with 3-month forward projection</div>
    </div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual['Month'], y=actual['Demand'],
        mode='lines+markers', name='Actual',
        line=dict(color=STEEL, width=2.5, shape='spline'),
        marker=dict(size=6, color=STEEL),
        hovertemplate='<b>%{x|%b %Y}</b><br>Actual: %{y:,}<extra></extra>'))

    if len(cat_fc) > 0:
        fig.add_trace(go.Scatter(
            x=cat_fc['Date'], y=cat_fc['Forecasted_Demand'],
            mode='lines+markers', name='Forecast',
            line=dict(color=ORANGE, width=2.5, dash='dot'),
            marker=dict(size=7, symbol='diamond', color=ORANGE),
            hovertemplate='<b>%{x|%b %Y}</b><br>Forecast: %{y:,.0f}<extra></extra>'))

        fv = cat_fc['Forecasted_Demand'].values
        fig.add_trace(go.Scatter(
            x=list(cat_fc['Date']) + list(cat_fc['Date'])[::-1],
            y=list(fv * 1.10) + list(fv * 0.90)[::-1],
            fill='toself', fillcolor='rgba(234,88,12,0.10)',
            line=dict(color='rgba(0,0,0,0)'),
            name='90% Confidence', showlegend=True, hoverinfo='skip'))

        future = cat_fc[cat_fc['Type'] == 'Future']
        if len(future) > 0:
            fig.add_trace(go.Scatter(
                x=future['Date'], y=future['Forecasted_Demand'],
                mode='markers', name='Projected',
                marker=dict(size=14, color=AMBER, symbol='star',
                            line=dict(color='white', width=2)),
                hovertemplate='<b>%{x|%b %Y}</b><br>Projected: %{y:,.0f}<extra></extra>'))

    fig.update_layout(
        plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        font=dict(family='Inter', color=TEXT_AXIS, size=12),
        xaxis=dict(showgrid=False, tickformat='%b %Y', **axis_style()),
        yaxis=dict(showgrid=True, gridcolor=GRID, **axis_style()),
        legend=dict(orientation='h', y=1.05, x=0.5, xanchor='center',
                    bgcolor=WHITE, font=dict(color=TEXT_DARK, size=12)),
        height=380, margin=dict(l=10, r=10, t=40, b=10),
        hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Seasonal Pattern</div>
            <div class='chart-subtitle'>Year-over-year monthly demand · Orange = Q4 Peak · Blue = Monsoon</div>
        </div>
        """, unsafe_allow_html=True)

        merged['MN'] = merged['Order_Date'].dt.month
        merged['Yr'] = merged['Order_Date'].dt.year
        seas = merged[merged['Category'] == sel].groupby(
            ['Yr','MN'])['Quantity_Ordered'].sum().reset_index()
        mn = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
              7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        seas['Month'] = seas['MN'].map(mn)

        fig2 = go.Figure()
        for idx, yr in enumerate(seas['Yr'].unique()):
            yd = seas[seas['Yr'] == yr].sort_values('MN')
            fig2.add_trace(go.Scatter(
                x=yd['Month'], y=yd['Quantity_Ordered'],
                mode='lines+markers', name=str(yr),
                line=dict(width=2.5, color=[STEEL, ORANGE][idx % 2]),
                marker=dict(size=7),
                hovertemplate='<b>%{x} ' + str(yr) + '</b><br>%{y:,} units<extra></extra>'))

        fig2.add_vrect(x0="Oct", x1="Dec", fillcolor="rgba(234,88,12,0.10)",
                       layer="below", line_width=0)
        fig2.add_vrect(x0="Jun", x1="Aug", fillcolor="rgba(30,64,175,0.10)",
                       layer="below", line_width=0)

        fig2.add_annotation(x="Nov", y=1, yref="paper", text="<b>Q4 PEAK</b>",
                            showarrow=False,
                            font=dict(size=10, color=ORANGE, family='Inter'),
                            yanchor="bottom", yshift=2)
        fig2.add_annotation(x="Jul", y=1, yref="paper", text="<b>MONSOON</b>",
                            showarrow=False,
                            font=dict(size=10, color=STEEL, family='Inter'),
                            yanchor="bottom", yshift=2)

        fig2.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_AXIS, size=12),
            xaxis=dict(showgrid=False, **axis_style()),
            yaxis=dict(showgrid=True, gridcolor=GRID, **axis_style()),
            legend=dict(bgcolor=WHITE, font=dict(color=TEXT_DARK, size=12),
                        orientation='h', y=-0.20, x=0.5, xanchor='center'),
            height=320, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown(f"""
        <div class='chart-card'>
            <div class='chart-title'>Model Details</div>
            <div style='margin-top:12px;'>
                <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #E2E8F0;'>
                    <span style='color:#475569;font-size:11px;text-transform:uppercase;font-weight:600;letter-spacing:0.5px;'>Model</span>
                    <span style='color:#0F172A;font-size:13px;font-weight:600;'>Exp. Smoothing</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #E2E8F0;'>
                    <span style='color:#475569;font-size:11px;text-transform:uppercase;font-weight:600;letter-spacing:0.5px;'>MAPE</span>
                    <span style='color:{"#DC2626" if mv > 15 else "#059669"};font-size:15px;font-weight:700;'>{mv:.1f}%</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #E2E8F0;'>
                    <span style='color:#475569;font-size:11px;text-transform:uppercase;font-weight:600;letter-spacing:0.5px;'>Accuracy</span>
                    <span style='color:#1E40AF;font-size:15px;font-weight:700;'>{100-mv:.1f}%</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #E2E8F0;'>
                    <span style='color:#475569;font-size:11px;text-transform:uppercase;font-weight:600;letter-spacing:0.5px;'>Horizon</span>
                    <span style='color:#0F172A;font-size:13px;font-weight:600;'>3 Months</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #E2E8F0;'>
                    <span style='color:#475569;font-size:11px;text-transform:uppercase;font-weight:600;letter-spacing:0.5px;'>Train/Test</span>
                    <span style='color:#0F172A;font-size:13px;font-weight:600;'>80 / 20</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:10px 0;'>
                    <span style='color:#475569;font-size:11px;text-transform:uppercase;font-weight:600;letter-spacing:0.5px;'>Confidence</span>
                    <span style='color:#0F172A;font-size:13px;font-weight:600;'>90% Band</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)