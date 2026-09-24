import psycopg2

## Bu değeri localinde çalışırken kendi passwordün yap. Ama kodu pushlarken 'postgres' olarak bırak.
password = '1907'

def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password=password
    )

def create_view_completed_orders():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
CREATE OR REPLACE VIEW completed_orders AS 
SELECT * 
FROM data4.orders 
WHERE status = 'completed';""")
            conn.commit()

def create_view_electronics_products():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
CREATE OR REPLACE VIEW electronics_products AS 
SELECT * 
FROM data4.products 
WHERE category = 'Electronics';
""")
            conn.commit()

def total_spending_per_customer():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
WITH customer_spending AS (
    SELECT c.full_name, SUM(p.price * o.quantity) AS total_spending
    FROM data4.customers c
    JOIN data4.orders o 
    ON c.customer_id = o.customer_id
    JOIN data4.products p 
    ON o.product_id = p.product_id
    GROUP BY c.full_name
)
SELECT full_name, total_spending FROM customer_spending;""")
            return cur.fetchall()

def order_details_with_total():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
WITH order_details AS (
    SELECT o.order_id, c.full_name, p.product_name, (p.price * o.quantity) AS total_price
    FROM data4.orders o
    JOIN data4.customers c 
	ON o.customer_id = c.customer_id
    JOIN data4.products p 
	ON o.product_id = p.product_id
)
SELECT order_id, full_name, product_name, total_price FROM order_details;""")
            return cur.fetchall()

def get_customer_who_bought_most_expensive_product():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT c.full_name
FROM data4.customers c
JOIN data4.orders o ON c.customer_id = o.customer_id
WHERE o.product_id = (
    SELECT product_id 
    FROM data4.products 
    ORDER BY price DESC 
    LIMIT 1
)
LIMIT 1;""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 2. Sipariş durumlarına göre açıklama
def get_order_status_descriptions():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
SELECT order_id, status,
	CASE 
		WHEN status = 'completed' THEN 'Tamamlandı'
        WHEN status = 'cancelled' THEN 'İptal Edildi' 
    END AS status_description
FROM data4.orders;""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 3. Ortalama fiyatın üstündeki ürünler
def get_products_above_average_price():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT product_name, price
FROM data4.products
WHERE price > (SELECT AVG(price) FROM data4.products);""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 4. Müşteri kategorileri
def get_customer_categories():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT c.full_name,
    CASE 
        WHEN COUNT(o.order_id) > 5 THEN 'Sadık Müşteri'
        WHEN COUNT(o.order_id) BETWEEN 2 AND 5 THEN 'Orta Seviye'
        ELSE 'Yeni Müşteri'
    END AS customer_category
FROM data4.customers c
LEFT JOIN data4.orders o ON c.customer_id = o.customer_id
GROUP BY c.full_name;""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 5. Son 30 gün içinde sipariş veren müşteriler
def get_recent_customers():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT full_name
FROM data4.customers
WHERE customer_id IN (
    SELECT customer_id 
    FROM data4.orders 
    WHERE order_date >= CURRENT_DATE - 30
);""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 6. En çok sipariş verilen ürün
def get_most_ordered_product():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT p.product_name, COUNT(o.order_id) AS total_orders
FROM data4.products p
JOIN data4.orders o ON p.product_id = o.product_id
GROUP BY p.product_name
ORDER BY total_orders DESC
LIMIT 1;""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 7. Ürün fiyatlarına göre etiketleme
def get_product_price_categories():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT 
    product_name, 
    price,
    CASE 
        WHEN price > 1000 THEN 'Pahalı'
        WHEN price BETWEEN 500 AND 1000 THEN 'Orta'
        ELSE 'Ucuz'
    END AS price_category
FROM data4.products;
""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result