import pandas as pd
import numpy as np
import networkx as nx
from itertools import combinations
import os

def calculate_manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def simulate_picking(df_orders, df_layout, depot=(0, 5)):
    """Simulates picking process and calculates total travel distance."""
    # Merge order lines with their shelf locations
    layout_map = df_layout.set_index('product_id')[['shelf_x', 'shelf_y']].to_dict('index')
    
    total_distance = 0
    grouped_orders = df_orders.groupby('order_id')
    
    for _, order_group in grouped_orders:
        products = order_group['product_id'].tolist()
        if not products: continue
        
        # Simple routing: Nearest neighbor from depot, then through items, then back to depot
        locations = [(layout_map[p]['shelf_x'], layout_map[p]['shelf_y']) for p in products]
        
        current_loc = depot
        unvisited = locations.copy()
        order_dist = 0
        
        while unvisited:
            # Find nearest next item
            next_loc = min(unvisited, key=lambda loc: calculate_manhattan_distance(current_loc, loc))
            order_dist += calculate_manhattan_distance(current_loc, next_loc)
            current_loc = next_loc
            unvisited.remove(next_loc)
            
        # Return to depot
        order_dist += calculate_manhattan_distance(current_loc, depot)
        total_distance += order_dist
        
    return total_distance

def optimize_layout():
    print("Building Demand Graph & Optimizing Layout...")
    
    df_orders = pd.read_csv('data/orders.csv')
    df_layout_base = pd.read_csv('data/layout_baseline.csv')
    df_products = pd.read_csv('data/products.csv')
    
    # 1. Build Co-Order Graph
    G = nx.Graph()
    for p in df_products['product_id']:
        G.add_node(p)
        
    order_groups = df_orders.groupby('order_id')['product_id'].apply(list)
    edge_weights = {}
    
    for items in order_groups:
        if len(items) > 1:
            for p1, p2 in combinations(sorted(items), 2):
                pair = (p1, p2)
                edge_weights[pair] = edge_weights.get(pair, 0) + 1
                
    for (p1, p2), weight in edge_weights.items():
        if weight > 1: # Filter weak connections
            G.add_edge(p1, p2, weight=weight)
            
    # 2. Demand Velocity (Pick Frequency)
    pick_freq = df_orders['product_id'].value_counts().to_dict()
    for node in G.nodes():
        G.nodes[node]['demand'] = pick_freq.get(node, 0)
        
    # 3. Clustering Implementation (Louvain Community Detection)
    # NetworkX greedy modularity as an alternative to Louvain for no extra dependency
    communities = nx.algorithms.community.greedy_modularity_communities(G, weight='weight')
    
    cluster_map = {}
    for i, comm in enumerate(communities):
        for node in comm:
            cluster_map[node] = i
            
    df_products['cluster_id'] = df_products['product_id'].map(cluster_map).fillna(-1)
    
    # 4. Layout Optimization Logic (Greedy Heuristic based on graph)
    # Goal: Fast moving items & high degree clusters near Depot (0,5)
    # Available spots: 1..10 x 1..10
    available_spots = [(x, y) for x in range(1, 11) for y in range(1, 11)]
    depot = (0, 5)
    # Sort spots by distance to depot
    available_spots.sort(key=lambda s: calculate_manhattan_distance(depot, s))
    
    # Calculate cluster importance (sum of demand)
    cluster_demand = {i: 0 for i in set(cluster_map.values())}
    for node, c_id in cluster_map.items():
        cluster_demand[c_id] += pick_freq.get(node, 0)
        
    # Sort products: first by their cluster's total demand, then by individual demand
    products_to_place = []
    for node in G.nodes():
        c_id = cluster_map.get(node, -1)
        c_dem = cluster_demand.get(c_id, 0)
        p_dem = pick_freq.get(node, 0)
        products_to_place.append((node, c_dem, p_dem))
        
    products_to_place.sort(key=lambda x: (x[2], x[1]), reverse=True)
    
    optimized_layout = []
    for i, (prod_id, _, _) in enumerate(products_to_place):
        if i < len(available_spots):
            x, y = available_spots[i]
            optimized_layout.append({
                'product_id': prod_id,
                'shelf_x': x,
                'shelf_y': y
            })
            
    df_opt_layout = pd.DataFrame(optimized_layout)
    df_opt_layout.to_csv('data/layout_optimized.csv', index=False)
    
    # 5. Travel Distance Simulation
    print("Simulating Baseline Travel Distance...")
    base_dist = simulate_picking(df_orders, df_layout_base, depot)
    
    print("Simulating Optimized Travel Distance...")
    opt_dist = simulate_picking(df_orders, df_opt_layout, depot)
    
    improvement = ((base_dist - opt_dist) / base_dist) * 100
    
    print(f"--- Evaluation Metrics ---")
    print(f"Baseline Distance: {base_dist} units")
    print(f"Optimized Distance: {opt_dist} units")
    print(f"Distance Reduction: {improvement:.2f}%")
    
    # Save metrics for dashboard
    df_metrics = pd.DataFrame([{
        'metric': 'Total Travel Distance',
        'baseline': base_dist,
        'optimized': opt_dist,
        'improvement_pct': improvement
    }])
    df_metrics.to_csv('data/evaluation_metrics.csv', index=False)
    
    # Save graph structure for visualization
    nx.write_gml(G, "data/demand_graph.gml")

if __name__ == "__main__":
    optimize_layout()
