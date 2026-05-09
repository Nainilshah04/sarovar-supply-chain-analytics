/*
================================================================================
SAROVAR ENTERPRISES - SUPPLY CHAIN ANALYTICS SQL QUERIES
================================================================================
Author: Your Name
Date: 2024
Description: 10 Advanced SQL queries for inventory optimization, vendor 
             performance analysis, and demand forecasting
================================================================================
*/

-- ============================================================================
-- QUERY 1: INVENTORY TURNOVER RATIO PER SKU
-- ============================================================================
/*
Purpose: Calculate how many times inventory is sold and replaced over a period
Formula: COGS / Average Inventory
Higher ratio = Better inventory management
*/

WITH inventory_metrics AS (
    SELECT 
        i.SKU_ID,
        i.Product_Name,
        i.Category,
        AVG(i.Closing_Stock) AS avg_inventory,
        SUM(s.Quantity_Delivered * i.Unit_Cost) AS total_cogs
    FROM inventory_data i
    LEFT JOIN sales_orders s ON i.SKU_ID = s.SKU_ID
    WHERE s.Order_Status = 'Completed'
    GROUP BY i.SKU_ID, i.Product_Name, i.Category
)
SELECT 
    SKU_ID,
    Product_Name,
    Category,
    ROUND(avg_inventory, 2) AS Average_Inventory_Units,
    ROUND(total_cogs, 2) AS Total_COGS,
    ROUND(
        CASE 
            WHEN avg_inventory > 0 THEN total_cogs / avg_inventory 
            ELSE 0 
        END, 
        2
    ) AS Inventory_Turnover_Ratio,
    -- Performance classification
    CASE 
        WHEN total_cogs / NULLIF(avg_inventory, 0) > 20 THEN 'Excellent'
        WHEN total_cogs / NULLIF(avg_inventory, 0) > 10 THEN 'Good'
        WHEN total_cogs / NULLIF(avg_inventory, 0) > 5 THEN 'Average'
        ELSE 'Poor'
    END AS Performance_Rating
FROM inventory_metrics
WHERE avg_inventory > 0
ORDER BY Inventory_Turnover_Ratio DESC;


-- ============================================================================
-- QUERY 2: DAYS OF INVENTORY OUTSTANDING (DIO) PER CATEGORY
-- ============================================================================
/*
Purpose: Measures how long inventory sits before being sold
Formula: (Average Inventory / COGS) * 365
Lower DIO = Faster inventory movement
*/

WITH category_metrics AS (
    SELECT 
        i.Category,
        AVG(i.Closing_Stock) AS avg_inventory,
        SUM(s.Quantity_Delivered * i.Unit_Cost) / 365.0 AS daily_cogs
    FROM inventory_data i
    LEFT JOIN sales_orders s ON i.SKU_ID = s.SKU_ID
    WHERE s.Order_Status = 'Completed'
    GROUP BY i.Category
)
SELECT 
    Category,
    ROUND(avg_inventory, 2) AS Average_Inventory,
    ROUND(daily_cogs * 365, 2) AS Annual_COGS,
    ROUND(
        CASE 
            WHEN daily_cogs > 0 THEN avg_inventory / daily_cogs 
            ELSE 0 
        END, 
        1
    ) AS Days_Inventory_Outstanding,
    -- Health indicator
    CASE 
        WHEN avg_inventory / NULLIF(daily_cogs, 0) < 30 THEN '🟢 Fast Moving'
        WHEN avg_inventory / NULLIF(daily_cogs, 0) < 60 THEN '🟡 Moderate'
        ELSE '🔴 Slow Moving'
    END AS Movement_Status
FROM category_metrics
ORDER BY Days_Inventory_Outstanding ASC;


-- ============================================================================
-- QUERY 3: STOCKOUT RISK ITEMS
-- ============================================================================
/*
Purpose: Identify SKUs where closing stock is below safety stock threshold
Critical for preventing sales loss and customer dissatisfaction
*/

