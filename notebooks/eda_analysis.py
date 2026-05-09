"""
================================================================================
SAROVAR ENTERPRISES - EDA + FORECASTING
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from statsmodels.tsa.holtwinters import ExponentialSmoothing
import os

os.makedirs('images/eda_outputs', exist_ok=True)

plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

print("="*60)
print("SAROVAR ENTERPRISES - EDA STARTED")
print("="*60)

# ==================================================
# LOAD DATA
# ==================================================
print("\n📂 Loading data...")

df_inventory = pd.read_csv('data/inventory_data.csv')
df_sales = pd.read_csv('data/sales_orders.csv')
df_vendor = pd.read_csv('data/vendor_data.csv')
df_po = pd.read_csv('data/purchase_orders.csv')

# Convert dates
df_inventory['Date'] = pd.to_datetime(df_inventory['Date'])
df_sales['Order_Date'] = pd.to_datetime(df_sales['Order_Date'])
df_sales['Delivery_Date'] = pd.to_datetime(df_sales['Delivery_Date'])
df_vendor['Order_Date'] = pd.to_datetime(df_vendor['Order_Date'])
df_vendor['Promised_Delivery_Date'] = pd.to_datetime(df_vendor['Promised_Delivery_Date'])
df_vendor['Actual_Delivery_Date'] = pd.to_datetime(df_vendor['Actual_Delivery_Date'])

print("✅ Data loaded!")
print(f"   Inventory: {df_inventory.shape}")
print(f"   Sales: {df_sales.shape}")
print(f"   Vendor: {df_vendor.shape}")
print(f"   Purchase Orders: {df_po.shape}")

# ==================================================
# CHART 1: INVENTORY DISTRIBUTION BY CATEGORY
# ==================================================
print("\n📈 Chart 1: Inventory Distribution...")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336']
categories_list = df_inventory['Category'].unique()

category_data = [
    df_inventory[df_inventory['Category'] == cat]['Closing_Stock'].values
    for cat in categories_list
]

bp = axes[0].boxplot(
    category_data,
    labels=categories_list,
    patch_artist=True
)

for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

axes[0].set_title('Closing Stock Distribution by Category', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Category', fontsize=12)
axes[0].set_ylabel('Closing Stock (Units)', fontsize=12)
axes[0].tick_params(axis='x', rotation=15)

avg_stock = df_inventory.groupby('Category').agg({
    'Opening_Stock': 'mean',
    'Closing_Stock': 'mean',
    'Safety_Stock': 'mean',
    'Reorder_Point': 'mean'
}).round(0)

x = np.arange(len(avg_stock.index))
width = 0.2

axes[1].bar(x - width*1.5, avg_stock['Opening_Stock'], width,
            label='Avg Opening Stock', color='#2196F3', alpha=0.8)
axes[1].bar(x - width*0.5, avg_stock['Closing_Stock'], width,
            label='Avg Closing Stock', color='#4CAF50', alpha=0.8)
axes[1].bar(x + width*0.5, avg_stock['Safety_Stock'], width,
            label='Safety Stock', color='#FF9800', alpha=0.8)
axes[1].bar(x + width*1.5, avg_stock['Reorder_Point'], width,
            label='Reorder Point', color='#F44336', alpha=0.8)

axes[1].set_title('Average Stock Levels by Category', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Category', fontsize=12)
axes[1].set_ylabel('Units', fontsize=12)
axes[1].set_xticks(x)
axes[1].set_xticklabels(avg_stock.index, rotation=15)
axes[1].legend(fontsize=10)

plt.tight_layout()
plt.savefig('images/eda_outputs/01_inventory_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 1 saved!")

# ==================================================
# CHART 2: MONTHLY DEMAND TREND
# ==================================================
print("\n📈 Chart 2: Monthly Demand Trends...")

df_sales_merged = df_sales.merge(
    df_inventory[['SKU_ID', 'Category']].drop_duplicates(),
    on='SKU_ID',
    how='left'
)

df_sales_merged['Month'] = df_sales_merged['Order_Date'].dt.to_period('M')
monthly_demand = df_sales_merged.groupby(
    ['Month', 'Category']
)['Quantity_Ordered'].sum().reset_index()
monthly_demand['Month'] = monthly_demand['Month'].dt.to_timestamp()

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

category_colors = {
    'Pipes': '#2196F3',
    'Sheets': '#4CAF50',
    'Coils': '#FF9800',
    'Fittings': '#9C27B0',
    'Fasteners': '#F44336'
}

unique_categories = monthly_demand['Category'].unique()

for idx, category in enumerate(unique_categories):
    cat_data = monthly_demand[
        monthly_demand['Category'] == category
    ].sort_values('Month')

    color = category_colors.get(category, '#333333')

    axes[idx].plot(
        cat_data['Month'],
        cat_data['Quantity_Ordered'],
        color=color, linewidth=2.5,
        marker='o', markersize=5
    )
    axes[idx].fill_between(
        cat_data['Month'],
        cat_data['Quantity_Ordered'],
        alpha=0.15, color=color
    )

    if len(cat_data) > 1:
        z = np.polyfit(range(len(cat_data)), cat_data['Quantity_Ordered'], 1)
        p = np.poly1d(z)
        axes[idx].plot(
            cat_data['Month'],
            p(range(len(cat_data))),
            "--", color='gray', alpha=0.7, linewidth=1.5, label='Trend'
        )

    axes[idx].set_title(f'{category} - Monthly Demand', fontsize=13, fontweight='bold', color=color)
    axes[idx].set_xlabel('Month', fontsize=10)
    axes[idx].set_ylabel('Quantity Ordered', fontsize=10)
    axes[idx].tick_params(axis='x', rotation=45)
    axes[idx].legend(fontsize=9)

axes[-1].set_visible(False)

plt.suptitle('Monthly Demand Trends by Category', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('images/eda_outputs/02_monthly_demand_trends.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 2 saved!")

# ==================================================
# CHART 3: VENDOR PERFORMANCE
# ==================================================
print("\n📈 Chart 3: Vendor Performance...")

df_vendor['Is_OnTime'] = df_vendor['Actual_Delivery_Date'] <= df_vendor['Promised_Delivery_Date']
df_vendor['Defect_Rate'] = (df_vendor['Defect_Quantity'] / df_vendor['Quantity_Ordered']) * 100
df_vendor['Lead_Time'] = (df_vendor['Actual_Delivery_Date'] - df_vendor['Order_Date']).dt.days

vendor_perf = df_vendor.groupby('Vendor_Name').agg(
    OnTime_Pct=('Is_OnTime', lambda x: round(x.mean() * 100, 1)),
    Defect_Rate=('Defect_Rate', 'mean'),
    Avg_Lead_Time=('Lead_Time', 'mean'),
    Total_Volume=('Quantity_Ordered', 'sum')
).round(2).reset_index()

vendor_perf['Quality_Score'] = 100 - vendor_perf['Defect_Rate']

min_lt = vendor_perf['Avg_Lead_Time'].min()
max_lt = vendor_perf['Avg_Lead_Time'].max()
vendor_perf['Price_Score'] = 100 - (
    (vendor_perf['Avg_Lead_Time'] - min_lt) /
    (max_lt - min_lt + 0.001) * 100
)

vendor_perf['Composite_Score'] = (
    vendor_perf['OnTime_Pct'] * 0.5 +
    vendor_perf['Quality_Score'] * 0.3 +
    vendor_perf['Price_Score'] * 0.2
).round(2)

fig, axes = plt.subplots(1, 3, figsize=(20, 8))

vendor_sorted_ot = vendor_perf.sort_values('OnTime_Pct', ascending=True)
colors_ot = [
    '#F44336' if x < 70 else '#FF9800' if x < 85 else '#4CAF50'
    for x in vendor_sorted_ot['OnTime_Pct']
]

bars = axes[0].barh(
    vendor_sorted_ot['Vendor_Name'],
    vendor_sorted_ot['OnTime_Pct'],
    color=colors_ot
)
axes[0].axvline(x=70, color='red', linestyle='--', linewidth=1.5, label='Min 70%')
axes[0].axvline(x=85, color='orange', linestyle='--', linewidth=1.5, label='Good 85%')

for bar, val in zip(bars, vendor_sorted_ot['OnTime_Pct']):
    axes[0].text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height()/2,
        f'{val}%', va='center', fontsize=9, fontweight='bold'
    )

axes[0].set_title('On-Time Delivery %', fontsize=13, fontweight='bold')
axes[0].set_xlabel('On-Time %', fontsize=11)
axes[0].legend(fontsize=9)
axes[0].set_xlim(0, 110)

vendor_sorted_dr = vendor_perf.sort_values('Defect_Rate', ascending=False)
colors_dr = [
    '#F44336' if x > 8 else '#FF9800' if x > 4 else '#4CAF50'
    for x in vendor_sorted_dr['Defect_Rate']
]

bars2 = axes[1].barh(
    vendor_sorted_dr['Vendor_Name'],
    vendor_sorted_dr['Defect_Rate'],
    color=colors_dr
)
axes[1].axvline(x=8, color='red', linestyle='--', linewidth=1.5, label='Critical 8%')
axes[1].axvline(x=4, color='orange', linestyle='--', linewidth=1.5, label='Warning 4%')

for bar, val in zip(bars2, vendor_sorted_dr['Defect_Rate']):
    axes[1].text(
        bar.get_width() + 0.1,
        bar.get_y() + bar.get_height()/2,
        f'{val:.1f}%', va='center', fontsize=9, fontweight='bold'
    )

axes[1].set_title('Defect Rate %', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Defect Rate %', fontsize=11)
axes[1].legend(fontsize=9)

vendor_sorted_cs = vendor_perf.sort_values('Composite_Score', ascending=True)
colors_cs = [
    '#F44336' if x < 50 else '#FF9800' if x < 75 else '#4CAF50'
    for x in vendor_sorted_cs['Composite_Score']
]

bars3 = axes[2].barh(
    vendor_sorted_cs['Vendor_Name'],
    vendor_sorted_cs['Composite_Score'],
    color=colors_cs
)
axes[2].axvline(x=75, color='green', linestyle='--', linewidth=1.5, label='Green >75')
axes[2].axvline(x=50, color='red', linestyle='--', linewidth=1.5, label='Red <50')

for bar, val in zip(bars3, vendor_sorted_cs['Composite_Score']):
    axes[2].text(
        bar.get_width() + 0.3,
        bar.get_y() + bar.get_height()/2,
        f'{val:.1f}', va='center', fontsize=9, fontweight='bold'
    )

axes[2].set_title('Composite Score', fontsize=13, fontweight='bold')
axes[2].set_xlabel('Score (0-100)', fontsize=11)
axes[2].legend(fontsize=9)
axes[2].set_xlim(0, 110)

plt.suptitle('Vendor Performance Analysis', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('images/eda_outputs/03_vendor_performance.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 3 saved!")

# ==================================================
# CHART 4: STOCKOUT VS OVERSTOCK
# ==================================================
print("\n📈 Chart 4: Stockout vs Overstock...")

df_inventory['Stock_Status'] = 'Healthy'
df_inventory.loc[
    df_inventory['Closing_Stock'] < df_inventory['Safety_Stock'],
    'Stock_Status'
] = 'Stockout Risk'
df_inventory.loc[
    df_inventory['Closing_Stock'] > df_inventory['Reorder_Point'] * 3,
    'Stock_Status'
] = 'Overstock'

status_counts = df_inventory['Stock_Status'].value_counts()

colors_status = {
    'Healthy': '#4CAF50',
    'Stockout Risk': '#F44336',
    'Overstock': '#FF9800'
}

fig, axes = plt.subplots(1, 3, figsize=(18, 7))

pie_colors = [colors_status[s] for s in status_counts.index]

wedges, texts, autotexts = axes[0].pie(
    status_counts.values,
    labels=status_counts.index,
    colors=pie_colors,
    autopct='%1.1f%%',
    pctdistance=0.75,
    startangle=90,
    wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
)

for text in autotexts:
    text.set_fontsize(12)
    text.set_fontweight('bold')

axes[0].set_title('Stock Status Distribution', fontsize=13, fontweight='bold')
axes[0].text(0, 0, f'Total\n{status_counts.sum()}\nSKUs',
             ha='center', va='center', fontsize=13, fontweight='bold')

category_status = df_inventory.groupby(
    ['Category', 'Stock_Status']
).size().unstack(fill_value=0)

bottom_vals = np.zeros(len(category_status))

for status in ['Healthy', 'Stockout Risk', 'Overstock']:
    if status in category_status.columns:
        vals = category_status[status].values
        axes[1].bar(
            category_status.index, vals,
            bottom=bottom_vals,
            label=status,
            color=colors_status[status],
            edgecolor='white'
        )
        for j, (v, b) in enumerate(zip(vals, bottom_vals)):
            if v > 0:
                axes[1].text(j, b + v/2, str(v),
                             ha='center', va='center',
                             fontsize=10, fontweight='bold', color='white')
        bottom_vals += vals

axes[1].set_title('Stock Status by Category', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Category', fontsize=11)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].legend(fontsize=10)
axes[1].tick_params(axis='x', rotation=15)

warehouse_status = df_inventory.groupby(
    ['Warehouse_Location', 'Stock_Status']
).size().unstack(fill_value=0)

bottom_vals2 = np.zeros(len(warehouse_status))

for status in ['Healthy', 'Stockout Risk', 'Overstock']:
    if status in warehouse_status.columns:
        vals = warehouse_status[status].values
        axes[2].bar(
            warehouse_status.index, vals,
            bottom=bottom_vals2,
            label=status,
            color=colors_status[status],
            edgecolor='white'
        )
        for j, (v, b) in enumerate(zip(vals, bottom_vals2)):
            if v > 0:
                axes[2].text(j, b + v/2, str(v),
                             ha='center', va='center',
                             fontsize=10, fontweight='bold', color='white')
        bottom_vals2 += vals

axes[2].set_title('Stock Status by Warehouse', fontsize=13, fontweight='bold')
axes[2].set_xlabel('Warehouse', fontsize=11)
axes[2].set_ylabel('Count', fontsize=11)
axes[2].legend(fontsize=10)
axes[2].tick_params(axis='x', rotation=15)

plt.suptitle('Inventory Health Analysis', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('images/eda_outputs/04_stockout_overstock.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 4 saved!")

# ==================================================
# CHART 5: CORRELATION HEATMAP
# ==================================================
print("\n📈 Chart 5: Correlation Heatmap...")

df_vendor['Lead_Time'] = (
    df_vendor['Actual_Delivery_Date'] - df_vendor['Order_Date']
).dt.days

vendor_sku_lead = df_vendor.groupby('SKU_ID')['Lead_Time'].mean().reset_index()
vendor_sku_defect = df_vendor.groupby('SKU_ID')['Defect_Rate'].mean().reset_index()
sku_order_qty = df_sales.groupby('SKU_ID')['Quantity_Ordered'].mean().reset_index()

corr_data = df_inventory.groupby('SKU_ID').agg(
    Opening_Stock=('Opening_Stock', 'mean'),
    Closing_Stock=('Closing_Stock', 'mean'),
    Reorder_Point=('Reorder_Point', 'mean'),
    Safety_Stock=('Safety_Stock', 'mean'),
    Unit_Cost=('Unit_Cost', 'mean')
).reset_index()

corr_data = corr_data.merge(sku_order_qty, on='SKU_ID', how='left')
corr_data = corr_data.merge(vendor_sku_lead, on='SKU_ID', how='left')
corr_data = corr_data.merge(vendor_sku_defect, on='SKU_ID', how='left')

numeric_cols = [
    'Opening_Stock', 'Closing_Stock', 'Reorder_Point',
    'Safety_Stock', 'Unit_Cost', 'Quantity_Ordered',
    'Lead_Time', 'Defect_Rate'
]

corr_matrix = corr_data[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(12, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

sns.heatmap(
    corr_matrix,
    mask=mask,
    annot=True,
    fmt='.2f',
    cmap='RdYlGn',
    center=0,
    vmin=-1, vmax=1,
    ax=ax,
    square=True,
    linewidths=0.5,
    annot_kws={'size': 11, 'weight': 'bold'}
)

ax.set_title('Correlation Heatmap - Supply Chain Metrics', fontsize=15, fontweight='bold', pad=20)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10)

plt.tight_layout()
plt.savefig('images/eda_outputs/05_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 5 saved!")

# ==================================================
# DEMAND FORECASTING
# ==================================================
print("\n" + "="*60)
print("🔮 DEMAND FORECASTING")
print("="*60)

monthly_demand_forecast = df_sales_merged.groupby(
    [df_sales_merged['Order_Date'].dt.to_period('M'), 'Category']
)['Quantity_Ordered'].sum().reset_index()

monthly_demand_forecast.columns = ['Month', 'Category', 'Demand']
monthly_demand_forecast['Month'] = monthly_demand_forecast['Month'].dt.to_timestamp()
monthly_demand_forecast = monthly_demand_forecast.sort_values(['Category', 'Month'])

forecast_results = {}
mape_scores = {}

for category in monthly_demand_forecast['Category'].unique():
    cat_data = monthly_demand_forecast[
        monthly_demand_forecast['Category'] == category
    ].sort_values('Month')

    demand_series = cat_data['Demand'].values

    if len(demand_series) < 6:
        print(f"   ⚠️ {category}: Not enough data")
        continue

    split_idx = int(len(demand_series) * 0.8)
    train_data = demand_series[:split_idx]
    test_data = demand_series[split_idx:]

    try:
        model = ExponentialSmoothing(
            train_data,
            trend='add',
            seasonal=None,
            initialization_method='estimated'
        )
        fitted_model = model.fit(optimized=True)

        n_forecast = len(test_data) + 3
        predictions = fitted_model.forecast(n_forecast)
        predictions = np.maximum(predictions, 0)

        test_predictions = predictions[:len(test_data)]
        non_zero_mask = test_data > 0

        if non_zero_mask.sum() > 0:
            mape = np.mean(
                np.abs(
                    (test_data[non_zero_mask] - test_predictions[non_zero_mask]) /
                    test_data[non_zero_mask]
                )
            ) * 100
        else:
            mape = 0

        mape_scores[category] = round(mape, 2)

        forecast_results[category] = {
            'dates': cat_data['Month'].values,
            'actual': demand_series,
            'train_size': split_idx,
            'forecast': predictions,
            'mape': round(mape, 2)
        }

        print(f"   ✅ {category}: MAPE = {mape:.2f}%")

    except Exception as e:
        print(f"   ❌ {category}: {str(e)}")

# ==================================================
# FORECAST CHART
# ==================================================
print("\n📈 Chart 6: Forecast Chart...")

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
axes = axes.flatten()

for idx, category in enumerate(forecast_results.keys()):
    result = forecast_results[category]
    color = category_colors.get(category, '#333333')
    ax = axes[idx]

    actual_dates = result['dates']
    split_idx = result['train_size']

    ax.plot(
        actual_dates[:split_idx],
        result['actual'][:split_idx],
        color=color, linewidth=2,
        label='Actual (Train)', marker='o', markersize=4
    )

    ax.plot(
        actual_dates[split_idx:],
        result['actual'][split_idx:],
        color=color, linewidth=2, linestyle='--',
        label='Actual (Test)', marker='s', markersize=4
    )

    last_date = pd.Timestamp(actual_dates[-1])
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=3, freq='MS'
    )

    all_forecast_dates = list(actual_dates[split_idx:]) + list(future_dates)
    forecast_vals = result['forecast']

    ax.plot(
        all_forecast_dates,
        forecast_vals,
        color='purple', linewidth=2, linestyle=':',
        label='Forecast', marker='^', markersize=5
    )

    ax.fill_between(
        all_forecast_dates,
        forecast_vals * 0.90,
        forecast_vals * 1.10,
        alpha=0.15, color='purple',
        label='Confidence Band'
    )

    ax.axvline(x=actual_dates[split_idx], color='gray', linestyle='--', alpha=0.7)
    ax.axvline(x=actual_dates[-1], color='red', linestyle='--', alpha=0.7)

    ax.set_title(f'{category} | MAPE: {result["mape"]}%',
                 fontsize=12, fontweight='bold', color=color)
    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Demand (Units)', fontsize=10)
    ax.legend(fontsize=8)
    ax.tick_params(axis='x', rotation=45)

axes[-1].set_visible(False)

plt.suptitle('Demand Forecasting - Exponential Smoothing', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('images/eda_outputs/06_demand_forecast.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Chart 6 saved!")

# ==================================================
# VENDOR SCORECARD
# ==================================================
print("\n📊 Building Vendor Scorecard...")

def get_flag(score):
    if score > 75:
        return 'GREEN'
    elif score >= 50:
        return 'YELLOW'
    else:
        return 'RED'

vendor_scorecard = vendor_perf[[
    'Vendor_Name', 'OnTime_Pct', 'Defect_Rate',
    'Avg_Lead_Time', 'Total_Volume', 'Composite_Score'
]].copy()

vendor_scorecard['Performance_Flag'] = vendor_scorecard['Composite_Score'].apply(get_flag)
vendor_scorecard = vendor_scorecard.sort_values('Composite_Score', ascending=False)
vendor_scorecard['Rank'] = range(1, len(vendor_scorecard) + 1)

print(vendor_scorecard[[
    'Rank', 'Vendor_Name', 'OnTime_Pct',
    'Defect_Rate', 'Composite_Score', 'Performance_Flag'
]].to_string(index=False))

vendor_scorecard.to_csv('data/vendor_scorecard.csv', index=False)
print("✅ Vendor scorecard saved!")

# ==================================================
# SAVE FORECAST DATA FOR STREAMLIT
# ==================================================
print("\n💾 Saving forecast data...")

forecast_export = []
for category, result in forecast_results.items():
    actual_dates = result['dates']
    last_date = pd.Timestamp(actual_dates[-1])
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=3, freq='MS'
    )
    all_forecast_dates = list(actual_dates[result['train_size']:]) + list(future_dates)

    for i, (date, val) in enumerate(zip(all_forecast_dates, result['forecast'])):
        forecast_export.append({
            'Category': category,
            'Date': pd.Timestamp(date).strftime('%Y-%m-%d'),
            'Forecasted_Demand': round(val, 0),
            'Type': 'Test' if i < len(actual_dates) - result['train_size'] else 'Future'
        })

pd.DataFrame(forecast_export).to_csv('data/forecast_results.csv', index=False)

mape_df = pd.DataFrame.from_dict(mape_scores, orient='index', columns=['MAPE'])
mape_df['Accuracy'] = (100 - mape_df['MAPE']).round(2)
mape_df.to_csv('data/mape_scores.csv')

monthly_demand_forecast.to_csv('data/monthly_demand.csv', index=False)

print("✅ All data files saved!")
print("   - data/vendor_scorecard.csv")
print("   - data/forecast_results.csv")
print("   - data/mape_scores.csv")
print("   - data/monthly_demand.csv")

print("\n" + "="*60)
print("✅ EDA + FORECASTING COMPLETE!")
print("="*60)