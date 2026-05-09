"""
Sarovar Enterprises - Synthetic Supply Chain Data Generator
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

print("=" * 60)
print("SAROVAR ENTERPRISES - DATA GENERATION STARTED")
print("=" * 60)

# Configuration
CATEGORIES = {
    'Pipes': {'base_price': 1500, 'variance': 500, 'count': 15},
    'Sheets': {'base_price': 2000, 'variance': 600, 'count': 12},
    'Coils': {'base_price': 2500, 'variance': 700, 'count': 10},
    'Fittings': {'base_price': 800, 'variance': 300, 'count': 8},
    'Fasteners': {'base_price': 200, 'variance': 100, 'count': 5}
}

WAREHOUSES = ['Mumbai_Central', 'Navi_Mumbai', 'Thane', 'Pune']
REGIONS = ['North', 'South', 'East', 'West', 'Mumbai']

VENDORS = [
    'Steel Suppliers India',
    'Mumbai Metal Works',
    'Premium Steel Co',
    'Reliable Metals Ltd',
    'Quick Steel Industries',
    'Delayed Suppliers Pvt',
    'Late Delivery Inc',
    'Slow Logistics Ltd',
    'Defective Materials Co',
    'Quality Issues Pvt'
]

PAYMENT_TERMS = ['Net 30', 'Net 45', 'Net 60', 'Immediate', 'Net 15']

START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2023, 12, 31)
DATE_RANGE = pd.date_range(start=START_DATE, end=END_DATE, freq='MS')

print(f"\n📅 Date Range: {START_DATE.date()} to {END_DATE.date()}")
print(f"📦 Total Categories: {len(CATEGORIES)}")
print(f"🏭 Total Vendors: {len(VENDORS)}")

def get_seasonal_multiplier(month):
    if month in [10, 11, 12]:
        return 1.30
    elif month in [6, 7, 8]:
        return 0.85
    else:
        return 1.0

def generate_sku_id(category, index):
    prefix = category[:3].upper()
    return f"SKU_{prefix}_{index:04d}"

# 1. INVENTORY DATA
print("\n" + "="*60)
print("📊 GENERATING INVENTORY DATA...")
print("="*60)

inventory_records = []
sku_master = []

sku_counter = 1
for category, details in CATEGORIES.items():
    for i in range(details['count']):
        sku_id = generate_sku_id(category, sku_counter)
        product_name = f"{category[:-1]} Type-{chr(65+i)}"
        
        unit_cost = details['base_price'] + np.random.randint(-details['variance'], details['variance'])
        reorder_point = np.random.randint(100, 500)
        safety_stock = int(reorder_point * 0.4)
        
        sku_master.append({
            'SKU_ID': sku_id,
            'Product_Name': product_name,
            'Category': category,
            'Unit_Cost': unit_cost,
            'Reorder_Point': reorder_point,
            'Safety_Stock': safety_stock
        })
        
        for date in DATE_RANGE:
            warehouse = np.random.choice(WAREHOUSES)
            seasonal_factor = get_seasonal_multiplier(date.month)
            
            base_opening = np.random.randint(200, 1000)
            opening_stock = int(base_opening * seasonal_factor)
            
            stock_change = np.random.randint(-200, 100)
            closing_stock = max(0, opening_stock + stock_change)
            
            if np.random.random() < 0.12:
                closing_stock = np.random.randint(0, safety_stock)
            
            if np.random.random() < 0.09:
                closing_stock = reorder_point * np.random.randint(4, 7)
            
            inventory_records.append({
                'SKU_ID': sku_id,
                'Product_Name': product_name,
                'Category': category,
                'Opening_Stock': opening_stock,
                'Closing_Stock': closing_stock,
                'Reorder_Point': reorder_point,
                'Safety_Stock': safety_stock,
                'Unit_Cost': unit_cost,
                'Warehouse_Location': warehouse,
                'Date': date.strftime('%Y-%m-%d')
            })
        
        sku_counter += 1

df_inventory = pd.DataFrame(inventory_records)

if len(df_inventory) > 500:
    df_inventory = df_inventory.sample(n=500, random_state=42).reset_index(drop=True)

print(f"✅ Inventory records: {len(df_inventory)}")
print(f"   - Unique SKUs: {df_inventory['SKU_ID'].nunique()}")
print(f"   - Stockout risk: {len(df_inventory[df_inventory['Closing_Stock'] < df_inventory['Safety_Stock']])}")
print(f"   - Overstock: {len(df_inventory[df_inventory['Closing_Stock'] > df_inventory['Reorder_Point'] * 3])}")

# 2. SALES ORDERS
print("\n" + "="*60)
print("📦 GENERATING SALES ORDERS...")
print("="*60)

sales_orders = []
order_statuses = ['Completed', 'Pending', 'Cancelled']
status_weights = [0.75, 0.15, 0.10]

for order_num in range(1, 801):
    order_id = f"ORD_{order_num:06d}"
    sku_data = sku_master[np.random.randint(0, len(sku_master))]
    sku_id = sku_data['SKU_ID']
    customer_id = f"CUST_{np.random.randint(1001, 2001)}"
    
    days_offset = np.random.randint(0, (END_DATE - START_DATE).days)
    order_date = START_DATE + timedelta(days=days_offset)
    
    seasonal_factor = get_seasonal_multiplier(order_date.month)
    base_quantity = np.random.randint(50, 300)
    quantity_ordered = int(base_quantity * seasonal_factor)
    
    order_status = np.random.choice(order_statuses, p=status_weights)
    
    if order_status == 'Completed':
        quantity_delivered = quantity_ordered
        delivery_days = np.random.randint(3, 15)
    elif order_status == 'Pending':
        quantity_delivered = int(quantity_ordered * np.random.uniform(0, 0.5))
        delivery_days = np.random.randint(1, 5)
    else:
        quantity_delivered = 0
        delivery_days = 0
    
    delivery_date = order_date + timedelta(days=delivery_days) if delivery_days > 0 else None
    region = np.random.choice(REGIONS)
    
    sales_orders.append({
        'Order_ID': order_id,
        'SKU_ID': sku_id,
        'Customer_ID': customer_id,
        'Order_Date': order_date.strftime('%Y-%m-%d'),
        'Quantity_Ordered': quantity_ordered,
        'Quantity_Delivered': quantity_delivered,
        'Delivery_Date': delivery_date.strftime('%Y-%m-%d') if delivery_date else None,
        'Order_Status': order_status,
        'Region': region
    })

df_sales = pd.DataFrame(sales_orders)
print(f"✅ Sales orders: {len(df_sales)}")

# 3. VENDOR DATA
print("\n" + "="*60)
print("🏭 GENERATING VENDOR DATA...")
print("="*60)

vendor_records = []

vendor_performance = {
    'Steel Suppliers India': {'on_time': 0.90, 'defect_rate': 0.02},
    'Mumbai Metal Works': {'on_time': 0.88, 'defect_rate': 0.03},
    'Premium Steel Co': {'on_time': 0.92, 'defect_rate': 0.01},
    'Reliable Metals Ltd': {'on_time': 0.85, 'defect_rate': 0.04},
    'Quick Steel Industries': {'on_time': 0.87, 'defect_rate': 0.03},
    'Delayed Suppliers Pvt': {'on_time': 0.55, 'defect_rate': 0.05},
    'Late Delivery Inc': {'on_time': 0.60, 'defect_rate': 0.06},
    'Slow Logistics Ltd': {'on_time': 0.65, 'defect_rate': 0.04},
    'Defective Materials Co': {'on_time': 0.75, 'defect_rate': 0.12},
    'Quality Issues Pvt': {'on_time': 0.78, 'defect_rate': 0.10}
}

for rec_num in range(1, 301):
    vendor_id = f"VEN_{rec_num:04d}"
    vendor_name = np.random.choice(VENDORS)
    
    sku_data = sku_master[np.random.randint(0, len(sku_master))]
    sku_id = sku_data['SKU_ID']
    
    days_offset = np.random.randint(0, (END_DATE - START_DATE).days)
    order_date = START_DATE + timedelta(days=days_offset)
    
    promised_days = np.random.randint(7, 21)
    promised_delivery = order_date + timedelta(days=promised_days)
    
    perf = vendor_performance[vendor_name]
    is_on_time = np.random.random() < perf['on_time']
    
    if is_on_time:
        actual_days = np.random.randint(promised_days - 2, promised_days + 1)
    else:
        actual_days = np.random.randint(promised_days + 1, promised_days + 15)
    
    actual_delivery = order_date + timedelta(days=actual_days)
    
    quantity_ordered = np.random.randint(100, 1000)
    quantity_received = quantity_ordered
    defect_quantity = int(quantity_ordered * np.random.uniform(0, perf['defect_rate']))
    unit_price = sku_data['Unit_Cost'] * np.random.uniform(0.9, 1.1)
    payment_terms = np.random.choice(PAYMENT_TERMS)
    
    vendor_records.append({
        'Vendor_ID': vendor_id,
        'Vendor_Name': vendor_name,
        'SKU_ID': sku_id,
        'Order_Date': order_date.strftime('%Y-%m-%d'),
        'Promised_Delivery_Date': promised_delivery.strftime('%Y-%m-%d'),
        'Actual_Delivery_Date': actual_delivery.strftime('%Y-%m-%d'),
        'Quantity_Ordered': quantity_ordered,
        'Quantity_Received': quantity_received,
        'Unit_Price': round(unit_price, 2),
        'Defect_Quantity': defect_quantity,
        'Payment_Terms': payment_terms
    })

df_vendor = pd.DataFrame(vendor_records)
print(f"✅ Vendor records: {len(df_vendor)}")

# 4. PURCHASE ORDERS
print("\n" + "="*60)
print("💰 GENERATING PURCHASE ORDERS...")
print("="*60)

purchase_orders = []
po_statuses = ['Closed', 'Open', 'Delayed']

for po_num in range(1, 401):
    po_id = f"PO_{po_num:06d}"
    
    if np.random.random() < 0.75 and len(df_vendor) > 0:
        vendor_record = df_vendor.sample(n=1, random_state=po_num).iloc[0]
        vendor_id = vendor_record['Vendor_ID']
        sku_id = vendor_record['SKU_ID']
        po_date = pd.to_datetime(vendor_record['Order_Date'])
        po_quantity = vendor_record['Quantity_Ordered']
        unit_price = vendor_record['Unit_Price']
    else:
        vendor_id = f"VEN_{np.random.randint(1, 301):04d}"
        sku_data = sku_master[np.random.randint(0, len(sku_master))]
        sku_id = sku_data['SKU_ID']
        days_offset = np.random.randint(0, (END_DATE - START_DATE).days)
        po_date = START_DATE + timedelta(days=days_offset)
        po_quantity = np.random.randint(100, 1000)
        unit_price = sku_data['Unit_Cost'] * np.random.uniform(0.9, 1.1)
    
    po_value = round(po_quantity * unit_price, 2)
    days_since_po = (END_DATE - po_date).days
    
    if days_since_po > 30:
        status = np.random.choice(['Closed', 'Delayed'], p=[0.8, 0.2])
    elif days_since_po > 15:
        status = np.random.choice(['Closed', 'Open'], p=[0.6, 0.4])
    else:
        status = 'Open'
    
    purchase_orders.append({
        'PO_ID': po_id,
        'Vendor_ID': vendor_id,
        'SKU_ID': sku_id,
        'PO_Date': po_date.strftime('%Y-%m-%d'),
        'PO_Quantity': po_quantity,
        'PO_Value': po_value,
        'Status': status
    })

df_po = pd.DataFrame(purchase_orders)
print(f"✅ Purchase orders: {len(df_po)}")

# SAVE FILES
print("\n" + "="*60)
print("💾 SAVING FILES...")
print("="*60)

import os
os.makedirs('data', exist_ok=True)

df_inventory.to_csv('data/inventory_data.csv', index=False)
df_sales.to_csv('data/sales_orders.csv', index=False)
df_vendor.to_csv('data/vendor_data.csv', index=False)
df_po.to_csv('data/purchase_orders.csv', index=False)

print("\n✅ ALL FILES SAVED!")
print(f"   📄 data/inventory_data.csv ({len(df_inventory)} rows)")
print(f"   📄 data/sales_orders.csv ({len(df_sales)} rows)")
print(f"   📄 data/vendor_data.csv ({len(df_vendor)} rows)")
print(f"   📄 data/purchase_orders.csv ({len(df_po)} rows)")
print("\n" + "="*60)
print("✅ GENERATION COMPLETE!")
print("="*60)