SELECT 
    SKU_ID,
    Product_Name,
    Category,
    Warehouse_Location,
    Date,
    Closing_Stock,
    Safety_Stock,
    Reorder_Point,
    (Safety_Stock - Closing_Stock) AS Stock_Deficit,
    ROUND(
        (Closing_Stock * 1.0 / NULLIF(Safety_Stock, 0)) * 100, 
        1
    ) AS Stock_Level_Percentage,
    -- Urgency classification
    CASE 
        WHEN Closing_Stock = 0 THEN '🚨 CRITICAL - Out of Stock'
        WHEN Closing_Stock < Safety_Stock * 0.5 THEN '🔴 HIGH - Immediate Reorder'
        WHEN Closing_Stock < Safety_Stock THEN '🟠 MEDIUM - Monitor Closely'
        ELSE '🟢 SAFE'
    END AS Risk_Level
FROM inventory_data
WHERE Closing_Stock < Safety_Stock
ORDER BY 
    CASE 
        WHEN Closing_Stock = 0 THEN 1
        WHEN Closing_Stock < Safety_Stock * 0.5 THEN 2
        ELSE 3
    END,
    Stock_Level_Percentage ASC;


-- ============================================================================
-- QUERY 4: OVERSTOCK ITEMS
-- ============================================================================
/*
Purpose: Identify items with excess inventory (>3x reorder point)
Helps reduce carrying costs and free up warehouse space
*/

SELECT 
    SKU_ID,
    Product_Name,
    Category,
    Warehouse_Location,
    Date,
    Closing_Stock,
    Reorder_Point,
    (Closing_Stock - Reorder_Point) AS Excess_Stock,
    ROUND(
        (Closing_Stock * 1.0 / NULLIF(Reorder_Point, 0)), 
        2
    ) AS Overstock_Multiplier,
    ROUND(
        (Closing_Stock - Reorder_Point) * Unit_Cost, 
        2
    ) AS Excess_Inventory_Value,
    -- Action recommendation
    CASE 
        WHEN Closing_Stock > Reorder_Point * 5 THEN '🔴 URGENT - Consider Liquidation'
        WHEN Closing_Stock > Reorder_Point * 4 THEN '🟠 HIGH - Promotional Sale'
        WHEN Closing_Stock > Reorder_Point * 3 THEN '🟡 MODERATE - Slow Procurement'
        ELSE '🟢 NORMAL'
    END AS Action_Required
FROM inventory_data
WHERE Closing_Stock > Reorder_Point * 3
ORDER BY Excess_Inventory_Value DESC;


-- ============================================================================
-- QUERY 5: VENDOR ON-TIME DELIVERY PERCENTAGE
-- ============================================================================
/*
Purpose: Calculate percentage of orders delivered on or before promised date
Key metric for vendor reliability assessment
*/

WITH vendor_delivery_performance AS (
    SELECT 
        Vendor_Name,
        COUNT(*) AS Total_Orders,
        SUM(
            CASE 
                WHEN Actual_Delivery_Date <= Promised_Delivery_Date THEN 1 
                ELSE 0 
            END
        ) AS On_Time_Deliveries,
        SUM(
            CASE 
                WHEN Actual_Delivery_Date > Promised_Delivery_Date THEN 1 
                ELSE 0 
            END
        ) AS Late_Deliveries,
        ROUND(
            AVG(
                JULIANDAY(Actual_Delivery_Date) - JULIANDAY(Promised_Delivery_Date)
            ), 
            1
        ) AS Avg_Delay_Days
    FROM vendor_data
    GROUP BY Vendor_Name
)
SELECT 
    Vendor_Name,
    Total_Orders,
    On_Time_Deliveries,
    Late_Deliveries,
    ROUND(
        (On_Time_Deliveries * 100.0 / Total_Orders), 
        2
    ) AS On_Time_Delivery_Percentage,
    Avg_Delay_Days,
    -- Performance grade
    CASE 
        WHEN (On_Time_Deliveries * 100.0 / Total_Orders) >= 90 THEN '🟢 A - Excellent'
        WHEN (On_Time_Deliveries * 100.0 / Total_Orders) >= 80 THEN '🟡 B - Good'
        WHEN (On_Time_Deliveries * 100.0 / Total_Orders) >= 70 THEN '🟠 C - Average'
        ELSE '🔴 D - Poor'
    END AS Performance_Grade
