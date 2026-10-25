-- Retail Sales Analytics: example SQL analysis queries
-- Table name assumed: retail_sales_clean

-- 1. Monthly revenue and profit
SELECT
    DATE_TRUNC('month', Order_Date) AS month,
    SUM(Revenue) AS revenue,
    SUM(Profit) AS profit,
    COUNT(DISTINCT Order_ID) AS orders
FROM retail_sales_clean
GROUP BY 1
ORDER BY 1;

-- 2. Category performance
SELECT
    Category,
    SUM(Revenue) AS revenue,
    SUM(Profit) AS profit,
    SUM(Quantity) AS units_sold
FROM retail_sales_clean
GROUP BY Category
ORDER BY revenue DESC;

-- 3. Channel performance
SELECT
    Sales_Channel,
    SUM(Revenue) AS revenue,
    SUM(Profit) AS profit,
    COUNT(DISTINCT Order_ID) AS orders
FROM retail_sales_clean
GROUP BY Sales_Channel
ORDER BY revenue DESC;

-- 4. Regional performance
SELECT
    Region,
    SUM(Revenue) AS revenue,
    SUM(Profit) AS profit
FROM retail_sales_clean
GROUP BY Region
ORDER BY profit DESC;

-- 5. Discount impact (descriptive, not causal)
SELECT
    CASE
        WHEN Discount = 0 THEN 'No discount'
        WHEN Discount <= 0.05 THEN '1-5%'
        WHEN Discount <= 0.10 THEN '6-10%'
        WHEN Discount <= 0.15 THEN '11-15%'
        ELSE 'Above 15%'
    END AS discount_band,
    AVG(Revenue) AS average_order_revenue,
    AVG(Profit) AS average_order_profit,
    COUNT(*) AS order_lines
FROM retail_sales_clean
GROUP BY 1
ORDER BY 1;
