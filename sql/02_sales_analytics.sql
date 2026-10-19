-- 1. Confirm the table contains data
SELECT COUNT(*) AS row_count
FROM ecommerce_sales;

-- 2. Revenue and units by country
SELECT
    country,
    ROUND(SUM(total_amount), 2) AS gross_sales,
    SUM(quantity) AS units_sold
FROM ecommerce_sales
GROUP BY country
ORDER BY gross_sales DESC
LIMIT 10;

-- 3. Top products by revenue
SELECT
    stock_code,
    MAX(description) AS product_description,
    ROUND(SUM(TRY_CAST(total_amount AS DECIMAL(14,2))), 2)
        AS gross_sales,
    SUM(TRY_CAST(quantity AS INTEGER)) AS units_sold
FROM ecommerce_sales
GROUP BY stock_code
ORDER BY gross_sales DESC
LIMIT 20;