FROM vendor_delivery_performance
ORDER BY On_Time_Delivery_Percentage DESC;


-- ============================================================================
-- QUERY 6: VENDOR DEFECT RATE PERCENTAGE
-- ============================================================================
/*
Purpose: Calculate percentage of defective items received from each vendor
Critical for quality control and vendor evaluation
*/

WITH vendor_quality_metrics AS (
    SELECT 
        Vendor_Name,
        SUM(Quantity_Received) AS Total_Quantity_Received,
        SUM(Defect_Quantity) AS Total_Defects,
        COUNT(DISTINCT SKU_ID) AS SKUs_Supplied,
        ROUND(AVG(Unit_Price), 2) AS Avg_Unit_Price
    FROM vendor_data
    GROUP BY Vendor_Name
)
SELECT 
    Vendor_Name,
    Total_Quantity_Received,
    Total_Defects,
    SKUs_Supplied,
    Avg_Unit_Price,
    ROUND(
        (Total_Defects * 100.0 / NULLIF(Total_Quantity_Received, 0)), 
        2
    ) AS Defect_Rate_Percentage,
    -- Quality classification
    CASE 
        WHEN (Total_Defects * 100.0 / NULLIF(Total_Quantity_Received, 0)) < 2 THEN '🟢 Premium Quality'
        WHEN (Total_Defects * 100.0 / NULLIF(Total_Quantity_Received, 0)) < 5 THEN '🟡 Acceptable'
        WHEN (Total_Defects * 100.0 / NULLIF(Total_Quantity_Received, 0)) < 8 THEN '🟠 Needs Improvement'
        ELSE '🔴 Unacceptable - Review Contract'
    END AS Quality_Status,
    -- Financial impact
    ROUND(Total_Defects * Avg_Unit_Price, 2) AS Estimated_Defect_Loss
FROM vendor_quality_metrics
ORDER BY Defect_Rate_Percentage DESC;


-- ============================================================================
-- QUERY 7: TOP 5 SKUs BY TOTAL REVENUE
-- ============================================================================
/*
Purpose: Identify best-selling products by revenue generation
Helps prioritize inventory management and procurement
*/

WITH sku_revenue AS (
    SELECT 
        s.SKU_ID,
        i.Product_Name,
        i.Category,
        SUM(s.Quantity_Delivered) AS Total_Units_Sold,
        AVG(i.Unit_Cost) AS Avg_Unit_Cost,
        SUM(s.Quantity_Delivered * i.Unit_Cost) AS Total_Revenue
    FROM sales_orders s
    INNER JOIN inventory_data i ON s.SKU_ID = i.SKU_ID
    WHERE s.Order_Status = 'Completed'
    GROUP BY s.SKU_ID, i.Product_Name, i.Category
)
SELECT 
    SKU_ID,
    Product_Name,
    Category,
    Total_Units_Sold,
    ROUND(Avg_Unit_Cost, 2) AS Avg_Unit_Cost,
    ROUND(Total_Revenue, 2) AS Total_Revenue,
    ROUND(
        (Total_Revenue * 100.0 / (SELECT SUM(Total_Revenue) FROM sku_revenue)), 
        2
    ) AS Revenue_Contribution_Percentage,
    -- ABC classification
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY Total_Revenue DESC) <= 5 THEN 'A - Top Revenue Generator'
        WHEN ROW_NUMBER() OVER (ORDER BY Total_Revenue DESC) <= 15 THEN 'B - Moderate Revenue'
        ELSE 'C - Low Revenue'
    END AS ABC_Classification
