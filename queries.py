# -------------------------
# Blinkit SQL Queries
# -------------------------

# Total Revenue
total_revenue_query = """
SELECT SUM(order_total) AS revenue 
FROM blinkit_orders;
"""

# Top Products
top_products_query = """
SELECT 
    p.product_name, 
    SUM(oi.quantity) AS total_sold
FROM blinkit_order_items oi
JOIN blinkit_products p 
    ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 10;
"""

# Delayed Orders
delayed_orders_query = """
SELECT COUNT(*) AS delayed_orders
FROM blinkit_delivery_performance
WHERE delivery_status LIKE '%delayed%';
"""

# Low Stock
low_stock_query = """
SELECT 
    product_name, 
    min_stock_level
FROM blinkit_products
WHERE min_stock_level > 50;
"""



# Area-wise Customer Distribution :

area_distribution_query = """
SELECT 
    area,
    COUNT(*) AS total_customers
FROM blinkit_customers
GROUP BY area
ORDER BY total_customers DESC;
"""

# Top Revenue Products
top_revenue_products_query = """
SELECT 
    p.product_name,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM blinkit_order_items oi
JOIN blinkit_products p 
ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 10;
"""

# Daily Revenue
daily_revenue_query = """
SELECT 
    order_date,
    SUM(order_total) AS revenue
FROM blinkit_orders
GROUP BY order_date
ORDER BY order_date;
"""

# Repeat vs New Customers

repeat_customers_query = """
SELECT 
    CASE 
        WHEN total_orders = 1 THEN 'New'
        ELSE 'Repeat'
    END AS customer_type,
    COUNT(*) AS total
FROM blinkit_customers
GROUP BY customer_type;
"""

# Campaign Performance
campaign_performance_query = """
SELECT 
    campaign_name,
    spend,
    revenue_generated,
    (revenue_generated / spend) AS roas
FROM blinkit_marketing_performance
ORDER BY roas DESC;
"""

# Avg Order Value per Customer
avg_order_value_query = """
SELECT c.customer_name, AVG(o.order_total) AS avg_value
FROM blinkit_orders o
JOIN blinkit_customers c 
ON o.customer_id = c.customer_id
GROUP BY c.customer_name;
"""


# Most Expensive Products
expensive_products_query = """
SELECT product_name, price
FROM blinkit_products
ORDER BY price DESC
LIMIT 10;
"""

# Cheapest Products
cheap_products_query = """
SELECT product_name, price
FROM blinkit_products
ORDER BY price ASC
LIMIT 10;
"""


# Customers with No Orders
inactive_customers_query = """
SELECT customer_name
FROM blinkit_customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id FROM blinkit_orders
);
"""

# Best Campaign by Revenue
best_campaign_query = """
SELECT campaign_name, revenue_generated
FROM blinkit_marketing_performance
ORDER BY revenue_generated DESC
LIMIT 1;
"""

# Click Through Rate (CTR)
ctr_query = """
SELECT campaign_name,
(clicks / impressions) AS ctr
FROM blinkit_marketing_performance;
"""


# Top 3 Products per Category
top_products_per_category_query = """
SELECT *
FROM (
    SELECT p.category, p.product_name,
    SUM(oi.quantity) AS total_sold,
    RANK() OVER (PARTITION BY p.category ORDER BY SUM(oi.quantity) DESC) AS rnk
    FROM blinkit_order_items oi
    JOIN blinkit_products p
    ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_name
) t
WHERE rnk <= 3;
"""

# Row number per category

row_number_per_category_query = """
SELECT product_name, category,
ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS row_num
FROM blinkit_products;
"""

# Dense Rank Products by Sales

dense_rank_products_query = """
SELECT product_name, total_sold,
DENSE_RANK() OVER (ORDER BY total_sold DESC) AS rank_pos
FROM (
    SELECT p.product_name, SUM(oi.quantity) AS total_sold
    FROM blinkit_order_items oi
    JOIN blinkit_products p 
    ON oi.product_id = p.product_id
    GROUP BY p.product_name
) t;
"""

# Lag Function to Compare Current and Previous Order Totals
lag_order_totals_query = """
SELECT order_id, order_total,
LAG(order_total) OVER (ORDER BY order_date) AS prev_order
FROM blinkit_orders;
"""

# Top 20% Customers by Spending using NTILE

top_customers_ntile_query = """
SELECT customer_name, total_spent
FROM (
    SELECT c.customer_name,
    SUM(o.order_total) AS total_spent,
    NTILE(5) OVER (ORDER BY SUM(o.order_total) DESC) AS bucket
    FROM blinkit_orders o
    JOIN blinkit_customers c 
    ON o.customer_id = c.customer_id
    GROUP BY c.customer_name
) t
WHERE bucket = 1;
"""


# Cohort Analysis: Customer Retention by Cohort Month

cohort_analysis_query = """
WITH first_order AS (
    SELECT customer_id, MIN(DATE_FORMAT(order_date, '%Y-%m')) AS cohort_month
    FROM blinkit_orders
    GROUP BY customer_id
),
activity AS (
    SELECT customer_id, DATE_FORMAT(order_date, '%Y-%m') AS order_month
    FROM blinkit_orders
)
SELECT 
    f.cohort_month,
    a.order_month,
    COUNT(DISTINCT a.customer_id) AS active_customers
FROM first_order f
JOIN activity a 
ON f.customer_id = a.customer_id
GROUP BY f.cohort_month, a.order_month
ORDER BY f.cohort_month, a.order_month;
"""

# top category contribution to revenue

contribution_category_revenue_query = """
SELECT category, revenue,
ROUND(revenue / SUM(revenue) OVER () * 100, 2) AS contribution_percent
FROM (
    SELECT p.category,
    SUM(oi.quantity * oi.unit_price) AS revenue
    FROM blinkit_order_items oi
    JOIN blinkit_products p 
    ON oi.product_id = p.product_id
    GROUP BY p.category
) t;
"""

