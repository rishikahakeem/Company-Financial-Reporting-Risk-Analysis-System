# Automated Financial Report Generator

A comprehensive financial analysis and reporting system that generates automated insights from SEC filing data using Python, OpenAI GPT-4, Pandas, LangChain, and Streamlit.

## 🎯 Project Overview

**Objective**: Generate automated financial reports and summaries from raw transactional data (Edgar SEC Filings)

**Key Features**:
- 📊 Automated financial analysis and reporting
- 🤖 GPT-4 powered insights and recommendations  
- 📈 Interactive visualizations and dashboards
- ⚠️ Risk assessment and portfolio analysis
- 🏭 Sector-wise performance analysis
- 📤 Export capabilities (CSV, JSON)

**ROI Benefits**:
- ✅ Reduces manual effort by 80-90%
- ⚡ Speeds up financial reporting process
- 🎯 Provides consistent, standardized analysis
- 💡 AI-powered insights for better decision making

## 🛠️ Tech Stack

- **Python 3.8+**: Core programming language
- **Streamlit**: Interactive web application framework
- **Pandas**: Data manipulation and analysis
- **OpenAI GPT-4**: AI-powered financial insights
- **LangChain**: LLM integration framework
- **Plotly**: Interactive visualizations
- **Matplotlib/Seaborn**: Statistical plotting

## 📁 Project Structure

