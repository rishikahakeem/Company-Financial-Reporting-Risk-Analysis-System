
import os
import json
import requests
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama configuration
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = 120


class GPTFinancialAnalyzer:
    """
    Local Ollama-powered financial analysis and report generation.
    Uses the installed llama3.2 model without an OpenAI API key.
    """

    def __init__(self, api_key: str = None):
        # api_key is retained for compatibility with existing code.
        # Ollama does not require an OpenAI API key.
        self.api_key = None

    def _generate_analysis(
        self,
        prompt: str,
        max_tokens: int = 400,
        temperature: float = 0.6
    ) -> str:
        """Generate text using the local Ollama model."""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                },
                timeout=OLLAMA_TIMEOUT
            )

            response.raise_for_status()
            result = response.json()
            answer = result.get("response", "").strip()

            if not answer:
                return "AI analysis unavailable: Ollama returned an empty response."

            return answer

        except requests.exceptions.ConnectionError:
            return (
                "AI analysis unavailable: Could not connect to Ollama. "
                "Open a terminal and run 'ollama list', then try again."
            )

        except requests.exceptions.Timeout:
            return (
                "AI analysis unavailable: Ollama took too long to respond. "
                "Please try again."
            )

        except requests.exceptions.RequestException as error:
            return f"AI analysis unavailable: {error}"

        except (ValueError, KeyError, TypeError) as error:
            return f"AI analysis unavailable: Invalid Ollama response. {error}"

    def generate_executive_summary(self, financial_data: Dict) -> str:
        """Generate an executive summary of financial performance."""

        prompt = f"""
You are a financial analyst. Analyze the financial data provided below.

FINANCIAL METRICS
- Total Companies Analyzed: {financial_data.get('total_companies', 'N/A')}
- Total Revenue: ${financial_data.get('total_revenue', 0):,.0f}
- Total Expenses: ${financial_data.get('total_expenses', 0):,.0f}
- Total Net Income: ${financial_data.get('total_net_income', 0):,.0f}
- Average Profit Margin: {financial_data.get('profit_margin_avg', 0):.2f}%
- Average Expense Ratio: {financial_data.get('expense_ratio_avg', 0):.2f}%

Provide:
1. Key financial highlights.
2. Performance insights.
3. Potential financial risks.
4. Practical strategic recommendations.

Keep the response professional, concise, and under 300 words.
Base conclusions on the supplied figures. Do not invent missing data.
"""
        return self._generate_analysis(prompt, max_tokens=400, temperature=0.7)

    def analyze_company_performance(self, company_data: List[Dict]) -> str:
        """Analyze individual company performance."""

        if not company_data:
            return "Company analysis not available - insufficient company data."

        company_info = "\n".join([
            f"- {comp.get('Company', 'Unknown')}: "
            f"Revenue ${comp.get('Revenue_sum', 0):,.0f}, "
            f"Net Income ${comp.get('Net_Income_sum', 0):,.0f}, "
            f"Profit Margin {comp.get('Profit_Margin', 0):.1f}%"
            for comp in company_data[:10]
        ])

        prompt = f"""
Analyze these companies using only the supplied financial information.

COMPANY DATA
{company_info}

Discuss:
1. Companies with the strongest financial performance.
2. Companies that may need attention.
3. Patterns visible in the provided figures.
4. Practical business or portfolio recommendations.

Do not assume industry information that was not provided.
Keep the response under 250 words.
"""
        return self._generate_analysis(prompt, max_tokens=350, temperature=0.6)

    def generate_sector_insights(self, sector_data: List[Dict]) -> str:
        """Generate sector-wise performance insights."""

        if not sector_data:
            return "Sector analysis not available - insufficient sector data."

        sector_info = "\n".join([
            f"- {sector.get('Sector', 'Unknown')}: "
            f"Total Revenue ${sector.get('Revenue_sum', 0):,.0f}, "
            f"Companies: {sector.get('Revenue_count', 0)}, "
            f"Average Profit Margin: "
            f"{sector.get('Avg_Profit_Margin', 0):.1f}%"
            for sector in sector_data
        ])

        prompt = f"""
Analyze sector performance using the following data.

SECTOR DATA
{sector_info}

Discuss:
1. Stronger-performing sectors based on the available metrics.
2. Sectors that may face financial challenges.
3. Opportunities or risks suggested by the figures.
4. Practical recommendations for further analysis.

Do not invent market trends or facts not present in the data.
Keep the response under 200 words.
"""
        return self._generate_analysis(prompt, max_tokens=300, temperature=0.6)

    def generate_risk_assessment(self, risk_data: Dict) -> str:
        """Generate a financial risk assessment."""

        companies_at_risk = risk_data.get("companies_at_risk", [])
        if not isinstance(companies_at_risk, list):
            companies_at_risk = []

        prompt = f"""
Assess the potential financial risks using the supplied indicators.

RISK INDICATORS
- High Debt Companies: {risk_data.get('high_debt_companies', 0)}
- Low Profit Margin Companies: {risk_data.get('low_profit_margin_companies', 0)}
- Average Volatility Score: {risk_data.get('average_volatility', 0):.2f}
- Companies at Risk: {', '.join(str(name) for name in companies_at_risk[:5])}

Provide:
1. An overall risk assessment supported by these indicators.
2. Important risk factors and possible implications.
3. Practical risk-reduction recommendations.
4. Suggested metrics to monitor over time.

If information is insufficient to determine risk, state that clearly.
Keep the response under 250 words.
"""
        return self._generate_analysis(prompt, max_tokens=350, temperature=0.7)

    def generate_investment_recommendations(
        self,
        top_performers: List[Dict]
    ) -> str:
        """Generate data-based investment research insights."""

        if not top_performers:
            return (
                "Investment analysis not available - "
                "insufficient company data."
            )

        performer_info = "\n".join([
            f"- {perf.get('Company', 'Unknown')}: "
            f"Revenue ${perf.get('Revenue', 0):,.0f}, "
            f"Net Income ${perf.get('Net_Income', 0):,.0f}, "
            f"Profit Margin {perf.get('Profit_Margin', 0):.1f}%, "
            f"Sector: {perf.get('Sector', 'Unknown')}"
            for perf in top_performers[:5]
        ])

        prompt = f"""
Review the following top-performing companies.

COMPANY DATA
{performer_info}

Provide:
1. A comparison based on the supplied financial metrics.
2. Potential strengths and growth considerations.
3. Financial risks that require further investigation.
4. Questions to investigate before making an investment decision.
5. Possible short-, medium-, and long-term considerations.

Do not guarantee returns or present this analysis as personalized
financial advice. Do not invent missing data.
Keep the response under 250 words.
"""
        return self._generate_analysis(prompt, max_tokens=350, temperature=0.6)

    def create_comprehensive_report(self, all_data: Dict) -> Dict[str, str]:
        """Create a report containing the available analysis sections."""

        report = {}

        if "basic_report" in all_data:
            report["executive_summary"] = (
                self.generate_executive_summary(all_data["basic_report"])
            )

        if "company_insights" in all_data:
            report["company_analysis"] = (
                self.analyze_company_performance(all_data["company_insights"])
            )

        if "sector_analysis" in all_data:
            report["sector_insights"] = (
                self.generate_sector_insights(all_data["sector_analysis"])
            )

        if "risk_assessment" in all_data:
            report["risk_analysis"] = (
                self.generate_risk_assessment(all_data["risk_assessment"])
            )

        if "top_performers" in all_data:
            report["investment_recommendations"] = (
                self.generate_investment_recommendations(
                    all_data["top_performers"]
                )
            )

        return report


