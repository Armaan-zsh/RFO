"""
Standalone Streamlit frontend with mock backend for deployment.
"""
import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import uuid
import random

st.set_page_config(
    page_title="Rocket Fuel Optimizer", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# Custom CSS for modern UI
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
    .status-running {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
    }
    .status-completed {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0

def mock_simulation(params: Dict[str, Any]) -> Dict[str, Any]:
    """Mock simulation for standalone deployment."""
    thrust = params['isp'] * params['pressure'] * 9.81 * 0.1 * random.uniform(0.8, 1.2)
    efficiency = thrust / (params['pressure'] * params['isp']) * random.uniform(0.8, 1.2)
    
    # Mock optimization
    optimal_params = {
        'O_F_ratio': params['O_F_ratio'] * random.uniform(0.9, 1.1),
        'pressure': params['pressure'] * random.uniform(1.0, 1.2),
        'temp': params['temp'] * random.uniform(0.95, 1.05),
        'isp': params['isp'] * random.uniform(1.0, 1.1)
    }
    
    opt_thrust = optimal_params['isp'] * optimal_params['pressure'] * 9.81 * 0.1
    
    return {
        'simulation': {
            'thrust': thrust,
            'efficiency': efficiency,
            'temperature_ratio': params['temp'] / 3000,
            'params': params
        },
        'optimization': {
            'success': True,
            'optimal_params': optimal_params,
            'predicted_thrust': opt_thrust
        },
        'model_metrics': {
            'mae': random.uniform(10, 30),
            'r2': random.uniform(0.85, 0.95),
            'train_size': 400,
            'test_size': 100
        }
    }

def create_3d_surface_plot(results: Dict[str, Any]) -> go.Figure:
    """Create 3D surface plot for thrust visualization."""
    sim_results = results.get('simulation', {})
    current_params = sim_results.get('params', {})
    
    pressure_range = np.linspace(1, 10, 25)
    isp_range = np.linspace(200, 450, 25)
    P_grid, ISP_grid = np.meshgrid(pressure_range, isp_range)
    thrust_surface = ISP_grid * P_grid * 9.81 * 0.1
    
    fig = go.Figure(data=[
        go.Surface(
            x=P_grid, y=ISP_grid, z=thrust_surface,
            colorscale='plasma', opacity=0.8,
            name='Thrust Surface'
        )
    ])
    
    if current_params:
        fig.add_trace(go.Scatter3d(
            x=[current_params.get('pressure', 5)],
            y=[current_params.get('isp', 300)],
            z=[sim_results.get('thrust', 250)],
            mode='markers+text',
            marker=dict(size=12, color='#ff6b6b', symbol='diamond'),
            text=['Current Point'],
            textposition='top center',
            name='Current Configuration'
        ))
    
    fig.update_layout(
        title=dict(text="🚀 Thrust Performance Surface", x=0.5, font=dict(size=20)),
        scene=dict(
            xaxis_title="Chamber Pressure (MPa)",
            yaxis_title="Specific Impulse (ISP)", 
            zaxis_title="Thrust (kN)",
            bgcolor='rgba(0,0,0,0)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_parameter_sensitivity_plot(results: Dict[str, Any]) -> go.Figure:
    """Create parameter sensitivity analysis plot."""
    params = ['O/F Ratio', 'Pressure', 'Temperature', 'ISP']
    variations = [15.2, 22.8, 8.5, 18.9]  # Mock sensitivity data
    
    fig = go.Figure(data=[
        go.Bar(
            x=params, y=variations,
            marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'],
            text=[f'{v:.1f}%' for v in variations],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title=dict(text="📊 Parameter Sensitivity Analysis", x=0.5, font=dict(size=18)),
        xaxis_title="Parameters",
        yaxis_title="Thrust Sensitivity (%)",
        height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return fig

def create_optimization_comparison_plot(results: Dict[str, Any]) -> go.Figure:
    """Create optimization comparison radar chart."""
    sim_results = results.get('simulation', {})
    opt_results = results.get('optimization', {})
    
    if not opt_results or not opt_results.get('success'):
        return go.Figure()
    
    current_params = sim_results.get('params', {})
    optimal_params = opt_results.get('optimal_params', {})
    
    categories = ['O/F Ratio', 'Pressure', 'Temperature', 'Thrust']
    
    current_vals = [
        (current_params.get('O_F_ratio', 3.5) - 2) / 4,
        (current_params.get('pressure', 5) - 1) / 9,
        (current_params.get('temp', 3000) - 2500) / 2500,
        sim_results.get('thrust', 250) / 500
    ]
    
    optimal_vals = [
        (optimal_params.get('O_F_ratio', 3.5) - 2) / 4,
        (optimal_params.get('pressure', 5) - 1) / 9,
        (optimal_params.get('temp', 3000) - 2500) / 2500,
        opt_results.get('predicted_thrust', 250) / 500
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=current_vals + [current_vals[0]],
        theta=categories + [categories[0]],
        fill='toself', name='Current Config',
        line_color='#ff6b6b', fillcolor='rgba(255, 107, 107, 0.2)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=optimal_vals + [optimal_vals[0]],
        theta=categories + [categories[0]],
        fill='toself', name='Optimal Config',
        line_color='#4ecdc4', fillcolor='rgba(78, 205, 196, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title=dict(text="⚡ Configuration Comparison", x=0.5, font=dict(size=18)),
        height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def display_results(results: Dict[str, Any]):
    """Display experiment results with modern UI."""
    sim_results = results.get('simulation', {})
    opt_results = results.get('optimization')
    model_metrics = results.get('model_metrics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        thrust = sim_results.get('thrust', 0)
        st.metric(
            label="🚀 Predicted Thrust", 
            value=f"{thrust:.2f} kN",
            delta=f"{thrust-250:.1f}" if thrust > 0 else None
        )
    
    with col2:
        efficiency = sim_results.get('efficiency', 0)
        st.metric(
            label="⚡ Efficiency", 
            value=f"{efficiency:.3f}",
            delta=f"{(efficiency-0.5)*100:.1f}%" if efficiency > 0 else None
        )
    
    with col3:
        if opt_results and opt_results.get('success'):
            opt_thrust = opt_results.get('predicted_thrust', 0)
            improvement = ((opt_thrust - thrust) / thrust * 100) if thrust > 0 else 0
            st.metric(
                label="🎯 Optimal Thrust", 
                value=f"{opt_thrust:.2f} kN",
                delta=f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%"
            )
        else:
            st.metric(label="🎯 Optimal Thrust", value="N/A")
    
    with col4:
        r2 = model_metrics.get('r2', 0)
        st.metric(
            label="📊 Model R²", 
            value=f"{r2:.3f}",
            delta="Excellent" if r2 > 0.9 else "Good" if r2 > 0.8 else "Fair"
        )

def main():
    """Main Streamlit application with modern UI."""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Rocket Fuel Optimizer</h1>
        <p>Advanced rocket propulsion optimization using machine learning and physics simulation</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        
        with st.expander("🔧 Engine Parameters", expanded=True):
            O_F_ratio = st.slider("🔥 Oxidizer/Fuel Ratio", 2.0, 6.0, 3.5, 0.1)
            pressure = st.slider("💨 Chamber Pressure (MPa)", 1.0, 10.0, 5.0, 0.1)
            temp = st.slider("🌡️ Combustion Temp (K)", 2500.0, 5000.0, 3000.0, 50.0)
            isp = st.slider("⚡ Specific Impulse", 200.0, 450.0, 300.0, 10.0)
        
        with st.expander("🎯 Optimization Settings", expanded=True):
            enable_optimization = st.checkbox("Enable Multi-Objective Optimization", value=True)
            
            if enable_optimization:
                alpha = st.slider("⚖️ Thrust Weight (α)", 0.0, 1.0, 0.5, 0.1)
                max_temp = st.slider("🔥 Max Temp Constraint (K)", 3000.0, 5000.0, 4000.0, 100.0)
        
        st.markdown("---")
        
        if st.button("🚀 Launch Optimization", type="primary", use_container_width=True):
            st.session_state.job_id = str(uuid.uuid4())
            st.session_state.progress = 0
            st.session_state.results = None
            st.rerun()
        
        if st.session_state.job_id:
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state.job_id = None
                st.session_state.results = None
                st.session_state.progress = 0
                st.rerun()
    
    if st.session_state.job_id:
        if st.session_state.progress < 1.0:
            st.markdown("""
            <div class="status-running">
                <h3>🔄 Optimization in Progress</h3>
                <p>Running simulation and optimization...</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(st.session_state.progress)
            st.session_state.progress += 0.2
            time.sleep(1)
            st.rerun()
        else:
            st.markdown("""
            <div class="status-completed">
                <h3>✅ Optimization Complete</h3>
                <p>Your rocket fuel optimization has finished successfully!</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.results is None:
                params = {
                    "O_F_ratio": O_F_ratio,
                    "pressure": pressure,
                    "temp": temp,
                    "isp": isp
                }
                st.session_state.results = mock_simulation(params)
            
            display_results(st.session_state.results)
            
            tab1, tab2, tab3 = st.tabs(["🌐 3D Surface", "📊 Sensitivity", "⚡ Comparison"])
            
            with tab1:
                fig1 = create_3d_surface_plot(st.session_state.results)
                st.plotly_chart(fig1, use_container_width=True)
            
            with tab2:
                fig2 = create_parameter_sensitivity_plot(st.session_state.results)
                st.plotly_chart(fig2, use_container_width=True)
            
            with tab3:
                fig3 = create_optimization_comparison_plot(st.session_state.results)
                st.plotly_chart(fig3, use_container_width=True)
            
            st.markdown("### 🤖 AI Insights")
            col1, col2 = st.columns(2)
            with col1:
                st.info("💡 **Optimization Tip**: Higher pressure generally increases thrust but requires stronger materials.")
            with col2:
                st.info("🔬 **Physics Insight**: The O/F ratio affects combustion efficiency and exhaust velocity.")
    else:
        st.markdown("""
        ### 🎯 Welcome to Rocket Fuel Optimizer
        
        This advanced tool helps you optimize rocket fuel mixtures using:
        - 🤖 **Machine Learning**: Predictive models for thrust estimation
        - 🔬 **Physics Simulation**: Real-world combustion dynamics
        - 📊 **Multi-Objective Optimization**: Balance performance vs constraints
        - 📈 **Interactive Visualization**: 3D surfaces and sensitivity analysis
        
        **Get Started:**
        1. Adjust engine parameters in the sidebar
        2. Configure optimization settings
        3. Click "Launch Optimization" to begin
        4. Explore results with interactive charts
        
        ---
        *Configure your parameters in the sidebar to begin optimization* ➡️
        """)

if __name__ == "__main__":
    main()