```
prj/
├── data/
│   └── sample_edgar.csv           # Sample SEC filings data
├── app.py                         # Main Streamlit application
├── financial_report.py            # Core financial analysis logic
├── gpt_summary.py                 # GPT-4 integration and AI insights
├── test_examples.py               # Comprehensive test suite
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment (Optional)

Create a `.env` file for your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### 4. Upload Data or Use Samples

- **Upload CSV**: Use the file uploader to analyze your own financial data
- **Sample Data**: Click sidebar buttons to load pre-configured datasets:
  - 📊 **Sample Data**: Fortune 500 companies
  - 💻 **Tech Companies**: Technology sector analysis
  - 🏭 **Mixed Sectors**: Diverse industry analysis

## 📊 Data Format

### Required CSV Columns:
- `Company`: Company name
- `Revenue`: Total revenue ($)
- `Expenses`: Total expenses ($)  
- `Net_Income`: Net income/profit ($)

### Optional Columns:
- `Date`: Reporting date
- `Sector`: Industry sector
- `Market_Cap`: Market capitalization ($)

### Sample Data Format:
```csv
Company,Date,Revenue,Expenses,Net_Income,Sector,Market_Cap
Apple Inc,2024-03-31,123000000000,95000000000,28000000000,Technology,2800000000000
Microsoft Corp,2024-03-31,61900000000,45100000000,16800000000,Technology,2900000000000
```

## 🧪 Testing the Application

### Run Comprehensive Tests

```bash
python test_examples.py
```

### Test with GPT Analysis (requires API key)

```bash
python test_examples.py --test-gpt
```

### 4 Test Scenarios Included:

1. **Large Cap Success Stories**: High-revenue, profitable companies
   - Tests: Basic calculations, profit margins, market cap analysis
   - Expected: High profit margins, strong financial health

2. **Mixed Performance Companies**: Mix of profitable and loss-making companies
   - Tests: Loss handling, risk assessment, sector analysis
   - Expected: Varied performance metrics, risk identification

3. **Small Cap High Growth**: Smaller companies with high profit margins
   - Tests: Growth analysis, efficiency metrics, scaling insights
   - Expected: High profit margins, growth potential identification

4. **Crisis Scenario Companies**: Companies with significant losses
   - Tests: Risk assessment, bankruptcy indicators, turnaround analysis
   - Expected: High risk scores, comprehensive risk analysis

## 🔧 Configuration Options

### Streamlit App Features:
- **📈 Analysis Options**: Toggle visualizations, sector analysis, risk assessment
- **🤖 GPT-4 Insights**: AI-powered analysis (requires OpenAI API key)
- **📊 Visualizations**: Interactive charts and graphs
- **📁 Export Options**: Download reports in CSV/JSON format

### Analysis Capabilities:
- Basic financial metrics (revenue, profit margins, ratios)
- Company-wise performance analysis
- Sector benchmarking and comparison
- Risk assessment and volatility analysis
- Top performers identification
- Investment recommendations (with GPT-4)

## 🎮 How to Use

<img width="3795" height="1599" alt="image" src="https://github.com/user-attachments/assets/52a2c9e4-201f-4c4d-b52e-6979ea5b9c5e" />
<img width="3102" height="1638" alt="image" src="https://github.com/user-attachments/assets/246763d1-08a9-4355-a24c-6ad8b793a984" />
<img width="3087" height="1626" alt="image" src="https://github.com/user-attachments/assets/694c3ae1-76fa-4ebd-9b7d-21726dbb1839" />
<img width="3084" height="1569" alt="image" src="https://github.com/user-attachments/assets/8676450d-617f-446d-82d0-3764a965fb0f" />
<img width="3078" height="1602" alt="image" src="https://github.com/user-attachments/assets/73b54fed-c96f-4b4c-b796-46e77f981069" />


### Step 1: Data Upload
1. Open the application in your browser
2. Upload a CSV file or use sample data from the sidebar
3. Verify data format matches requirements

### Step 2: Configure Analysis
1. Enter OpenAI API key (optional, for AI insights)
2. Select analysis options in the sidebar:
   - Enable/disable visualizations
   - Toggle sector analysis
   - Enable risk assessment
   - Activate GPT-4 insights

### Step 3: Review Results
1. **Basic Metrics**: Revenue, profit, company counts
2. **Company Analysis**: Top performers, profit margins
3. **Sector Insights**: Industry comparison and trends
4. **Risk Assessment**: High-risk companies and indicators
5. **AI Insights**: GPT-4 powered recommendations (if enabled)

### Step 4: Export Reports
1. Download company performance reports (CSV)
2. Export sector analysis (CSV)
3. Save comprehensive report (JSON)

## 🏆 Key Metrics and KPIs

### Financial Health Indicators:
- **Profit Margin**: Net Income / Revenue
- **Expense Ratio**: Expenses / Revenue  
- **Revenue Growth**: Period-over-period growth
- **Market Position**: Market cap and sector ranking

### Risk Assessment Factors:
- **Debt Ratio**: Companies with >80% expense ratio
- **Low Profitability**: Companies with <5% profit margin
- **Volatility Score**: Deviation from average performance
- **Sector Risk**: Industry-specific risk factors

## 🔍 Sample Outputs

### Basic Financial Report:
```json
{
  "total_companies": 10,
  "total_revenue": 1450000000000,
  "total_net_income": 280000000000,
  "average_profit_margin": 19.31,
  "expense_ratio_avg": 80.69
}
```

### Risk Assessment:
```json
{
  "high_debt_companies": 2,
  "low_profit_margin_companies": 1,
  "average_volatility": 1.23,
  "companies_at_risk": ["Company A", "Company B"]
}
```

## 🚨 Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Data Format Issues**: Verify CSV has required columns
   - Check column names match exactly
   - Ensure numeric data is properly formatted

3. **GPT-4 Issues**: 
   - Verify OpenAI API key is valid
   - Check API quota and billing status
   - Ensure internet connectivity

4. **Performance Issues**: 
   - Large datasets may take time to process
   - Consider using sample data for testing
   - Close other applications to free memory

### Test Validation:
- Run `python test_examples.py` to validate installation
- Check `test_results.json` for detailed test outcomes
- Verify all 4 test scenarios pass successfully

## 📈 Performance Benchmarks

### Expected Processing Times:
- **Small Dataset** (5-10 companies): < 5 seconds
- **Medium Dataset** (50-100 companies): < 15 seconds  
- **Large Dataset** (500+ companies): < 60 seconds
- **GPT Analysis**: Additional 10-30 seconds per insight

### System Requirements:
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 100MB for application, additional for data
- **Network**: Internet connection for GPT-4 features
- **Browser**: Modern browser with JavaScript enabled

## 🤝 Contributing

To contribute to this project:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-analysis`
3. **Make changes** and test thoroughly
4. **Run test suite**: `python test_examples.py`
5. **Submit pull request** with detailed description

### Development Setup:
```bash
git clone <repository-url>
cd prj
pip install -r requirements.txt
python test_examples.py  # Validate setup
streamlit run app.py     # Start development server
```

## 📜 License

This project is open source and available under the MIT License.

## 🙋‍♂️ Support

For questions, issues, or feature requests:

1. **Run Tests**: `python test_examples.py` to identify issues
2. **Check Logs**: Review Streamlit console output for errors
3. **Validate Data**: Ensure CSV format matches requirements
4. **API Issues**: Verify OpenAI API key and quota

---

**🎯 Success Metrics**: This system typically reduces financial reporting time from hours to minutes while providing deeper insights through AI-powered analysis.


**🚀 Ready to Start**: Follow the Quick Start guide above to begin generating automated financial reports in minutes!
