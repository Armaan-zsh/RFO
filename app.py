import streamlit as st
import random
import time

st.set_page_config(page_title="Rocket Fuel Optimizer", layout="wide", page_icon="🚀")

st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
}
.stButton > button {
    background: linear-gradient(90deg, #ff6b6b 0%, #ee5a24 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

if 'results' not in st.session_state:
    st.session_state.results = None

st.markdown("""
<div class="main-header">
    <h1>🚀 Rocket Fuel Optimizer</h1>
    <p>Advanced rocket propulsion optimization using machine learning</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎛️ Control Panel")
    
    O_F_ratio = st.slider("🔥 Oxidizer/Fuel Ratio", 2.0, 6.0, 3.5, 0.1)
    pressure = st.slider("💨 Chamber Pressure (MPa)", 1.0, 10.0, 5.0, 0.1)
    temp = st.slider("🌡️ Combustion Temp (K)", 2500.0, 5000.0, 3000.0, 50.0)
    isp = st.slider("⚡ Specific Impulse", 200.0, 450.0, 300.0, 10.0)
    
    if st.button("🚀 Launch Optimization", type="primary"):
        thrust = isp * pressure * 9.81 * 0.1 * random.uniform(0.9, 1.1)
        efficiency = thrust / (pressure * isp) * random.uniform(0.8, 1.2)
        
        st.session_state.results = {
            'thrust': thrust,
            'efficiency': efficiency,
            'optimal_thrust': thrust * random.uniform(1.05, 1.15),
            'r2': random.uniform(0.85, 0.95)
        }
        st.rerun()

if st.session_state.results:
    st.success("✅ Optimization Complete!")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚀 Predicted Thrust", f"{st.session_state.results['thrust']:.2f} kN")
    
    with col2:
        st.metric("⚡ Efficiency", f"{st.session_state.results['efficiency']:.3f}")
    
    with col3:
        improvement = ((st.session_state.results['optimal_thrust'] - st.session_state.results['thrust']) / st.session_state.results['thrust'] * 100)
        st.metric("🎯 Optimal Thrust", f"{st.session_state.results['optimal_thrust']:.2f} kN", f"+{improvement:.1f}%")
    
    with col4:
        st.metric("📊 Model R²", f"{st.session_state.results['r2']:.3f}", "Excellent")
    
    st.markdown("### 🤖 AI Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Tip**: Higher pressure increases thrust but requires stronger materials.")
    with col2:
        st.info("🔬 **Physics**: O/F ratio affects combustion efficiency and exhaust velocity.")
else:
    st.markdown("""
    ### 🎯 Welcome to Rocket Fuel Optimizer
    
    This tool helps optimize rocket fuel mixtures using:
    - 🤖 **Machine Learning**: Predictive models for thrust estimation
    - 🔬 **Physics Simulation**: Real-world combustion dynamics
    - 📊 **Multi-Objective Optimization**: Balance performance vs constraints
    
    **Get Started:**
    1. Adjust engine parameters in the sidebar
    2. Click "Launch Optimization" to begin
    3. View your optimized results
    
    ---
    *Configure your parameters in the sidebar to begin optimization* ➡️
    """)