"""
Data Loader Utility - Loads and preprocesses all CSV files
"""

import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_all_data():
    """Load all CSV files with caching for performance"""

    # Load raw data
    df_inventory = pd.read_csv('data/inventory_data.csv')
    df_sales = pd.read_csv('data/sales_orders.csv')
    df_vendor = pd.read_csv('data/vendor_data.csv')
    df_po = pd.read_csv('data/purchase_orders.csv')
    df_forecast = pd.read_csv('data/forecast_results.csv')
    df_mape = pd.read_csv('data/mape_scores.csv')
    df_monthly = pd.read_csv('data/monthly_demand.csv')
    df_scorecard = pd.read_csv('data/vendor_scorecard.csv')

    # Convert dates - inventory
    df_inventory['Date'] = pd.to_datetime(df_inventory['Date'])

    # Convert dates - sales
    df_sales['Order_Date'] = pd.to_datetime(df_sales['Order_Date'])
    df_sales['Delivery_Date'] = pd.to_datetime(df_sales['Delivery_Date'])

    # Convert dates - vendor
    df_vendor['Order_Date'] = pd.to_datetime(df_vendor['Order_Date'])
    df_vendor['Promised_Delivery_Date'] = pd.to_datetime(df_vendor['Promised_Delivery_Date'])
    df_vendor['Actual_Delivery_Date'] = pd.to_datetime(df_vendor['Actual_Delivery_Date'])

    # Convert dates - forecast
    df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
    df_monthly['Month'] = pd.to_datetime(df_monthly['Month'])

    # Add derived columns to inventory
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

    # Add derived columns to vendor
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
    """Calculate all KPI metrics for executive summary"""

    df_inventory = data['inventory']
    df_vendor = data['vendor']
    df_scorecard = data['scorecard']
    df_mape = data['mape']

    # Total Inventory Value
    total_inv_value = df_inventory['Inventory_Value'].sum()

    # Stockout Risk Count
    stockout_count = len(
        df_inventory[df_inventory['Stock_Status'] == 'Stockout Risk']['SKU_ID'].unique()
    )

    # Overstock Count
    overstock_count = len(
        df_inventory[df_inventory['Stock_Status'] == 'Overstock']['SKU_ID'].unique()
    )

    # Average Vendor Score
    avg_vendor_score = df_scorecard['Composite_Score'].mean()

    # Forecast Accuracy
    avg_mape = df_mape['MAPE'].mean()
    forecast_accuracy = 100 - avg_mape

    # On Time Delivery
    on_time_pct = df_vendor['Is_OnTime'].mean() * 100

    # Total SKUs
    total_skus = df_inventory['SKU_ID'].nunique()

    # Total Orders
    total_orders = len(data['sales'])

    return {
        'total_inv_value': round(total_inv_value, 2),
        'stockout_count': stockout_count,
        'overstock_count': overstock_count,
        'avg_vendor_score': round(avg_vendor_score, 2),
        'forecast_accuracy': round(forecast_accuracy, 2),
        'on_time_pct': round(on_time_pct, 2),
        'total_skus': total_skus,
        'total_orders': total_orders
    }


@st.cache_data
def get_vendor_performance(data):
    """Calculate vendor performance metrics"""

    df_vendor = data['vendor']

    vendor_perf = df_vendor.groupby('Vendor_Name').agg(
        Total_Orders=('Vendor_ID', 'count'),
        OnTime_Pct=('Is_OnTime', lambda x: round(x.mean() * 100, 1)),
        Defect_Rate=('Defect_Rate', lambda x: round(x.mean(), 2)),
        Avg_Lead_Time=('Lead_Time', lambda x: round(x.mean(), 1)),
        Total_Volume=('Quantity_Ordered', 'sum')
    ).reset_index()

    # Quality score
    vendor_perf['Quality_Score'] = (100 - vendor_perf['Defect_Rate']).round(2)

    # Price score (based on lead time)
    min_lt = vendor_perf['Avg_Lead_Time'].min()
    max_lt = vendor_perf['Avg_Lead_Time'].max()
    vendor_perf['Price_Score'] = (
        100 - ((vendor_perf['Avg_Lead_Time'] - min_lt) /
               (max_lt - min_lt + 0.001) * 100)
    ).round(2)

    # Composite score
    vendor_perf['Composite_Score'] = (
        vendor_perf['OnTime_Pct'] * 0.5 +
        vendor_perf['Quality_Score'] * 0.3 +
        vendor_perf['Price_Score'] * 0.2
    ).round(2)

    # Performance flag
    def get_flag(score):
        if score > 75:
            return 'GREEN'
        elif score >= 50:
            return 'YELLOW'
        else:
            return 'RED'

    vendor_perf['Performance_Flag'] = vendor_perf['Composite_Score'].apply(get_flag)

    return vendor_perf.sort_values('Composite_Score', ascending=False)


@st.cache_data
def get_inventory_turnover(data):
    """Calculate inventory turnover ratio per SKU"""

    df_inventory = data['inventory']
    df_sales = data['sales']

    # Average inventory per SKU
    avg_inv = df_inventory.groupby('SKU_ID').agg(
        Avg_Inventory=('Closing_Stock', 'mean'),
        Unit_Cost=('Unit_Cost', 'mean'),
        Category=('Category', 'first'),
        Product_Name=('Product_Name', 'first')
    ).reset_index()

    # COGS per SKU
    completed_sales = df_sales[df_sales['Order_Status'] == 'Completed']
    cogs = completed_sales.groupby('SKU_ID').agg(
        Total_Units_Sold=('Quantity_Delivered', 'sum')
    ).reset_index()

    merged = avg_inv.merge(cogs, on='SKU_ID', how='left').fillna(0)
    merged['COGS'] = merged['Total_Units_Sold'] * merged['Unit_Cost']
    merged['Turnover_Ratio'] = (
        merged['COGS'] / merged['Avg_Inventory'].replace(0, np.nan)
    ).round(2).fillna(0)

    merged['DIO'] = (
        merged['Avg_Inventory'] / (merged['COGS'] / 365).replace(0, np.nan)
    ).round(1).fillna(0)

    return merged.sort_values('Turnover_Ratio', ascending=False)