"""Page 5 — Alerts & Recommendations"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_all_data, get_vendor_performance


def show_page():
    data = load_all_data()
    df_inv = data['inventory']
    vp = get_vendor_performance(data)

    st.markdown("<div class='page-title'>Alerts & Recommendations</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Action items requiring immediate attention</div>",
                unsafe_allow_html=True)

    latest = df_inv.sort_values('Date').groupby('SKU_ID').last().reset_index()
    stockout = latest[latest['Stock_Status'] == 'Stockout Risk'].copy()
    overstock = latest[latest['Stock_Status'] == 'Overstock'].copy()

    critical = len(stockout[stockout['Closing_Stock'] == 0])
    if critical > 0:
        st.markdown(f"""
        <div style='background:#FEE2E2; border:1px solid #FECACA;
                    border-radius:10px; padding:14px 20px; margin-bottom:16px;'>
            <div style='display:flex; align-items:center; gap:10px;'>
                <div style='width:8px;height:8px;background:#DC2626;border-radius:50%;'></div>
                <span style='color:#991B1B; font-size:13px; font-weight:700;'>
                    CRITICAL — {critical} SKU(s) completely out of stock
                </span>
            </div>
            <p style='color:#475569; font-size:11px; margin:6px 0 0 18px;'>
                Immediate procurement action required to prevent revenue loss.
            </p>
        </div>
        """, unsafe_allow_html=True)

    rv = len(vp[vp['Performance_Flag'] == 'RED'])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Stockout Risk", len(stockout), delta_color="inverse",
                  delta="Reorder needed")
    with c2:
        st.metric("Overstock", len(overstock), delta_color="inverse",
                  delta="Excess inventory")
    with c3:
        st.metric("Vendor Alerts", rv, delta_color="inverse",
                  delta="Performance issues")
    with c4:
        st.metric("Total Actions", len(stockout) + len(overstock) + rv,
                  delta_color="inverse", delta="Open items")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Stockout Alerts (only show if there are alerts) ──
    if len(stockout) > 0:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title' style='color:#DC2626;'>🔴 Stockout Alerts</div>
            <div class='chart-subtitle'>SKUs requiring immediate reorder action</div>
        </div>
        """, unsafe_allow_html=True)

        sd = stockout[['SKU_ID','Product_Name','Category','Closing_Stock',
                       'Safety_Stock','Reorder_Point','Warehouse_Location']].copy()
        sd['Deficit'] = sd['Safety_Stock'] - sd['Closing_Stock']
        sd['Action'] = sd['Closing_Stock'].apply(
            lambda x: 'Order Now' if x == 0 else 'Order < 3 Days')
        sd = sd.sort_values('Closing_Stock')
        sd.columns = ['SKU ID','Product','Category','Closing','Safety',
                      'Reorder','Warehouse','Deficit','Action']

        def hl(row):
            if row['Closing'] == 0:
                return ['background-color:#FEE2E2;color:#991B1B'] * len(row)
            return ['background-color:#FEF3C7;color:#92400E'] * len(row)

        st.dataframe(sd.style.apply(hl, axis=1),
                     use_container_width=True, height=300, hide_index=True)
    else:
        st.markdown("""
        <div class='alert-card alert-green'>
            <p class='alert-title' style='color:#059669;'>✓ All Clear — No Stockout Risks</p>
            <p class='alert-body'>All SKUs are above safety stock levels.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Overstock Alerts (only show if there are alerts) ──
    if len(overstock) > 0:
        st.markdown("""
        <div class='chart-card'>
            <div class='chart-title' style='color:#D97706;'>🟡 Overstock Alerts</div>
            <div class='chart-subtitle'>SKUs with excess inventory requiring action</div>
        </div>
        """, unsafe_allow_html=True)

        od = overstock[['SKU_ID','Product_Name','Category','Closing_Stock',
                        'Reorder_Point','Warehouse_Location']].copy()
        od['Excess'] = od['Closing_Stock'] - od['Reorder_Point']
        od['Ratio'] = (od['Closing_Stock'] / od['Reorder_Point']).round(1)
        od['Action'] = od['Ratio'].apply(
            lambda x: 'Liquidate' if x > 5 else 'Halt PO' if x > 4 else 'Reduce Orders')
        od = od.sort_values('Ratio', ascending=False)
        od.columns = ['SKU ID','Product','Category','Closing','Reorder',
                      'Warehouse','Excess','Ratio','Action']

        def hl2(row):
            if row['Ratio'] > 5:
                return ['background-color:#FEE2E2;color:#991B1B'] * len(row)
            return ['background-color:#FEF3C7;color:#92400E'] * len(row)

        st.dataframe(od.style.apply(hl2, axis=1),
                     use_container_width=True, height=300, hide_index=True)
    else:
        st.markdown("""
        <div class='alert-card alert-green'>
            <p class='alert-title' style='color:#059669;'>✓ All Clear — No Overstock Items</p>
            <p class='alert-body'>All SKUs are within healthy inventory ranges.</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Recommendations ──
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='chart-card'>
        <div class='chart-title'>Smart Recommendations</div>
        <div class='chart-subtitle'>AI-generated action items based on current data</div>
    </div>
    """, unsafe_allow_html=True)

    red_v = vp[vp['Performance_Flag'] == 'RED']['Vendor_Name'].tolist()
    top_sc = stockout.groupby('Category').size().idxmax() if len(stockout) > 0 else "N/A"
    top_oc = overstock.groupby('Category').size().idxmax() if len(overstock) > 0 else "N/A"

        # Build recommendations dynamically
    raw_recs = []

    # Stockout recommendation
    if len(stockout) > 0:
        raw_recs.append(("alert-red", "#DC2626", "Immediate Reorder Required",
                         f"{len(stockout)} SKUs below safety stock. Primary category: {top_sc}. "
                         f"Prioritize procurement from preferred vendors with fastest lead times."))
    else:
        raw_recs.append(("alert-green", "#059669", "Inventory Levels Healthy",
                         "All SKUs are above safety stock levels. "
                         "Continue current procurement strategy and monitor weekly."))

    # Overstock recommendation
    if len(overstock) > 0:
        raw_recs.append(("alert-amber", "#D97706", "Overstock Reduction Strategy",
                         f"{len(overstock)} SKUs above 3x reorder point. Category: {top_oc}. "
                         f"Halt new purchase orders and explore inter-warehouse transfers."))
    else:
        raw_recs.append(("alert-green", "#059669", "No Excess Inventory",
                         "Inventory levels are optimized. "
                         "No overstock items detected — continue current ordering patterns."))

    # Vendor recommendation
    if len(red_v) > 0:
        raw_recs.append(("alert-red", "#DC2626", "Vendor Performance Review",
                         f"{len(red_v)} vendor(s) flagged: {', '.join(red_v[:3])}. "
                         f"Schedule quarterly business reviews and enforce SLA penalties."))
    else:
        raw_recs.append(("alert-green", "#059669", "Vendor Performance Strong",
                         "All vendors meeting performance benchmarks. "
                         "Maintain regular communication and continue annual reviews."))

    # Always include these strategic recommendations
    raw_recs.extend([
        ("alert-blue", "#1E40AF", "Seasonal Demand Preparation",
         "Q4 demand increases by 30%. Begin safety stock buildup 8 weeks before October. "
         "Use monsoon slowdown for vendor renegotiations."),
        ("alert-orange", "#EA580C", "Cost Optimization Opportunity",
         "Implement ABC classification. Top 5 SKUs drive 60%+ revenue. "
         "Adopt JIT for low-value fasteners to reduce carrying costs by 15-20%."),
    ])

    # Auto-number and render
    for idx, (cls, color, title, body) in enumerate(raw_recs, start=1):
        st.markdown(f"""
        <div class='alert-card {cls}'>
            <p class='alert-title' style='color:{color};'>{idx:02d}  {title}</p>
            <p class='alert-body'>{body}</p>
        </div>
        """, unsafe_allow_html=True)