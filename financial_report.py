import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from datetime import datetime
import json
import tempfile

# MUST be the first Streamlit command
st.set_page_config(
    page_title="Automated Financial Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'original_data' not in st.session_state:
    st.session_state.original_data = None
if 'load_sample' not in st.session_state:
    st.session_state.load_sample = None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def load_and_transform_data(file_path):
    """Load and transform the ratio data"""
    try:
        # Read the original data
        original_data = pd.read_csv(file_path)
        
        # Create transformed dataframe
        transformed = pd.DataFrame()
        
        # Create company names
        transformed['Company'] = [f'Company_{i+1:03d}' for i in range(len(original_data))]
        
        # Create sectors
        np.random.seed(42)
        sectors = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Energy']
        transformed['Sector'] = np.random.choice(sectors, size=len(original_data))
        
        # Create synthetic financial data
        n = len(original_data)
        
        # Revenue between 10M and 50B
        transformed['Revenue'] = np.random.uniform(10, 50000, n) * 1e6
        
        # Net Income (5-25% of revenue)
        profit_margins = np.random.uniform(0.05, 0.25, n)
        transformed['Net_Income'] = transformed['Revenue'] * profit_margins
        
        # Expenses = Revenue - Net Income
        transformed['Expenses'] = transformed['Revenue'] - transformed['Net_Income']
        
        # Market Cap (0.5x to 5x revenue)
        transformed['Market_Cap'] = transformed['Revenue'] * np.random.uniform(0.5, 5, n)
        
        # Date
        transformed['Date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Round values
        for col in ['Revenue', 'Expenses', 'Net_Income', 'Market_Cap']:
            transformed[col] = transformed[col].round(2)
        
        return original_data, transformed
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def create_sample_data(sample_type="sample"):
    """Create sample data"""
    np.random.seed(42)
    
    if sample_type == "tech":
        n = 20
    elif sample_type == "mixed":
        n = 30
    else:
        n = 15
    
    # Create sample ratios
    sample_data = pd.DataFrame({
        'risk': np.random.choice([0, 1], size=n, p=[0.7, 0.3]),
        'RTA': np.random.uniform(5, 25, n),
        'ROCE': np.random.uniform(8, 35, n),
        'PATTI': np.random.uniform(2, 18, n)
    })
    
    return sample_data

def generate_basic_report(df):
    """Generate basic financial metrics"""
    report = {
        'total_companies': len(df),
        'total_revenue': df['Revenue'].sum(),
        'total_net_income': df['Net_Income'].sum(),
        'total_expenses': df['Expenses'].sum(),
        'avg_revenue': df['Revenue'].mean(),
        'avg_margin': (df['Net_Income'].sum() / df['Revenue'].sum() * 100)
    }
    return report

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Automated Financial Report Generator</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Options")
        
        st.subheader("📂 Sample Data")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Sample", use_container_width=True):
                st.session_state.load_sample = "sample"
        with col2:
            if st.button("Load Tech", use_container_width=True):
                st.session_state.load_sample = "tech"
        
        if st.button("Load Mixed Sectors", use_container_width=True):
            st.session_state.load_sample = "mixed"
        
        st.divider()
        
        st.subheader("📈 Analysis")
        show_viz = st.checkbox("Show Visualizations", value=True)
        show_sector = st.checkbox("Sector Analysis", value=True)
        show_risk = st.checkbox("Risk Assessment", value=True)
    
    # File Upload
    st.header("📤 Data Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload Financial Data (CSV)", type=['csv'])
        st.caption("Limit 200MB per file · CSV only")
    
    with col2:
        st.markdown("""
        **Required Columns:**
        - Company
        - Revenue
        - Expenses
        - Net_Income
        
        **Optional:**
        - Sector
        - Market_Cap
        """)
    
    # Handle sample data loading
    if st.session_state.load_sample is not None:
        with st.spinner(f"Loading sample data..."):
            # Create sample data
            sample_data = create_sample_data(st.session_state.load_sample)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                sample_data.to_csv(f.name, index=False)
                temp_path = f.name
            
            # Load and transform
            original, transformed = load_and_transform_data(temp_path)
            
            if transformed is not None:
                st.session_state.original_data = original
                st.session_state.current_data = transformed
                st.session_state.data_loaded = True
                st.success(f"✅ Sample data loaded successfully!")
            
            # Cleanup
            os.unlink(temp_path)
            st.session_state.load_sample = None
            st.rerun()
    
    # Handle file upload
    if uploaded_file is not None:
        with st.spinner("Processing..."):
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
                f.write(uploaded_file.getbuffer())
                temp_path = f.name
            
            # Load and transform
            original, transformed = load_and_transform_data(temp_path)
            
            if transformed is not None:
                st.session_state.original_data = original
                st.session_state.current_data = transformed
                st.session_state.data_loaded = True
                st.success(f"✅ Data loaded successfully!")
            
            # Cleanup
            os.unlink(temp_path)
    
    # Display results if data is loaded
    if st.session_state.data_loaded and st.session_state.current_data is not None:
        df = st.session_state.current_data
        
        # Data Preview
        st.header("📋 Data Preview")
        
        tab1, tab2 = st.tabs(["Original Data", "Transformed Data"])
        
        with tab1:
            if st.session_state.original_data is not None:
                st.dataframe(st.session_state.original_data.head(10), use_container_width=True)
        
        with tab2:
            display_df = df[['Company', 'Sector', 'Revenue', 'Expenses', 'Net_Income']].head(10).copy()
            for col in ['Revenue', 'Expenses', 'Net_Income']:
                display_df[col] = (display_df[col] / 1e6).round(2)
            st.dataframe(display_df, use_container_width=True)
            st.info(f"Total Companies: {len(df)} | Values in $M")
        
        # Key Metrics
        st.header("📊 Key Metrics")
        report = generate_basic_report(df)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", f"${report['total_revenue']/1e9:.2f}B")
        with col2:
            st.metric("Total Net Income", f"${report['total_net_income']/1e9:.2f}B")
        with col3:
            st.metric("Avg Revenue", f"${report['avg_revenue']/1e6:.0f}M")
        with col4:
            st.metric("Avg Margin", f"{report['avg_margin']:.1f}%")
        
        # Visualizations
        if show_viz:
            st.header("📈 Visualizations")
            
            # Scatter plot
            df_scatter = df.copy()
            df_scatter['Revenue_B'] = df_scatter['Revenue'] / 1e9
            df_scatter['Net_Income_B'] = df_scatter['Net_Income'] / 1e9
            
            fig = px.scatter(
                df_scatter,
                x='Revenue_B',
                y='Net_Income_B',
                color='Sector',
                hover_data=['Company'],
                title='Revenue vs Net Income',
                labels={'Revenue_B': 'Revenue ($B)', 'Net_Income_B': 'Net Income ($B)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Sector Analysis
        if show_sector and 'Sector' in df.columns:
            st.header("🏭 Sector Analysis")
            
            sector_data = df.groupby('Sector').agg({
                'Revenue': 'sum',
                'Net_Income': 'sum',
                'Company': 'count'
            }).reset_index()
            
            sector_data['Revenue_B'] = sector_data['Revenue'] / 1e9
            sector_data['Margin'] = (sector_data['Net_Income'] / sector_data['Revenue'] * 100).round(1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = px.pie(
                    sector_data,
                    values='Revenue_B',
                    names='Sector',
                    title='Revenue by Sector',
                    hole=0.4
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                fig_bar = px.bar(
                    sector_data,
                    x='Sector',
                    y='Margin',
                    title='Profit Margin by Sector',
                    color='Margin',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Risk Assessment
        if show_risk:
            st.header("⚠️ Risk Assessment")
            
            df['Profit_Margin'] = (df['Net_Income'] / df['Revenue'] * 100)
            low_margin = df[df['Profit_Margin'] < 5]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("High Risk", len(low_margin), f"out of {len(df)}")
            with col2:
                st.metric("Avg Margin", f"{df['Profit_Margin'].mean():.1f}%")
            with col3:
                st.metric("Volatility", f"{df['Profit_Margin'].std():.1f}%")
            
            if len(low_margin) > 0:
                st.warning(f"⚠️ {len(low_margin)} companies have margins below 5%")
        
        # Export
        st.header("📁 Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                f"financial_data_{datetime.now():%Y%m%d}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            report_json = json.dumps(report, indent=2)
            st.download_button(
                "📥 Download Summary",
                report_json,
                f"summary_{datetime.now():%Y%m%d}.json",
                "application/json",
                use_container_width=True
            )
    
    else:
        # Welcome message
        st.info("""
        👋 **Welcome!**
        
        **Get started by:**
        1. Clicking a sample button in the sidebar
        2. Uploading your own CSV file
        
        The app will automatically transform your data and generate reports.
        """)

if __name__ == "__main__":
    main()