FROM sku_revenue
ORDER BY Total_Revenue DESC
LIMIT 5;


-- ============================================================================
-- QUERY 8: MONTH-OVER-MONTH DEMAND GROWTH (Using Window Functions)
-- ============================================================================
/*
Purpose: Analyze demand trends using LAG function to compare month-over-month
Identifies seasonal patterns and growth trends
*/

WITH monthly_demand AS (
    SELECT 
        STRFTIME('%Y-%m', Order_Date) AS Month,
        Category,
        SUM(Quantity_Ordered) AS Total_Demand
    FROM sales_orders s
    INNER JOIN inventory_data i ON s.SKU_ID = i.SKU_ID
    GROUP BY STRFTIME('%Y-%m', Order_Date), Category
),
demand_with_previous AS (
    SELECT 
        Month,
        Category,
        Total_Demand,
        LAG(Total_Demand, 1) OVER (
            PARTITION BY Category 
            ORDER BY Month
        ) AS Previous_Month_Demand
    FROM monthly_demand
)
SELECT 
    Month,
    Category,
    Total_Demand AS Current_Month_Demand,
    COALESCE(Previous_Month_Demand, 0) AS Previous_Month_Demand,
    ROUND(
        CASE 
            WHEN Previous_Month_Demand > 0 
            THEN ((Total_Demand - Previous_Month_Demand) * 100.0 / Previous_Month_Demand)
            ELSE 0 
        END, 
        2
    ) AS MoM_Growth_Percentage,
    -- Trend indicator
    CASE 
        WHEN ((Total_Demand - Previous_Month_Demand) * 100.0 / NULLIF(Previous_Month_Demand, 0)) > 20 THEN '📈 High Growth'
        WHEN ((Total_Demand - Previous_Month_Demand) * 100.0 / NULLIF(Previous_Month_Demand, 0)) > 0 THEN '🟢 Positive Growth'
        WHEN ((Total_Demand - Previous_Month_Demand) * 100.0 / NULLIF(Previous_Month_Demand, 0)) < -20 THEN '📉 Significant Decline'
        WHEN ((Total_Demand - Previous_Month_Demand) * 100.0 / NULLIF(Previous_Month_Demand, 0)) < 0 THEN '🔴 Decline'
        ELSE '➡️ Stable'
    END AS Trend
FROM demand_with_previous
WHERE Previous_Month_Demand IS NOT NULL
ORDER BY Month DESC, Category;


-- ============================================================================
-- QUERY 9: VENDOR COMPOSITE PERFORMANCE SCORE
-- ============================================================================
/*
Purpose: Calculate overall vendor score with weighted metrics
Weightage: 50% On-Time Delivery, 30% Quality (Defect Rate), 20% Price Competitiveness
*/

