import streamlit as st
import pandas as pd
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Warehouse Layout Optimization", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
    .main {background-color: #0d1117; color: #c9d1d9;}
    .metric-card {
        background-color: #161b22; 
        padding: 20px; 
        border-radius: 8px; 
        border: 1px solid #30363d;
    }
    h1, h2, h3 {color: #58a6ff;}
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        metrics = pd.read_csv('data/evaluation_metrics.csv')
        base_layout = pd.read_csv('data/layout_baseline.csv')
        opt_layout = pd.read_csv('data/layout_optimized.csv')
        products = pd.read_csv('data/products.csv')
        
        # Merge product details
        base_layout = base_layout.merge(products, on='product_id', how='left')
        opt_layout = opt_layout.merge(products, on='product_id', how='left')
        
        G = nx.read_gml('data/demand_graph.gml')
        return metrics, base_layout, opt_layout, products, G
    except FileNotFoundError:
        return None, None, None, None, None

metrics, base_layout, opt_layout, products, G = load_data()

st.title("📦 Warehouse Slotting Optimization")
st.markdown("Reorganizing warehouse shelves using **Graph Clustering** to minimize picker travel distance.")

if metrics is None:
    st.warning("Data not generated. Run `python data_generator.py` and `python optimizer.py` first.")
    st.stop()

# --- Performance Metrics ---
st.header("1. Performance Evaluation (Simulation Results)")
col1, col2, col3 = st.columns(3)

base_dist = metrics.iloc[0]['baseline']
opt_dist = metrics.iloc[0]['optimized']
imp_pct = metrics.iloc[0]['improvement_pct']

col1.metric("Baseline Travel Distance", f"{base_dist:,.0f} units")
col2.metric("Optimized Travel Distance", f"{opt_dist:,.0f} units", delta=f"-{imp_pct:.1f}%", delta_color="inverse")
col3.metric("Estimated Time Saved", f"{imp_pct:.1f}%", help="Direct reduction in picker walking time.")

# --- Layout Visualization ---
st.header("2. Warehouse Layout Map (Depot at [0, 5])")
tab1, tab2 = st.tabs(["Optimized Layout", "Baseline Layout"])

def plot_layout(df, title):
    fig = px.scatter(df, x='shelf_x', y='shelf_y', color='category', 
                     hover_data=['product_id', 'demand_velocity'],
                     title=title, width=800, height=600, size='demand_velocity', size_max=20)
    
    # Add Depot marker
    fig.add_trace(go.Scatter(x=[0], y=[5], mode='markers+text', marker=dict(size=25, symbol='star', color='gold'),
                             name='Depot (Start/End)', text=["DEPOT"], textposition="top center"))
                             
    fig.update_layout(template="plotly_dark", xaxis=dict(range=[-1, 12], dtick=1), yaxis=dict(range=[0, 11], dtick=1))
    return fig

with tab1:
    st.markdown("**Notice how items with high demand velocity and strong affinities are clustered near the depot (0,5).**")
    st.plotly_chart(plot_layout(opt_layout, "Optimized Graph-Based Layout"), use_container_width=True)
    
with tab2:
    st.markdown("**Baseline layout assigns products randomly, causing pickers to walk across the entire warehouse.**")
    st.plotly_chart(plot_layout(base_layout, "Random Baseline Layout"), use_container_width=True)

# --- Graph Visualization ---
st.header("3. Product Demand Graph (Affinity Clusters)")
st.markdown("Items frequently co-ordered form connected clusters. The optimizer places these connected nodes in adjacent bins.")

# Generate Plotly Network Graph
pos = nx.spring_layout(G, k=0.3, seed=42)
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

node_x = []
node_y = []
node_text = []
node_size = []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    dem = G.nodes[node].get('demand', 1)
    node_size.append(min(dem / 10 + 5, 30))  # Scale for visibility
    node_text.append(f"Product: {node}<br>Demand: {dem}")

node_trace = go.Scatter(
    x=node_x, y=node_y, mode='markers', hoverinfo='text',
    text=node_text, marker=dict(showscale=True, colorscale='YlGnBu', size=node_size, 
                                color=node_size, colorbar=dict(thickness=15, title=dict(text='Demand', side='right'), xanchor='left'))
)

fig_graph = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='Product Co-Order Network',
                showlegend=False, hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                template='plotly_dark'
             ))

st.plotly_chart(fig_graph, use_container_width=True)
