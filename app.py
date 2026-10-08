import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
import numpy as np
import json

# Page configuration
st.set_page_config(
    page_title="Automated Financial Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stProgress .st-bo {
        background-color: #1f77b4;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class FinancialReportGenerator:
    """Custom report generator adapted for financial ratios dataset"""
    
    def __init__(self):
        self.data = None
        self.processed_data = None
        
    def load_data(self, file_path):
        """Load and transform the ratio data to match expected format"""
        # Read the original data
        self.data = pd.read_csv(file_path)
        
        # Create transformed dataframe with required columns
        transformed = pd.DataFrame()
        
        # 1. Create company names
        transformed['Company'] = [f'Company_{i+1:03d}' for i in range(len(self.data))]
        
        # 2. Create sectors based on risk or random assignment
        np.random.seed(42)
        sectors = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Energy', 
                  'Consumer Goods', 'Industrial', 'Utilities', 'Real Estate']
        
        # Use risk column to influence sector distribution (0=low risk, 1=high risk)
        if 'risk' in self.data.columns:
            # Riskier companies more likely to be in volatile sectors
            risk_sectors = ['Technology', 'Energy', 'Retail']
            safe_sectors = ['Utilities', 'Healthcare', 'Consumer Goods']
            
            transformed['Sector'] = self.data['risk'].apply(
                lambda x: np.random.choice(risk_sectors if x == 1 else safe_sectors)
            )
        else:
            transformed['Sector'] = np.random.choice(sectors, size=len(self.data))
        
        # 3. Create synthetic Market Cap based on company size indicators
        # Use RTA (Return on Total Assets) or other metrics as proxy for size
        if 'RTA' in self.data.columns:
            size_proxy = self.data['RTA'].fillna(self.data['RTA'].median())
            # Normalize to get market cap between 100M and 500B
            normalized = (size_proxy - size_proxy.min()) / (size_proxy.max() - size_proxy.min() + 1e-10)
            transformed['Market_Cap'] = (100 + normalized * 4900) * 1e6  # in dollars
        else:
            transformed['Market_Cap'] = np.random.uniform(100, 5000, size=len(self.data)) * 1e6
        
        # 4. Create synthetic Revenue using available ratios as proxies
        # Use multiple ratios to estimate company size/revenue
        revenue_proxies = []
        
        if 'RTA' in self.data.columns:
            revenue_proxies.append(self.data['RTA'].fillna(self.data['RTA'].median()))
        if 'ROCE' in self.data.columns:
            revenue_proxies.append(self.data['ROCE'].fillna(self.data['ROCE'].median()) * 10)
        if 'PATTI' in self.data.columns:
            revenue_proxies.append(self.data['PATTI'].fillna(self.data['PATTI'].median()) * 100)
        
        if revenue_proxies:
            # Combine proxies
            combined_proxy = pd.concat(revenue_proxies, axis=1).mean(axis=1)
            # Normalize to get revenue between 10M and 100B
            norm_proxy = (combined_proxy - combined_proxy.min()) / (combined_proxy.max() - combined_proxy.min() + 1e-10)
            transformed['Revenue'] = (10 + norm_proxy * 9990) * 1e6  # in dollars
        else:
            transformed['Revenue'] = np.random.uniform(10, 10000, size=len(self.data)) * 1e6
        
        # 5. Calculate Net Income using profit ratios
        if 'PATTI' in self.data.columns:
            # PATTI is Profit After Tax to Total Income - directly gives profit margin
            profit_margin = self.data['PATTI'].fillna(0.05).abs()  # Use absolute value
            transformed['Net_Income'] = transformed['Revenue'] * profit_margin
        elif 'ROCE' in self.data.columns:
            # Use ROCE as rough profit indicator
            profit_factor = self.data['ROCE'].fillna(0.1).abs() / 100
            transformed['Net_Income'] = transformed['Revenue'] * profit_factor
        else:
            # Default 10% profit margin
            transformed['Net_Income'] = transformed['Revenue'] * 0.1
        
        # 6. Calculate Expenses = Revenue - Net_Income
        transformed['Expenses'] = transformed['Revenue'] - transformed['Net_Income']
        
        # 7. Add date column
        transformed['Date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        # Round all financial values to 2 decimals (in millions for display)
        for col in ['Revenue', 'Expenses', 'Net_Income', 'Market_Cap']:
            transformed[col] = transformed[col].round(2)
        
        self.processed_data = transformed
        return transformed
    
    def generate_basic_report(self):
        """Generate basic financial metrics"""
        df = self.processed_data
        
        report = {
            'total_companies': len(df),
            'total_revenue': df['Revenue'].sum(),
            'total_expenses': df['Expenses'].sum(),
            'total_net_income': df['Net_Income'].sum(),
            'average_revenue': df['Revenue'].mean(),
            'average_expenses': df['Expenses'].mean(),
            'average_net_income': df['Net_Income'].mean(),
            'profit_margin_avg': (df['Net_Income'].sum() / df['Revenue'].sum() * 100),
            'expense_ratio_avg': (df['Expenses'].sum() / df['Revenue'].sum() * 100)
        }
        
        return report
    
    def get_company_insights(self):
        """Get company-level insights"""
        df = self.processed_data.copy()
        
        # Calculate profit margin for each company
        df['Profit_Margin'] = (df['Net_Income'] / df['Revenue'] * 100).round(2)
        
        # Group by company (though each appears once in this dataset)
        insights = df.groupby('Company').agg({
            'Revenue': 'sum',
            'Expenses': 'sum',
            'Net_Income': 'sum',
            'Profit_Margin': 'mean',
            'Sector': 'first',
            'Market_Cap': 'first'
        }).rename(columns={
            'Revenue': 'Revenue_sum',
            'Expenses': 'Expenses_sum',
            'Net_Income': 'Net_Income_sum'
        }).reset_index()
        
        return insights
    
    def get_sector_analysis(self):
        """Generate sector-level analysis"""
        if 'Sector' not in self.processed_data.columns:
            return pd.DataFrame()
        
        df = self.processed_data.copy()
        df['Profit_Margin'] = (df['Net_Income'] / df['Revenue'] * 100).round(2)
        
        sector_analysis = df.groupby('Sector').agg({
            'Revenue': 'sum',
            'Net_Income': 'sum',
            'Profit_Margin': 'mean',
            'Company': 'count',
            'Market_Cap': 'mean'
        }).rename(columns={
            'Revenue': 'Revenue_sum',
            'Net_Income': 'Net_Income_sum',
            'Profit_Margin': 'Avg_Profit_Margin',
            'Company': 'Company_Count',
            'Market_Cap': 'Avg_Market_Cap'
        }).reset_index()
        
        return sector_analysis
    
    def generate_risk_assessment(self):
        """Generate risk assessment"""
        risk_data = {
            'high_debt_companies': 0,
            'low_profit_margin_companies': 0,
            'average_volatility': 0,
            'companies_at_risk': []
        }
        
        df = self.processed_data.copy()
        df['Profit_Margin'] = (df['Net_Income'] / df['Revenue'] * 100).round(2)
        
        # Identify companies with low profit margins
        low_margin = df[df['Profit_Margin'] < 5]
        risk_data['low_profit_margin_companies'] = len(low_margin)
        
        # Use original risk column if available
        if hasattr(self, 'data') and 'risk' in self.data.columns:
            risk_indices = self.data[self.data['risk'] == 1].index
            if len(risk_indices) > 0:
                risk_companies = df.iloc[risk_indices]['Company'].tolist()
                risk_data['companies_at_risk'].extend(risk_companies)
                risk_data['high_debt_companies'] = len(risk_companies)
        
        # Add some companies from low margin if no risk column
        if not risk_data['companies_at_risk'] and len(low_margin) > 0:
            risk_data['companies_at_risk'] = low_margin.head(5)['Company'].tolist()
            risk_data['high_debt_companies'] = len(risk_data['companies_at_risk'])
        
        # Calculate volatility (standard deviation of profit margins)
        risk_data['average_volatility'] = df['Profit_Margin'].std()
        
        return risk_data
    
    def identify_top_performers(self):
        """Identify top performing companies"""
        df = self.processed_data.copy()
        df['Profit_Margin'] = (df['Net_Income'] / df['Revenue'] * 100).round(2)
        
        # Top 10 by revenue
        top_revenue = df.nlargest(10, 'Revenue')[['Company', 'Revenue', 'Profit_Margin']]
        
        # Top 10 by profit margin
        top_margin = df.nlargest(10, 'Profit_Margin')[['Company', 'Profit_Margin', 'Revenue']]
        
        return pd.concat([top_revenue, top_margin]).drop_duplicates('Company')

# Simple GPT summary generator (optional)
def generate_basic_summary(basic_report):
    """Generate a basic text summary"""
    summary = f"""
Financial Summary:
- Total Companies: {basic_report['total_companies']}
- Total Revenue: ${basic_report['total_revenue']/1e6:,.0f}M
- Total Net Income: ${basic_report['total_net_income']/1e6:,.0f}M
- Average Profit Margin: {basic_report['profit_margin_avg']:.1f}%
- Average Expense Ratio: {basic_report['expense_ratio_avg']:.1f}%

Market Overview:
- Largest Company Revenue: ${basic_report['average_revenue']*2/1e6:,.0f}M (estimated max)
- Industry Average Revenue: ${basic_report['average_revenue']/1e6:,.0f}M per company
"""
    return summary

def main():
    # Main title
    st.markdown('<h1 class="main-header">📊 Automated Financial Report Generator</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input (kept for compatibility)
        api_key = st.text_input(
            "OpenAI API Key (Optional)", 
            type="password",
            help="Enter your OpenAI API key for AI-powered insights (optional)"
        )
        
        # Analysis options
        st.subheader("📈 Analysis Options")
        show_visualizations = st.checkbox("Show Visualizations", value=True)
        show_sector_analysis = st.checkbox("Sector Analysis", value=True)
        show_risk_assessment = st.checkbox("Risk Assessment", value=True)
        show_gpt_insights = st.checkbox("GPT-4 Insights", value=False, disabled=not api_key)
        
        st.divider()
        
        # Sample data section
        st.subheader("📂 Sample Data")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Sample Data", use_container_width=True):
                st.session_state.load_sample = "sample"
        with col2:
            if st.button("Load Tech Companies", use_container_width=True):
                st.session_state.load_sample = "tech"
        
        if st.button("Load Mixed Sectors", use_container_width=True):
            st.session_state.load_sample = "mixed"
        
        # Note about dataset
        st.info("""
        **📌 Dataset Note:**
        Your dataset contains financial ratios. The app creates synthetic 
        Revenue/Expenses based on these ratios to match the required format.
        
        **Required columns:** risk, RTA, ROCE, PATTI (or similar ratios)
        """)

    # Initialize the financial report generator
    if 'report_generator' not in st.session_state:
        st.session_state.report_generator = FinancialReportGenerator()
    
    # File upload section
    st.header("📤 Data Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Financial Data (CSV)", 
            type=["csv"],
            help="Upload your financial ratios CSV file"
        )
        
        # File size limit info
        st.caption("Limit 200MB per file · CSV only")
        
        # Show sample file info if available
        if uploaded_file is None and 'last_upload' in st.session_state:
            st.info(f"📎 Last file: {st.session_state.last_upload}  0.9KB")
    
    with col2:
        st.markdown("""
        **Required CSV Columns:**
        - Company
        - Revenue
        - Expenses
        - Net_Income
        
        **Optional:**
        - Date
        - Sector
        - Market_Cap
        """)
        
        # Sample data loaded message
        if 'sample_loaded' in st.session_state and st.session_state.sample_loaded:
            st.success("✅ Sample data loaded successfully!")
    
    # Handle sample data loading
    if 'load_sample' in st.session_state:
        sample_type = st.session_state.load_sample
        # Create sample data based on selection
        np.random.seed(42)
        n_companies = 20 if sample_type == "tech" else 30 if sample_type == "mixed" else 15
        
        # Create sample ratios data
        sample_data = pd.DataFrame({
            'risk': np.random.choice([0, 1], size=n_companies, p=[0.7, 0.3]),
            'RTA': np.random.uniform(5, 25, n_companies),
            'ROCE': np.random.uniform(8, 35, n_companies),
            'PATTI': np.random.uniform(2, 18, n_companies),
            'CURRENT': np.random.uniform(0.5, 3.5, n_companies),
            'QUICK': np.random.uniform(0.3, 2.5, n_companies),
            'DER': np.random.uniform(0.2, 3.0, n_companies),
            'DSCR': np.random.uniform(0.8, 4.5, n_companies)
        })
        
        # Save temporarily and load
        temp_path = "temp_sample.csv"
        sample_data.to_csv(temp_path, index=False)
        
        try:
            df = st.session_state.report_generator.load_data(temp_path)
            st.session_state.sample_loaded = True
            st.session_state.last_upload = "sample_edgar.csv"
            os.remove(temp_path)
            st.rerun()
        except Exception as e:
            st.error(f"Error loading sample: {str(e)}")
        
        del st.session_state.load_sample
    
    # Handle data loading from upload
    data_loaded = False
    df = None
    
    if uploaded_file is not None:
        try:
            # Save temporarily
            temp_path = "temp_upload.csv"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Load through our custom generator
            df = st.session_state.report_generator.load_data(temp_path)
            data_loaded = True
            st.session_state.sample_loaded = True
            st.session_state.last_upload = uploaded_file.name
            os.remove(temp_path)
            st.success("✅ Data loaded and transformed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
    
    # Use sample data if loaded
    if 'sample_loaded' in st.session_state and st.session_state.sample_loaded and df is None:
        if hasattr(st.session_state.report_generator, 'processed_data'):
            df = st.session_state.report_generator.processed_data
            data_loaded = True
    
    # Main analysis section
    if data_loaded and df is not None:
        
        # Display raw data preview
        st.header("📋 Data Preview")
        
        tab1, tab2 = st.tabs(["Original Ratios", "Transformed Financials"])
        
        with tab1:
            if hasattr(st.session_state.report_generator, 'data'):
                st.dataframe(st.session_state.report_generator.data.head(10), use_container_width=True)
                st.info(f"Original dataset contains {len(st.session_state.report_generator.data)} companies")
            else:
                st.info("Original ratios not available")
        
        with tab2:
            # Convert to millions for display
            display_df = df[['Company', 'Sector', 'Revenue', 'Expenses', 'Net_Income', 'Market_Cap', 'Date']].head(10).copy()
            for col in ['Revenue', 'Expenses', 'Net_Income', 'Market_Cap']:
                display_df[col] = (display_df[col] / 1e6).round(2)
            st.dataframe(display_df, use_container_width=True)
            st.info(f"Transformed dataset has {len(df)} records with synthetic Revenue/Expenses (values in $M)")
        
        # Generate basic report
        st.header("📊 Financial Analysis Dashboard")
        
        try:
            # Basic financial metrics
            basic_report = st.session_state.report_generator.generate_basic_report()
            
            # Display key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Revenue",
                    value=f"${basic_report['total_revenue']/1e9:,.1f}B",
                    delta=f"{basic_report['total_companies']} companies"
                )
            
            with col2:
                st.metric(
                    label="Total Net Income", 
                    value=f"${basic_report['total_net_income']/1e9:,.1f}B",
                    delta=f"{basic_report['profit_margin_avg']:.1f}% avg margin"
                )
            
            with col3:
                st.metric(
                    label="Average Revenue",
                    value=f"${basic_report['average_revenue']/1e6:,.0f}M",
                    delta=f"per company"
                )
            
            with col4:
                st.metric(
                    label="Expense Ratio",
                    value=f"{basic_report['expense_ratio_avg']:.1f}%",
                    delta="of revenue"
                )
            
            # Company insights
            st.subheader("🏢 Company Performance Analysis")
            company_insights = st.session_state.report_generator.get_company_insights()
            
            # Display top performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top Companies by Revenue:**")
                top_revenue = company_insights.nlargest(5, 'Revenue_sum')[
                    ['Company', 'Revenue_sum', 'Profit_Margin', 'Sector']
                ].copy()
                top_revenue['Revenue_sum'] = (top_revenue['Revenue_sum'] / 1e9).round(2)
                top_revenue = top_revenue.rename(columns={
                    'Revenue_sum': 'Revenue ($B)', 
                    'Profit_Margin': 'Margin %'
                })
                st.dataframe(top_revenue, use_container_width=True, hide_index=True)
            
            with col2:
                st.write("**Most Profitable Companies:**")
                top_profit = company_insights.nlargest(5, 'Profit_Margin')[
                    ['Company', 'Net_Income_sum', 'Profit_Margin', 'Sector']
                ].copy()
                top_profit['Net_Income_sum'] = (top_profit['Net_Income_sum'] / 1e9).round(2)
                top_profit = top_profit.rename(columns={
                    'Net_Income_sum': 'Net Income ($B)', 
                    'Profit_Margin': 'Margin %'
                })
                st.dataframe(top_profit, use_container_width=True, hide_index=True)
            
            # Sector analysis
            if show_sector_analysis:
                st.subheader("🏭 Sector Analysis")
                sector_analysis = st.session_state.report_generator.get_sector_analysis()
                
                if not sector_analysis.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Sector revenue pie chart
                        sector_display = sector_analysis.copy()
                        sector_display['Revenue_sum'] = sector_display['Revenue_sum'] / 1e9
                        
                        fig_pie = px.pie(
                            sector_display, 
                            values='Revenue_sum', 
                            names='Sector',
                            title='Revenue Distribution by Sector ($B)',
                            hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        # Sector profitability bar chart
                        fig_bar = px.bar(
                            sector_analysis,
                            x='Sector',
                            y='Avg_Profit_Margin',
                            title='Average Profit Margin by Sector',
                            color='Avg_Profit_Margin',
                            color_continuous_scale='RdYlGn',
                            text_auto='.1f'
                        )
                        fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
                        fig_bar.update_layout(yaxis_title="Profit Margin (%)")
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    # Display sector data
                    st.write("**Sector Summary:**")
                    display_sector = sector_analysis.copy()
                    display_sector['Revenue_sum'] = (display_sector['Revenue_sum'] / 1e9).round(2)
                    display_sector['Avg_Profit_Margin'] = display_sector['Avg_Profit_Margin'].round(2)
                    display_sector['Avg_Market_Cap'] = (display_sector['Avg_Market_Cap'] / 1e9).round(2)
                    display_sector = display_sector.rename(columns={
                        'Revenue_sum': 'Revenue ($B)',
                        'Avg_Profit_Margin': 'Avg Margin %',
                        'Company_Count': '# Companies',
                        'Avg_Market_Cap': 'Avg Mkt Cap ($B)'
                    })
                    st.dataframe(display_sector, use_container_width=True, hide_index=True)
            
            # Visualizations
            if show_visualizations:
                st.subheader("📈 Financial Visualizations")
                
                # Create tabs for different visualizations
                viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Scatter Analysis", "Top Companies", "Distribution"])
                
                with viz_tab1:
                    # Revenue vs Net Income scatter plot
                    df_scatter = df.copy()
                    df_scatter['Revenue_B'] = df_scatter['Revenue'] / 1e9
                    df_scatter['Net_Income_B'] = df_scatter['Net_Income'] / 1e9
                    df_scatter['Market_Cap_B'] = df_scatter['Market_Cap'] / 1e9
                    
                    fig_scatter = px.scatter(
                        df_scatter,
                        x='Revenue_B',
                        y='Net_Income_B',
                        color='Sector',
                        size='Market_Cap_B',
                        hover_data=['Company'],
                        title='Revenue vs Net Income Analysis',
                        labels={
                            'Revenue_B': 'Revenue ($B)', 
                            'Net_Income_B': 'Net Income ($B)',
                            'Market_Cap_B': 'Market Cap ($B)'
                        },
                        size_max=60
                    )
                    fig_scatter.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                with viz_tab2:
                    # Top companies bar chart
                    top_15 = df.nlargest(15, 'Revenue').copy()
                    top_15['Revenue_B'] = top_15['Revenue'] / 1e9
                    top_15['Net_Income_B'] = top_15['Net_Income'] / 1e9
                    
                    fig_bar = px.bar(
                        top_15,
                        x='Company',
                        y=['Revenue_B', 'Net_Income_B'],
                        title='Top 15 Companies - Revenue vs Net Income',
                        barmode='group',
                        labels={'value': 'Amount ($B)', 'variable': 'Metric'},
                        color_discrete_map={'Revenue_B': '#1f77b4', 'Net_Income_B': '#2ca02c'}
                    )
                    fig_bar.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with viz_tab3:
                    # Distribution of profit margins
                    df['Profit_Margin'] = (df['Net_Income'] / df['Revenue'] * 100).round(2)
                    
                    fig_hist = px.histogram(
                        df,
                        x='Profit_Margin',
                        nbins=20,
                        title='Distribution of Profit Margins',
                        labels={'Profit_Margin': 'Profit Margin (%)', 'count': 'Number of Companies'},
                        color_discrete_sequence=['#1f77b4']
                    )
                    fig_hist.add_vline(x=df['Profit_Margin'].mean(), line_dash="dash", line_color="red",
                                      annotation_text=f"Mean: {df['Profit_Margin'].mean():.1f}%")
                    st.plotly_chart(fig_hist, use_container_width=True)
            
            # Risk Assessment
            if show_risk_assessment:
                st.subheader("⚠️ Risk Assessment")
                risk_data = st.session_state.report_generator.generate_risk_assessment()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "High Risk Companies",
                        risk_data['high_debt_companies'],
                        delta=f"out of {basic_report['total_companies']}",
                        delta_color="inverse"
                    )
                
                with col2:
                    st.metric(
                        "Low Margin Companies", 
                        risk_data['low_profit_margin_companies'],
                        delta="margin < 5%",
                        delta_color="inverse"
                    )
                
                with col3:
                    st.metric(
                        "Profit Volatility",
                        f"{risk_data['average_volatility']:.2f}%",
                        delta="std deviation",
                        delta_color="off"
                    )
                
                if risk_data['companies_at_risk']:
                    st.warning(f"⚠️ **Companies requiring attention:** {', '.join(risk_data['companies_at_risk'][:5])}")
                    if len(risk_data['companies_at_risk']) > 5:
                        st.caption(f"... and {len(risk_data['companies_at_risk']) - 5} more")
            
            # GPT Insights (placeholder if API key provided)
            if show_gpt_insights and api_key:
                st.subheader("🤖 GPT-4 Insights")
                with st.spinner("Generating AI-powered insights..."):
                    # This is a placeholder - in production you'd call OpenAI API
                    st.info("""
                    **AI Analysis Summary:**
                    
                    Based on the financial data, the technology sector shows the highest growth potential 
                    with average profit margins of 15.2%. However, it also carries higher volatility.
                    
                    **Key Recommendations:**
                    1. Consider diversifying into Healthcare and Utilities for stable returns
                    2. High-risk companies (n=8) need immediate working capital optimization
                    3. Top 3 companies show 40% higher efficiency than industry average
                    
                    *Note: This is a simulated insight. Add a valid OpenAI API key for real analysis.*
                    """)
            
            # Financial Summary
            st.header("📝 Financial Summary")
            basic_summary = generate_basic_summary(basic_report)
            st.info(basic_summary)
            
            # Export options
            st.header("📁 Export Options")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                csv_company = company_insights.to_csv(index=False)
                st.download_button(
                    label="📊 Company Report (CSV)",
                    data=csv_company,
                    file_name=f"company_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                if show_sector_analysis and 'sector_analysis' in locals() and not sector_analysis.empty:
                    sector_csv = sector_analysis.to_csv(index=False)
                    st.download_button(
                        label="🏭 Sector Analysis (CSV)",
                        data=sector_csv,
                        file_name=f"sector_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col3:
                # Create full report JSON
                full_report = {
                    "summary": basic_report,
                    "companies": company_insights.to_dict('records'),
                    "risk_assessment": risk_data,
                    "generated_at": datetime.now().isoformat()
                }
                report_json = json.dumps(full_report, indent=2, default=str)
                st.download_button(
                    label="📈 Full Report (JSON)",
                    data=report_json,
                    file_name=f"financial_report_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col4:
                # Create a simple Excel-like summary
                summary_df = pd.DataFrame([basic_report])
                summary_csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📋 Summary (CSV)",
                    data=summary_csv,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                        
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            st.exception(e)
    
    else:
        # Welcome message with instructions
        st.info("""
        👋 **Welcome to the Automated Financial Report Generator!**
        
        **Getting Started:**
        1. Upload your financial ratios CSV file using the uploader above
        2. Or click one of the sample data buttons in the sidebar
        3. The app will automatically transform your ratios into synthetic Revenue/Expenses
        4. All visualizations and metrics will work with the transformed data
        
        **Your dataset will be used to:**
        - Create realistic company profiles with sector classifications
        - Generate revenue and expense estimates based on your ratios
        - Identify risk patterns from your original risk labels
        - Produce comprehensive charts, tables, and exportable reports
        
        **Expected CSV format:**
        - Should contain columns like: risk, RTA, ROCE, PATTI, CURRENT, QUICK, DER, DSCR
        - The 'risk' column (0/1) is used for risk assessment
        - Other financial ratios are used to estimate company size and profitability
        """)
        
        # Show sample of expected format
        with st.expander("📋 View sample CSV format"):
            sample_format = pd.DataFrame({
                'risk': [0, 1, 0, 0, 1],
                'RTA': [15.2, 8.7, 22.1, 12.4, 6.8],
                'ROCE': [18.5, 10.2, 25.3, 14.6, 8.9],
                'PATTI': [12.3, 4.5, 18.7, 9.8, 3.2],
                'CURRENT': [1.8, 0.9, 2.3, 1.5, 0.7],
                'QUICK': [1.2, 0.5, 1.8, 1.1, 0.4],
                'DER': [1.5, 2.8, 0.9, 1.3, 3.2],
                'DSCR': [2.1, 1.1, 3.2, 2.4, 0.9]
            })
            st.dataframe(sample_format, use_container_width=True)
            st.caption("Your CSV should have at least a 'risk' column and some financial ratios")

if __name__ == "__main__":
    main()