WITH vendor_metrics AS (
    SELECT 
        v.Vendor_Name,
        -- On-Time Delivery Score (50% weight)
        ROUND(
            (SUM(CASE WHEN Actual_Delivery_Date <= Promised_Delivery_Date THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
            2
        ) AS OnTime_Percentage,
        
        -- Quality Score (30% weight) - Inverse of defect rate
        ROUND(
            100 - (SUM(Defect_Quantity) * 100.0 / NULLIF(SUM(Quantity_Received), 0)), 
            2
        ) AS Quality_Score,
        
        -- Price Competitiveness (20% weight)
        AVG(Unit_Price) AS Avg_Price
    FROM vendor_data v
    GROUP BY v.Vendor_Name
),
price_ranking AS (
    SELECT 
        *,
        -- Normalize price score (lower price = higher score)
        ROUND(
            100 - ((Avg_Price - MIN(Avg_Price) OVER ()) * 100.0 / 
            NULLIF((MAX(Avg_Price) OVER () - MIN(Avg_Price) OVER ()), 0)),
            2
        ) AS Price_Score
    FROM vendor_metrics
)
SELECT 
    Vendor_Name,
    OnTime_Percentage,
    Quality_Score,
    ROUND(Avg_Price, 2) AS Avg_Unit_Price,
    Price_Score,
    ROUND(
        (OnTime_Percentage * 0.5) + 
        (Quality_Score * 0.3) + 
        (Price_Score * 0.2),
        2
    ) AS Composite_Performance_Score,
    -- Overall rating
    CASE 
        WHEN ((OnTime_Percentage * 0.5) + (Quality_Score * 0.3) + (Price_Score * 0.2)) >= 85 THEN '🟢 Preferred Vendor'
        WHEN ((OnTime_Percentage * 0.5) + (Quality_Score * 0.3) + (Price_Score * 0.2)) >= 70 THEN '🟡 Approved Vendor'
        WHEN ((OnTime_Percentage * 0.5) + (Quality_Score * 0.3) + (Price_Score * 0.2)) >= 50 THEN '🟠 Conditional Approval'
        ELSE '🔴 Under Review'
    END AS Vendor_Status
FROM price_ranking
ORDER BY Composite_Performance_Score DESC;


-- ============================================================================
-- QUERY 10: SKUs WITH CONSISTENT STOCKOUT (Stockout in >3 Months)
-- ============================================================================
/*
Purpose: Identify chronic inventory problems requiring strategic intervention
SKUs with repeated stockouts indicate procurement or forecasting issues
*/

WITH monthly_stockouts AS (
    SELECT 
        SKU_ID,
        Product_Name,
        Category,
        STRFTIME('%Y-%m', Date) AS Month,
        CASE 
            WHEN Closing_Stock < Safety_Stock THEN 1 
            ELSE 0 
        END AS Is_Stockout
    FROM inventory_data
),
stockout_frequency AS (
    SELECT 
        SKU_ID,
        Product_Name,
        Category,
        SUM(Is_Stockout) AS Months_With_Stockout,
        COUNT(DISTINCT Month) AS Total_Months_Tracked
    FROM monthly_stockouts
    GROUP BY SKU_ID, Product_Name, Category
)
SELECT 
    sf.SKU_ID,
    sf.Product_Name,
    sf.Category,
    sf.Months_With_Stockout,
    sf.Total_Months_Tracked,
    ROUND(
        (sf.Months_With_Stockout * 100.0 / sf.Total_Months_Tracked), 
        1
    ) AS Stockout_Frequency_Percentage,
    i.Reorder_Point,
    i.Safety_Stock,
    AVG(i.Closing_Stock) AS Avg_Closing_Stock,
    -- Recommended action
    CASE 
        WHEN sf.Months_With_Stockout >= 6 THEN '🔴 CRITICAL - Revise Reorder Point & Safety Stock'
        WHEN sf.Months_With_Stockout >= 4 THEN '🟠 HIGH - Increase Safety Stock by 50%'
        WHEN sf.Months_With_Stockout >= 3 THEN '🟡 MEDIUM - Review Supplier Lead Time'
        ELSE '🟢 ACCEPTABLE'
    END AS Recommended_Action
FROM stockout_frequency sf
INNER JOIN inventory_data i ON sf.SKU_ID = i.SKU_ID
WHERE sf.Months_With_Stockout > 3
GROUP BY sf.SKU_ID, sf.Product_Name, sf.Category, sf.Months_With_Stockout, 
         sf.Total_Months_Tracked, i.Reorder_Point, i.Safety_Stock
ORDER BY sf.Months_With_Stockout DESC, Stockout_Frequency_Percentage DESC;


-- ============================================================================
-- END OF QUERIES
-- ============================================================================