"""
Test SQL Queries using SQLite
"""

import sqlite3
import pandas as pd

print("="*60)
print("LOADING DATA INTO SQLite DATABASE")
print("="*60)

# Create SQLite database
conn = sqlite3.connect('data/sarovar_analytics.db')

# Load CSV files
df_inventory = pd.read_csv('data/inventory_data.csv')
df_sales = pd.read_csv('data/sales_orders.csv')
df_vendor = pd.read_csv('data/vendor_data.csv')
df_po = pd.read_csv('data/purchase_orders.csv')

# Load into SQLite
df_inventory.to_sql('inventory_data', conn, if_exists='replace', index=False)
df_sales.to_sql('sales_orders', conn, if_exists='replace', index=False)
df_vendor.to_sql('vendor_data', conn, if_exists='replace', index=False)
df_po.to_sql('purchase_orders', conn, if_exists='replace', index=False)

print("✅ Data loaded into database!")
print("\nTables created:")
print("  - inventory_data")
print("  - sales_orders")
print("  - vendor_data")
print("  - purchase_orders")

# Test Query 1: Inventory Turnover
print("\n" + "="*60)
print("QUERY 1: INVENTORY TURNOVER RATIO")
print("="*60)

query1 = """
SELECT 
    SKU_ID,
    Product_Name,
    Category,
    ROUND((SELECT SUM(Quantity_Delivered * Unit_Cost) 
           FROM sales_orders s 
           INNER JOIN inventory_data i2 ON s.SKU_ID = i2.SKU_ID 
           WHERE i2.SKU_ID = i.SKU_ID AND Order_Status = 'Completed') / 
          AVG(Closing_Stock), 2) AS Turnover_Ratio
FROM inventory_data i
GROUP BY SKU_ID, Product_Name, Category
HAVING AVG(Closing_Stock) > 0
ORDER BY Turnover_Ratio DESC
LIMIT 10;
"""

result = pd.read_sql_query(query1, conn)
print(result)

# Test Query 3: Stockout Risk
print("\n" + "="*60)
print("QUERY 3: STOCKOUT RISK ITEMS")
print("="*60)

query3 = """
SELECT 
    SKU_ID,
    Product_Name,
    Category,
    Closing_Stock,
    Safety_Stock,
    (Safety_Stock - Closing_Stock) AS Deficit
FROM inventory_data
WHERE Closing_Stock < Safety_Stock
ORDER BY Deficit DESC
LIMIT 10;
"""

result3 = pd.read_sql_query(query3, conn)
print(result3)

# Test Query 5: Vendor On-Time Delivery
print("\n" + "="*60)
print("QUERY 5: VENDOR ON-TIME DELIVERY %")
print("="*60)

query5 = """
SELECT 
    Vendor_Name,
    COUNT(*) AS Total_Orders,
    ROUND(SUM(CASE WHEN Actual_Delivery_Date <= Promised_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS OnTime_Percentage
FROM vendor_data
GROUP BY Vendor_Name
ORDER BY OnTime_Percentage DESC;
"""

result5 = pd.read_sql_query(query5, conn)
print(result5)

conn.close()

print("\n" + "="*60)
print("✅ SQL QUERIES TESTED SUCCESSFULLY!")
print("="*60)