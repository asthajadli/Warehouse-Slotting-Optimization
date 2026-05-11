import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

def generate_warehouse_data(num_products=100, num_orders=5000):
    print("Generating Warehouse Slotting Data...")
    np.random.seed(42)
    random.seed(42)

    # --- 1. Product Catalog & Affinities ---
    categories = ['Electronics', 'Clothing', 'Groceries', 'Home', 'Beauty', 'Sports']
    products = []
    
    for i in range(num_products):
        cat = random.choice(categories)
        products.append({
            'product_id': f"P{i:03d}",
            'category': cat,
            'demand_velocity': np.random.lognormal(mean=2, sigma=0.5) # Some highly popular, most long-tail
        })
    df_products = pd.DataFrame(products)

    # --- 2. Baseline Layout (Random Grid) ---
    # Warehouse grid: e.g., 10 aisles (X), 10 positions (Y)
    layout = []
    available_spots = [(x, y) for x in range(1, 11) for y in range(1, 11)]
    random.shuffle(available_spots)
    
    for i, row in df_products.iterrows():
        x, y = available_spots[i]
        layout.append({
            'product_id': row['product_id'],
            'shelf_x': x,
            'shelf_y': y
        })
    df_layout = pd.DataFrame(layout)

    # --- 3. Order Generation (With Co-Purchase Patterns) ---
    orders = []
    start_date = datetime.now() - timedelta(days=30)
    
    # Create distinct "baskets" of items that are frequently bought together
    baskets = []
    for _ in range(15): # 15 common combinations
        basket_size = random.randint(2, 5)
        # Baskets usually contain items from same category, or specific pairs
        cat = random.choice(categories)
        cat_products = df_products[df_products['category'] == cat]['product_id'].tolist()
        if len(cat_products) >= basket_size:
            baskets.append(random.sample(cat_products, basket_size))

    current_time = start_date
    for order_id in range(num_orders):
        current_time += timedelta(minutes=random.randint(1, 15))
        
        # Decide if this is a "basket" order or random
        items_in_order = []
        if random.random() < 0.6 and baskets: # 60% chance of typical basket pattern
            base_basket = random.choice(baskets)
            # Add some noise (maybe not all items bought, maybe an extra random item)
            items_in_order = [p for p in base_basket if random.random() < 0.8]
            if not items_in_order:
                items_in_order = [random.choice(df_products['product_id'])]
        else:
            # Random order weighted by demand velocity
            probs = df_products['demand_velocity'] / df_products['demand_velocity'].sum()
            num_items = random.randint(1, 6)
            items_in_order = np.random.choice(df_products['product_id'], size=num_items, p=probs, replace=False).tolist()

        for prod_id in items_in_order:
            orders.append({
                'order_id': f"ORD{order_id:05d}",
                'order_timestamp': current_time,
                'product_id': prod_id,
                'quantity': random.randint(1, 3)
            })
            
    df_orders = pd.DataFrame(orders)

    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df_products.to_csv('data/products.csv', index=False)
    df_layout.to_csv('data/layout_baseline.csv', index=False)
    df_orders.to_csv('data/orders.csv', index=False)
    
    print(f"Generated {len(df_products)} products, {num_orders} orders ({len(df_orders)} order lines).")
    print("Files saved to data/ directory.")

if __name__ == "__main__":
    generate_warehouse_data()