def generate_basic_summary(financial_data: Dict) -> str:
    """Generate a basic summary without an AI model."""

    total_companies = financial_data.get("total_companies", 0)
    total_revenue = financial_data.get("total_revenue", 0)
    total_net_income = financial_data.get("total_net_income", 0)
    profit_margin = financial_data.get("profit_margin_avg", 0)
    average_revenue = financial_data.get("average_revenue", 0)
    average_net_income = financial_data.get("average_net_income", 0)
    expense_ratio = financial_data.get("expense_ratio_avg", 0)

    summary = f"""
FINANCIAL PERFORMANCE SUMMARY
=============================

Portfolio Overview:
- Total Companies: {total_companies}
- Combined Revenue: ${total_revenue:,.0f}
- Combined Net Income: ${total_net_income:,.0f}
- Average Profit Margin: {profit_margin:.2f}%

Key Metrics:
- Revenue per company: ${average_revenue:,.0f}
- Net Income per company: ${average_net_income:,.0f}
- Expense Ratio: {expense_ratio:.2f}%

Performance Assessment:
- {"Strong profitability across portfolio" if profit_margin > 15 else "Moderate or lower profitability; review company-level results"}
- {"Efficient cost management based on the expense ratio" if expense_ratio < 80 else "Potential room for cost optimization"}
- {"High combined revenue" if total_revenue > 1000000000 else "Review revenue scale and growth trends"}
"""
    return summary.strip()
