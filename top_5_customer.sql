WITH LastYearOrders AS (
    SELECT
        o.customer_id,
        oi.product_id,
        SUM(oi.quantity * oi.price_per_unit) AS total_spent
    FROM
        Orders o
    JOIN
        Order_Items oi ON o.order_id = oi.order_id
    WHERE
        o.order_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    GROUP BY
        o.customer_id, oi.product_id
),
CustomerTotalSpent AS (
    SELECT
        lyo.customer_id,
        c.customer_name,
        c.email,
        SUM(lyo.total_spent) AS total_spent
    FROM
        LastYearOrders lyo
    JOIN
        Customers c ON lyo.customer_id = c.customer_id
    GROUP BY
        lyo.customer_id, c.customer_name, c.email
),
CustomerCategorySpent AS (
    SELECT
        lyo.customer_id,
        p.category,
        SUM(lyo.total_spent) AS category_spent
    FROM
        LastYearOrders lyo
    JOIN
        Products p ON lyo.product_id = p.product_id
    GROUP BY
        lyo.customer_id, p.category
),
CustomerMostPurchasedCategory AS (
    SELECT
        ccs.customer_id,
        ccs.category AS most_purchased_category
    FROM
        CustomerCategorySpent ccs
    JOIN (
        SELECT
            customer_id,
            MAX(category_spent) AS max_spent
        FROM
            CustomerCategorySpent
        GROUP BY
            customer_id
    ) max_spent_per_category ON ccs.customer_id = max_spent_per_category.customer_id
    AND ccs.category_spent = max_spent_per_category.max_spent
)
SELECT
    cts.customer_id,
    cts.customer_name,
    cts.email,
    cts.total_spent,
    cmpc.most_purchased_category
FROM
    CustomerTotalSpent cts
JOIN
    CustomerMostPurchasedCategory cmpc ON cts.customer_id = cmpc.customer_id
ORDER BY
    cts.total_spent DESC
LIMIT 5;