# RFM Analysis: Recency, Frequency, Monetary Value per Customer

rfm_analysis_query = """
SELECT customer_id,
DATEDIFF(CURDATE(), MAX(order_date)) AS recency,
COUNT(order_id) AS frequency,
SUM(order_total) AS monetary
FROM blinkit_orders
GROUP BY customer_id;
"""

# Product Pairing: Top 10 Most Frequently Bought Together Products

product_pairing_query = """
SELECT 
    p1.product_name AS product_1,
    p2.product_name AS product_2,
    COUNT(*) AS frequency
FROM blinkit_order_items oi1
JOIN blinkit_order_items oi2 
ON oi1.order_id = oi2.order_id 
AND oi1.product_id < oi2.product_id
JOIN blinkit_products p1 
ON oi1.product_id = p1.product_id
JOIN blinkit_products p2 
ON oi2.product_id = p2.product_id
GROUP BY product_1, product_2
ORDER BY frequency DESC
LIMIT 10;
"""

# Cohort Analysis with Retention Rate

cohort_analysis_retention_query = """
WITH cohort AS (
    SELECT customer_id,
           DATE_FORMAT(MIN(order_date), '%Y-%m') AS cohort_month
    FROM blinkit_orders
    GROUP BY customer_id
),
activity AS (
    SELECT customer_id,
           DATE_FORMAT(order_date, '%Y-%m') AS order_month
    FROM blinkit_orders
),
retention AS (
    SELECT c.cohort_month,
           a.order_month,
           COUNT(DISTINCT a.customer_id) AS users
    FROM cohort c
    JOIN activity a
    ON c.customer_id = a.customer_id
    GROUP BY c.cohort_month, a.order_month
)
SELECT *,
ROUND(users * 100.0 /
FIRST_VALUE(users) OVER (PARTITION BY cohort_month ORDER BY order_month),2) AS retention_rate
FROM retention;
"""

# Product Pairing: Top 10 Most Frequently Bought Together Products

product_pairing_query = """
SELECT p1.product_name, p2.product_name, COUNT(*) AS freq
FROM blinkit_order_items oi1
JOIN blinkit_order_items oi2 
ON oi1.order_id = oi2.order_id
AND oi1.product_id <> oi2.product_id
JOIN blinkit_products p1 
ON oi1.product_id = p1.product_id
JOIN blinkit_products p2 
ON oi2.product_id = p2.product_id
GROUP BY p1.product_name, p2.product_name
ORDER BY freq DESC
LIMIT 10;
"""

# Customer Purchase Sequences: Analyze the order of product purchases by customers

customer_purchase_sequence_query = """
SELECT customer_id,
GROUP_CONCAT(product_id ORDER BY order_date) AS purchase_sequence
FROM blinkit_orders o
JOIN blinkit_order_items oi 
ON o.order_id = oi.order_id
GROUP BY customer_id;"""



# Revenue Growth and Acceleration: Calculate daily revenue growth and acceleration

revenue_growth_acceleration_query = """
WITH base AS (
    SELECT order_date,
    SUM(order_total) AS revenue
    FROM blinkit_orders
    GROUP BY order_date
),
lag1 AS (
    SELECT *,
    LAG(revenue) OVER (ORDER BY order_date) AS prev_rev
    FROM base
),
lag2 AS (
    SELECT *,
    (revenue - prev_rev) AS growth,
    LAG(revenue - prev_rev) OVER (ORDER BY order_date) AS prev_growth
    FROM lag1
)
SELECT order_date,
growth,
(growth - prev_growth) AS acceleration
FROM lag2;"""

# Top Customers by Revenue
top_customers_query = """
SELECT c.name AS customer_name, SUM(o.order_total) AS total_spent
FROM blinkit_orders o
JOIN blinkit_customers c 
ON o.customer_id = c.customer_id
GROUP BY c.name
ORDER BY total_spent DESC
LIMIT 10;
"""

# High Demand, Low Stock Products

high_demand_low_stock_query = """
SELECT p.product_name, SUM(oi.quantity) AS demand, p.min_stock_level
FROM blinkit_products p
JOIN blinkit_order_items oi 
ON p.product_id = oi.product_id
GROUP BY p.product_name, p.min_stock_level
HAVING demand > p.min_stock_level;
"""

# Delivery Performance

delivery_performance_query = """
SELECT delivery_status, COUNT(*) AS total_orders
FROM blinkit_delivery_performance
GROUP BY delivery_status;
"""

sales_prediction_query = """
SELECT 
    order_date,
    SUM(order_total) AS revenue
FROM blinkit_orders
GROUP BY order_date
ORDER BY order_date;
"""

demand_forecast_query = """
SELECT 
    p.product_name,
    SUM(oi.quantity) AS total_sold
FROM blinkit_order_items oi
JOIN blinkit_products p 
    ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 10;
"""

rfm_analysis_query = """
SELECT 
    c.customer_id,
    c.customer_name,
    DATEDIFF(CURDATE(), MAX(o.order_date)) AS recency,
    COUNT(o.order_id) AS frequency,
    SUM(o.order_total) AS monetary_value
FROM blinkit_customers c
JOIN blinkit_orders o 
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;
"""

daily_report_query = """
SELECT 
    order_date,
    COUNT(order_id) AS total_orders,
    SUM(order_total) AS revenue
FROM blinkit_orders
GROUP BY order_date
ORDER BY order_date DESC;
"""

monthly_report_query = """
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    COUNT(order_id) AS total_orders,
    SUM(order_total) AS revenue
FROM blinkit_orders
GROUP BY month
ORDER BY month;
"""


