# 🏭 Warehouse Slotting Optimization Using Demand Graphs

An ML-powered system that optimizes warehouse product placement to minimize picker travel distance, using demand graph analysis and community detection algorithms.

---

## 📌 Problem Statement

In large warehouses, inefficient product placement leads to excessive picker travel time and higher operational costs. This project addresses that by analyzing order patterns and strategically placing frequently co-ordered products closer together and near the depot.

---

## 💡 How It Works

1. **Demand Graph Construction** — Builds a co-order graph where products are nodes and edges represent how frequently two products are ordered together
2. **Community Detection** — Uses greedy modularity clustering (NetworkX) to identify product clusters that are frequently bought together
3. **Layout Optimization** — Places high-demand clusters closest to the depot using a greedy heuristic based on pick frequency and cluster importance
4. **Travel Distance Simulation** — Simulates picker travel using nearest-neighbor routing and Manhattan distance, comparing baseline vs optimized layout
5. **Interactive Dashboard** — Visualizes results, layout comparisons, and metrics via a Streamlit web app

---

## 📊 Results

| Metric | Baseline | Optimized |
|---|---|---|
| Total Travel Distance | Simulated | Reduced |
| Layout Strategy | Random | Demand-based |
| Routing | Fixed | Nearest Neighbor |

> Distance reduction percentage is calculated and displayed live on the dashboard.

---

## 🛠️ Tech Stack

- **Language:** Python
- **Data Manipulation:** Pandas, NumPy
- **Graph Analysis:** NetworkX
- **Machine Learning:** Scikit-learn, SciPy
- **Visualization:** Plotly, Matplotlib
- **Web App:** Streamlit

---

## 📁 Project Structure

```
├── app.py                  # Streamlit dashboard
├── optimizer.py            # Core optimization logic
├── data_generator.py       # Synthetic data generation
├── requirements.txt        # Dependencies
└── data/
    ├── orders.csv              # Order transaction data
    ├── products.csv            # Product catalog
    ├── layout_baseline.csv     # Original warehouse layout
    ├── layout_optimized.csv    # Optimized warehouse layout
    ├── evaluation_metrics.csv  # Performance comparison
    └── demand_graph.gml        # Graph structure
```

## 📚 Concepts Used

- Graph Theory & Community Detection
- Demand Velocity Analysis
- Greedy Optimization Heuristics
- Manhattan Distance Routing Simulation
