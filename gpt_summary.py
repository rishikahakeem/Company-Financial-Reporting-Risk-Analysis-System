import openai
from typing import Dict, List
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GPTFinancialAnalyzer:
    """
    Advanced GPT-4 powered financial analysis and report generation.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_executive_summary(self, financial_data: Dict) -> str:
        """Generate an executive summary of financial performance."""
        
        prompt = f"""
        As a senior financial analyst, provide an executive summary based on the following financial data:
        
        Financial Metrics:
        - Total Companies Analyzed: {financial_data.get('total_companies', 'N/A')}
        - Total Revenue: ${financial_data.get('total_revenue', 0):,.0f}
        - Total Expenses: ${financial_data.get('total_expenses', 0):,.0f}
        - Total Net Income: ${financial_data.get('total_net_income', 0):,.0f}
        - Average Profit Margin: {financial_data.get('profit_margin_avg', 0):.2f}%
        - Average Expense Ratio: {financial_data.get('expense_ratio_avg', 0):.2f}%
        
        Please provide:
        1. Key financial highlights
        2. Performance trends and insights
        3. Risk factors to consider
        4. Strategic recommendations
        
        Keep the summary professional, concise, and actionable (max 300 words).
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"GPT Analysis unavailable: {str(e)}"
    
    def analyze_company_performance(self, company_data: List[Dict]) -> str:
        """Analyze individual company performance."""
        
        company_info = "\n".join([
            f"- {comp.get('Company', 'Unknown')}: Revenue ${comp.get('Revenue_sum', 0):,.0f}, "
            f"Net Income ${comp.get('Net_Income_sum', 0):,.0f}, "
            f"Profit Margin {comp.get('Profit_Margin', 0):.1f}%"
            for comp in company_data[:10]  # Analyze top 10 companies
        ])
        
        prompt = f"""
        Analyze the performance of these companies based on their financial metrics:
        
        {company_info}
        
        Provide insights on:
        1. Which companies show the strongest financial health
        2. Companies that may need attention or restructuring
        3. Industry patterns or trends you observe
        4. Recommendations for portfolio management
        
        Be specific and data-driven in your analysis (max 250 words).
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Company analysis unavailable: {str(e)}"
    
    def generate_sector_insights(self, sector_data: List[Dict]) -> str:
        """Generate sector-wise performance insights."""
        
        if not sector_data:
            return "Sector analysis not available - insufficient sector data."
        
        sector_info = "\n".join([
            f"- {sector.get('Sector', 'Unknown')}: "
            f"Total Revenue ${sector.get('Revenue_sum', 0):,.0f}, "
            f"Companies: {sector.get('Revenue_count', 0)}, "
            f"Avg Profit Margin: {sector.get('Avg_Profit_Margin', 0):.1f}%"
            for sector in sector_data
        ])
        
        prompt = f"""
        Analyze sector performance based on the following data:
        
        {sector_info}
        
        Provide insights on:
        1. Best performing sectors and why
        2. Sectors facing challenges
        3. Market opportunities and threats
        4. Investment recommendations by sector
        
        Focus on actionable insights for investors and business leaders (max 200 words).
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Sector analysis unavailable: {str(e)}"
    
    def generate_risk_assessment(self, risk_data: Dict) -> str:
        """Generate risk assessment and mitigation strategies."""
        
        prompt = f"""
        Based on the following risk metrics, provide a comprehensive risk assessment:
        
        Risk Indicators:
        - High Debt Companies: {risk_data.get('high_debt_companies', 0)}
        - Low Profit Margin Companies: {risk_data.get('low_profit_margin_companies', 0)}
        - Average Volatility Score: {risk_data.get('average_volatility', 0):.2f}
        - Companies at Risk: {', '.join(risk_data.get('companies_at_risk', [])[:5])}
        
        Provide:
        1. Overall risk level assessment
        2. Key risk factors and their implications
        3. Specific recommendations for risk mitigation
        4. Monitoring strategies for ongoing risk management
        
        Be practical and specific in your recommendations (max 250 words).
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Risk assessment unavailable: {str(e)}"
    
    def generate_investment_recommendations(self, top_performers: List[Dict]) -> str:
        """Generate investment recommendations based on top performers."""
        
        if not top_performers:
            return "Investment recommendations not available - insufficient data."
        
        performer_info = "\n".join([
            f"- {perf.get('Company', 'Unknown')}: "
            f"Revenue ${perf.get('Revenue', 0):,.0f}, "
            f"Net Income ${perf.get('Net_Income', 0):,.0f}, "
            f"Profit Margin {perf.get('Profit_Margin', 0):.1f}%, "
            f"Sector: {perf.get('Sector', 'Unknown')}"
            for perf in top_performers[:5]
        ])
        
        prompt = f"""
        Based on the top performing companies, provide investment recommendations:
        
        Top Performers:
        {performer_info}
        
        Provide:
        1. Investment attractiveness ranking
        2. Growth potential assessment
        3. Risk-adjusted return expectations
        4. Portfolio allocation suggestions
        5. Timeline recommendations (short/medium/long term)
        
        Focus on practical investment advice (max 250 words).
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Investment recommendations unavailable: {str(e)}"
    
    def create_comprehensive_report(self, all_data: Dict) -> Dict[str, str]:
        """Create a comprehensive financial report with all analyses."""
        
        report = {}
        
        # Generate all sections
        if 'basic_report' in all_data:
            report['executive_summary'] = self.generate_executive_summary(
                all_data['basic_report']
            )
        
        if 'company_insights' in all_data:
            report['company_analysis'] = self.analyze_company_performance(
                all_data['company_insights']
            )
        
        if 'sector_analysis' in all_data:
            report['sector_insights'] = self.generate_sector_insights(
                all_data['sector_analysis']
            )
        
        if 'risk_assessment' in all_data:
            report['risk_analysis'] = self.generate_risk_assessment(
                all_data['risk_assessment']
            )
        
        if 'top_performers' in all_data:
            report['investment_recommendations'] = self.generate_investment_recommendations(
                all_data['top_performers']
            )
        
        return report

# Utility function for non-GPT basic analysis
def generate_basic_summary(financial_data: Dict) -> str:
    """Generate a basic summary without GPT (fallback option)."""
    
    summary = f"""
    FINANCIAL PERFORMANCE SUMMARY
    ============================
    
    Portfolio Overview:
    • Total Companies: {financial_data.get('total_companies', 0)}
    • Combined Revenue: ${financial_data.get('total_revenue', 0):,.0f}
    • Combined Net Income: ${financial_data.get('total_net_income', 0):,.0f}
    • Average Profit Margin: {financial_data.get('profit_margin_avg', 0):.2f}%
    
    Key Metrics:
    • Revenue per company: ${financial_data.get('average_revenue', 0):,.0f}
    • Net Income per company: ${financial_data.get('average_net_income', 0):,.0f}
    • Expense Ratio: {financial_data.get('expense_ratio_avg', 0):.2f}%
    
    Performance Assessment:
    {'• Strong profitability across portfolio' if financial_data.get('profit_margin_avg', 0) > 15 else '• Moderate profitability levels'}
    {'• Efficient cost management' if financial_data.get('expense_ratio_avg', 0) < 80 else '• Room for cost optimization'}
    {'• Healthy revenue generation' if financial_data.get('total_revenue', 0) > 1000000000 else '• Growing revenue base'}
    """
    
    return summary