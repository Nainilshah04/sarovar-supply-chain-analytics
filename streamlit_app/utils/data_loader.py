"""
Sarovar Enterprises - Data Loader Module
Handles all data loading, preprocessing and metric calculations
"""

import pandas as pd
import numpy as np
import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')


@st.cache_data
def load_all_data():
    """Load and preprocess all datasets"""

    df_inventory = pd.read_csv(os.path.join(DATA_DIR, 'inventory_data.csv'))
    df_sales = pd.read_csv(os.path.join(DATA_DIR, 'sales_orders.csv'))
    df_vendor = pd.read_csv(os.path.join(DATA_DIR, 'vendor_data.csv'))
    df_po = pd.read_csv(os.path.join(DATA_DIR, 'purchase_orders.csv'))
    df_forecast = pd.read_csv(os.path.join(DATA_DIR, 'forecast_results.csv'))
    df_mape = pd.read_csv(os.path.join(DATA_DIR, 'mape_scores.csv'))
    df_monthly = pd.read_csv(os.path.join(DATA_DIR, 'monthly_demand.csv'))
    df_scorecard = pd.read_csv(os.path.join(DATA_DIR, 'vendor_scorecard.csv'))

    # Fix MAPE columns
    mape_cols = df_mape.columns.tolist()
    if len(mape_cols) == 4:
        df_mape.columns = ['Index', 'Category', 'MAPE', 'Accuracy']
        df_mape = df_mape.drop('Index', axis=1, errors='ignore')
    elif len(mape_cols) == 3:
        df_mape.columns = ['Category', 'MAPE', 'Accuracy']

    # Convert dates
    df_inventory['Date'] = pd.to_datetime(df_inventory['Date'])
    df_sales['Order_Date'] = pd.to_datetime(df_sales['Order_Date'])
    df_sales['Delivery_Date'] = pd.to_datetime(df_sales['Delivery_Date'], errors='coerce')
    df_vendor['Order_Date'] = pd.to_datetime(df_vendor['Order_Date'])
    df_vendor['Promised_Delivery_Date'] = pd.to_datetime(df_vendor['Promised_Delivery_Date'])
    df_vendor['Actual_Delivery_Date'] = pd.to_datetime(df_vendor['Actual_Delivery_Date'])
    df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
    df_monthly['Month'] = pd.to_datetime(df_monthly['Month'])

    # Stock status classification
    df_inventory['Stock_Status'] = 'Healthy'
    df_inventory.loc[
        df_inventory['Closing_Stock'] < df_inventory['Safety_Stock'],
        'Stock_Status'
    ] = 'Stockout Risk'
    df_inventory.loc[
        df_inventory['Closing_Stock'] > df_inventory['Reorder_Point'] * 3,
        'Stock_Status'
    ] = 'Overstock'

    df_inventory['Inventory_Value'] = (
        df_inventory['Closing_Stock'] * df_inventory['Unit_Cost']
    )

    # Vendor derived metrics
    df_vendor['Is_OnTime'] = (
        df_vendor['Actual_Delivery_Date'] <= df_vendor['Promised_Delivery_Date']
    )
    df_vendor['Defect_Rate'] = (
        df_vendor['Defect_Quantity'] / df_vendor['Quantity_Ordered'] * 100
    )
    df_vendor['Lead_Time'] = (
        df_vendor['Actual_Delivery_Date'] - df_vendor['Order_Date']
    ).dt.days

    return {
        'inventory': df_inventory,
        'sales': df_sales,
        'vendor': df_vendor,
        'po': df_po,
        'forecast': df_forecast,
        'mape': df_mape,
        'monthly': df_monthly,
        'scorecard': df_scorecard
    }


@st.cache_data
def get_kpi_metrics(data):
    """Calculate executive KPI metrics"""

    df_inv = data['inventory']
    df_vendor = data['vendor']
    df_sc = data['scorecard']
    df_mape = data['mape']

    return {
        'total_inv_value': round(df_inv['Inventory_Value'].sum(), 2),
        'stockout_count': df_inv[df_inv['Stock_Status'] == 'Stockout Risk']['SKU_ID'].nunique(),
        'overstock_count': df_inv[df_inv['Stock_Status'] == 'Overstock']['SKU_ID'].nunique(),
        'avg_vendor_score': round(df_sc['Composite_Score'].mean(), 2),
        'forecast_accuracy': round(100 - df_mape['MAPE'].mean(), 2),
        'on_time_pct': round(df_vendor['Is_OnTime'].mean() * 100, 2),
        'total_skus': df_inv['SKU_ID'].nunique(),
        'total_orders': len(data['sales'])
    }


@st.cache_data
def get_vendor_performance(data):
    """Calculate vendor composite performance"""

    df_vendor = data['vendor']

    vp = df_vendor.groupby('Vendor_Name').agg(
        Total_Orders=('Vendor_ID', 'count'),
        OnTime_Pct=('Is_OnTime', lambda x: round(x.mean() * 100, 1)),
        Defect_Rate=('Defect_Rate', lambda x: round(x.mean(), 2)),
        Avg_Lead_Time=('Lead_Time', lambda x: round(x.mean(), 1)),
        Total_Volume=('Quantity_Ordered', 'sum')
    ).reset_index()

    vp['Quality_Score'] = (100 - vp['Defect_Rate']).round(2)

    min_lt = vp['Avg_Lead_Time'].min()
    max_lt = vp['Avg_Lead_Time'].max()
    vp['Price_Score'] = (
        100 - ((vp['Avg_Lead_Time'] - min_lt) / (max_lt - min_lt + 0.001) * 100)
    ).round(2)

    vp['Composite_Score'] = (
        vp['OnTime_Pct'] * 0.5 +
        vp['Quality_Score'] * 0.3 +
        vp['Price_Score'] * 0.2
    ).round(2)

    vp['Performance_Flag'] = vp['Composite_Score'].apply(
        lambda x: 'GREEN' if x > 75 else ('YELLOW' if x >= 50 else 'RED')
    )

    return vp.sort_values('Composite_Score', ascending=False)


@st.cache_data
def get_inventory_turnover(data):
    """Calculate inventory turnover and DIO per SKU"""

    df_inv = data['inventory']
    df_sales = data['sales']

    avg_inv = df_inv.groupby('SKU_ID').agg(
        Avg_Inventory=('Closing_Stock', 'mean'),
        Unit_Cost=('Unit_Cost', 'mean'),
        Category=('Category', 'first'),
        Product_Name=('Product_Name', 'first')
    ).reset_index()

    completed = df_sales[df_sales['Order_Status'] == 'Completed']
    cogs_df = completed.groupby('SKU_ID').agg(
        Total_Units_Sold=('Quantity_Delivered', 'sum')
    ).reset_index()

    merged = avg_inv.merge(cogs_df, on='SKU_ID', how='left').fillna(0)
    merged['COGS'] = merged['Total_Units_Sold'] * merged['Unit_Cost']
    merged['Turnover_Ratio'] = (
        merged['COGS'] / merged['Avg_Inventory'].replace(0, np.nan)
    ).round(2).fillna(0)
    merged['DIO'] = (
        merged['Avg_Inventory'] / (merged['COGS'] / 365).replace(0, np.nan)
    ).round(1).fillna(0)

    return merged.sort_values('Turnover_Ratio', ascending=False)