"""Page 1 — Executive Overview"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_all_data, get_kpi_metrics

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
        linecolor='#CBD5E1',
        linewidth=1
    )


def show_page():
    data = load_all_data()
    k = get_kpi_metrics(data)
    df_inv = data['inventory']
    df_sales = data['sales']

    st.markdown("<div class='page-title'>Executive Overview</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Real-time supply chain performance dashboard</div>",
                unsafe_allow_html=True)

    # KPI Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Inventory Value", f"₹{k['total_inv_value']/10000000:.2f} Cr", "+8.3%")
    with c2:
        st.metric("Stockout Risk", k['stockout_count'], "-2 SKUs", delta_color="inverse")
    with c3:
        st.metric("Overstock Items", k['overstock_count'], "+1 SKU", delta_color="inverse")
    with c4:
        st.metric("Vendor Score", f"{k['avg_vendor_score']:.1f}", "+3.2 pts")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric("Forecast Accuracy", f"{k['forecast_accuracy']:.1f}%", "+2.1%")
    with c6:
        st.metric("On-Time Delivery", f"{k['on_time_pct']:.1f}%", "-1.5%", delta_color="inverse")
    with c7:
        st.metric("Active SKUs", k['total_skus'])
    with c8:
        st.metric("Total Orders", f"{k['total_orders']:,}")

    # Charts Row 1
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Monthly Inventory Value Trend</div>
            <div class='chart-subtitle'>Total inventory valuation over 24 months</div>
        </div>
        """, unsafe_allow_html=True)

        monthly = df_inv.groupby(
            df_inv['Date'].dt.to_period('M')
        )['Inventory_Value'].sum().reset_index()
        monthly['Date'] = monthly['Date'].dt.to_timestamp()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly['Date'], y=monthly['Inventory_Value'],
            mode='lines',
            line=dict(color=STEEL, width=2.5, shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(30,64,175,0.08)',
            hovertemplate='<b>%{x|%b %Y}</b><br>₹%{y:,.0f}<extra></extra>'
        ))
        fig.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_AXIS, size=12),
            xaxis=dict(showgrid=False, tickformat='%b %Y', **axis_style()),
            yaxis=dict(showgrid=True, gridcolor=GRID, tickprefix='₹',
                       tickformat='.2s', **axis_style()),
            height=280, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False, hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Stock Health Distribution</div>
            <div class='chart-subtitle'>Current SKU status</div>
        </div>
        """, unsafe_allow_html=True)

        status = df_inv['Stock_Status'].value_counts()
        cmap = {'Healthy': GREEN, 'Stockout Risk': RED, 'Overstock': AMBER}
        pcolors = [cmap.get(s, TEXT_MUTED) for s in status.index]

        fig2 = go.Figure(data=[go.Pie(
            labels=status.index, values=status.values, hole=0.7,
            marker=dict(colors=pcolors, line=dict(color=WHITE, width=3)),
            textinfo='percent',
            textfont=dict(color=WHITE, size=13, family='Inter'),
            hovertemplate='<b>%{label}</b><br>%{value} SKUs (%{percent})<extra></extra>'
        )])
        fig2.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_DARK, size=12),
            height=280, margin=dict(l=10, r=10, t=10, b=10),
            annotations=[dict(
                text=f"<b style='font-size:24px;color:#0F172A'>{status.sum()}</b><br>" +
                     f"<span style='font-size:11px;color:#475569'>TOTAL SKUs</span>",
                x=0.5, y=0.5, font=dict(family='Inter'), showarrow=False
            )],
            showlegend=True,
            legend=dict(orientation='h', y=-0.05, x=0.5, xanchor='center',
                        font=dict(size=11, color=TEXT_DARK))
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    # Charts Row 2
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Top 5 Revenue Generators</div>
            <div class='chart-subtitle'>Highest grossing SKUs</div>
        </div>
        """, unsafe_allow_html=True)

        comp = df_sales[df_sales['Order_Status'] == 'Completed']
        rev = comp.merge(df_inv[['SKU_ID','Unit_Cost','Product_Name']].drop_duplicates(),
                          on='SKU_ID', how='left')
        rev['Revenue'] = rev['Quantity_Delivered'] * rev['Unit_Cost']
        top5 = rev.groupby('Product_Name')['Revenue'].sum().nlargest(5).reset_index()
        top5 = top5.sort_values('Revenue', ascending=True)

        fig3 = go.Figure(go.Bar(
            x=top5['Revenue'], y=top5['Product_Name'], orientation='h',
            marker=dict(color=[STEEL, INDIGO, SLATE, ORANGE, AMBER][:len(top5)],
                        cornerradius=4),
            text=[f'₹{v/100000:.1f}L' for v in top5['Revenue']],
            textposition='outside',
            textfont=dict(color=TEXT_DARK, size=12, family='Inter'),
            hovertemplate='<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>'
        ))
        fig3.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_AXIS, size=12),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, **axis_style()),
            height=280, margin=dict(l=10, r=70, t=10, b=10),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    with col4:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title'>Demand by Region</div>
            <div class='chart-subtitle'>Total quantity ordered</div>
        </div>
        """, unsafe_allow_html=True)

        rg = df_sales.groupby('Region')['Quantity_Ordered'].sum().reset_index()
        rg = rg.sort_values('Quantity_Ordered', ascending=False)

        fig4 = go.Figure(go.Bar(
            x=rg['Region'], y=rg['Quantity_Ordered'],
            marker=dict(color=[STEEL, ORANGE, SLATE, INDIGO, AMBER],
                        cornerradius=4),
            text=[f'{v:,}' for v in rg['Quantity_Ordered']],
            textposition='outside',
            textfont=dict(color=TEXT_DARK, size=12, family='Inter'),
            hovertemplate='<b>%{x}</b><br>%{y:,} units<extra></extra>'
        ))
        fig4.update_layout(
            plot_bgcolor=WHITE, paper_bgcolor=WHITE,
            font=dict(family='Inter', color=TEXT_AXIS, size=12),
            xaxis=dict(showgrid=False, **axis_style()),
            yaxis=dict(showgrid=True, gridcolor=GRID, showticklabels=False),
            height=280, margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})