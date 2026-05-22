import pandas as pd
import sqlite3
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH  = os.path.join(os.path.dirname(__file__), '..', 'olist.db')

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    print(f"  Lendo {filename}...")
    return pd.read_csv(path)

def run_pipeline():
    print("=== Pipeline de Dados — E-commerce Brasil (Olist) ===\n")

    orders       = load_csv('olist_orders_dataset.csv')
    items        = load_csv('olist_order_items_dataset.csv')
    payments     = load_csv('olist_order_payments_dataset.csv')
    reviews      = load_csv('olist_order_reviews_dataset.csv')
    customers    = load_csv('olist_customers_dataset.csv')
    products     = load_csv('olist_products_dataset.csv')
    sellers      = load_csv('olist_sellers_dataset.csv')
    translation  = load_csv('product_category_name_translation.csv')

    print("\nProcessando dados...")

    date_cols = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    orders_delivered = orders[orders['order_status'] == 'delivered'].copy()
    orders_delivered['delivery_days'] = (
        orders_delivered['order_delivered_customer_date'] -
        orders_delivered['order_purchase_timestamp']
    ).dt.days

    products = products.merge(translation, on='product_category_name', how='left')
    products['category'] = products['product_category_name_english'].fillna(
        products['product_category_name']
    ).str.replace('_', ' ').str.title()

    revenue_per_order = items.groupby('order_id').agg(
        revenue=('price', 'sum'),
        freight=('freight_value', 'sum'),
        items_count=('order_item_id', 'count')
    ).reset_index()

    avg_review = reviews.groupby('order_id')['review_score'].mean().reset_index()
    avg_review.columns = ['order_id', 'avg_review_score']

    master = orders.merge(customers[['customer_id', 'customer_state', 'customer_city']], on='customer_id', how='left')
    master = master.merge(revenue_per_order, on='order_id', how='left')
    master = master.merge(avg_review, on='order_id', how='left')

    master['year']       = master['order_purchase_timestamp'].dt.year
    master['month']      = master['order_purchase_timestamp'].dt.month
    master['year_month'] = master['order_purchase_timestamp'].dt.to_period('M').astype(str)

    items_enriched = items.merge(
        products[['product_id', 'category']], on='product_id', how='left'
    )

    print(f"\nSalvando no banco de dados: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    master.to_sql('orders', conn, if_exists='replace', index=False)
    items_enriched.to_sql('order_items', conn, if_exists='replace', index=False)
    payments.to_sql('payments', conn, if_exists='replace', index=False)
    reviews.to_sql('reviews', conn, if_exists='replace', index=False)
    customers.to_sql('customers', conn, if_exists='replace', index=False)
    products.to_sql('products', conn, if_exists='replace', index=False)
    sellers.to_sql('sellers', conn, if_exists='replace', index=False)

    conn.close()

    print("\n=== Pipeline concluído com sucesso! ===")
    print(f"  Pedidos carregados : {len(master):,}")
    print(f"  Itens carregados   : {len(items_enriched):,}")
    print(f"  Avaliações         : {len(reviews):,}")
    print(f"  Banco gerado       : olist.db")

if __name__ == '__main__':
    run_pipeline()
