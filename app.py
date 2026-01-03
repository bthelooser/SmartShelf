import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml
import logging

# 1. Setup Logging & Config
logging.basicConfig(level=logging.INFO)
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 2. UI Layout & Styling
st.set_page_config(page_title="SmartShelf AI", layout="wide")

# Custom Material Design CSS
st.markdown(f"""
    <style>
    .main {{ background-color: {config['ui']['theme_background']}; }}
    .stMetric {{ background-color: white; padding: 15px; border-radius: 12px; border: 1px solid #E0E0E0; }}
    [data-testid="stSidebar"] {{ background-color: white; }}
    </style>
""", unsafe_allow_html=True)

# 3. Data Loading Helper
@st.cache_data
def load_all_data():
    try:
        v_df = pd.read_csv(config['paths']['velocity_data'])
        r_df = pd.read_csv(config['paths']['revenue_data'])
        c_df = pd.read_csv(config['paths']['compliance_data'])
        return v_df, r_df, c_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

v_df, r_df, c_df = load_all_data()

# 4. Dashboard Title
st.title("🛒 SmartShelf • Retail Intelligence Dashboard")
st.markdown("---")

# 5. Sidebar Filters
st.sidebar.header("Global Filters")
selected_cat = st.sidebar.multiselect("Product Category", options=v_df['category'].unique(), default=v_df['category'].unique())
filtered_v = v_df[v_df['category'].isin(selected_cat)]

# --- TABBED INTERFACE ---
tab1, tab2, tab3 = st.tabs(["⚡ Velocity & Efficiency", "💸 Revenue Impact", "📐 Planogram Compliance"])

with tab1:
    st.header("Restock Performance")
    col1, col2, col3 = st.columns(3)
    
    avg_wait = filtered_v['wait_time_mins'].mean()
    total_refills = len(filtered_v)
    
    col1.metric("Avg. Wait Time", f"{int(avg_wait)} mins", delta="-12% (vs last week)")
    col2.metric("Total Refill Actions", total_refills)
    col3.metric("Stock Availability", "94.2%", delta="0.5%")

    # Product Ranking Chart
    rank_df = filtered_v.groupby('sku')['units_refilled'].sum().sort_values(ascending=False).reset_index().head(10)
    fig_rank = px.bar(rank_df, x='units_refilled', y='sku', orientation='h', 
                      title="Top 10 High-Velocity Products (by Refill Volume)",
                      color_discrete_sequence=[config['ui']['theme_primary']])
    st.plotly_chart(fig_rank, use_container_width=True)

with tab2:
    st.header("Financial Loss Analysis")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        total_loss = r_df['potential_revenue_lost'].sum()
        st.metric("Total Potential Revenue Lost", f"${total_loss:,.2f}", delta_color="inverse")
        st.info("Calculation based on unit price * sales velocity * duration of OOS.")

    with col2:
        fig_rev = px.scatter(r_df, x='oos_duration_hours', y='potential_revenue_lost', 
                             size='potential_revenue_lost', hover_name='sku',
                             title="Revenue Loss vs. Out-of-Stock Duration",
                             color_discrete_sequence=['#B3261E']) # Error Red
        st.plotly_chart(fig_rev, use_container_width=True)

with tab3:
    st.header("Planogram Compliance Map")
    
    # Create a 2D Heatmap using shelf coordinates
    fig_heat = px.density_heatmap(c_df, x='x_coord', y='y_coord', z='is_compliant',
                                  histfunc='avg', nbinsx=10, nbinsy=4,
                                  color_continuous_scale="RdYlGn",
                                  labels={'is_compliant': 'Compliance %'},
                                  title="Shelf Compliance Heatmap (Green = Compliant)")
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.subheader("Recent Compliance Errors")
    st.dataframe(c_df[c_df['is_compliant'] == 0][['shelf_id', 'slot_id', 'error_type']].head(10), use_container_width=True)

st.markdown("---")
st.caption("SmartShelf AI System • 2026 Internal Operations")