"""
Test Examples for Automated Financial Report Generator
=====================================================

This script provides 4 comprehensive test scenarios to validate
the financial report generation system functionality.
"""

import pandas as pd
import sys
import os
from financial_report import FinancialReportGenerator, create_sample_data_variations
from gpt_summary import GPTFinancialAnalyzer, generate_basic_summary
import json

class FinancialReportTester:
    """Comprehensive testing suite for the financial report generator."""
    
    def __init__(self):
        self.test_results = {}
        self.report_generator = FinancialReportGenerator()
    
    def create_test_datasets(self):
        """Create 4 different test datasets for comprehensive testing."""
        
        # Test Dataset 1: Large Cap Success Stories (High Revenue, High Profit)
        test1_data = {
            'Company': ['Apple Inc', 'Microsoft Corp', 'Alphabet Inc', 'Amazon.com Inc', 'Tesla Inc'],
            'Date': ['2024-03-31'] * 5,
            'Revenue': [380000000000, 211000000000, 282000000000, 514000000000, 96000000000],
            'Expenses': [270000000000, 150000000000, 220000000000, 480000000000, 85000000000],
            'Net_Income': [110000000000, 61000000000, 62000000000, 34000000000, 11000000000],
            'Sector': ['Technology', 'Technology', 'Technology', 'E-commerce', 'Automotive'],
            'Market_Cap': [3000000000000, 2800000000000, 1700000000000, 1500000000000, 800000000000]
        }
        
        # Test Dataset 2: Mixed Performance (Some Losses, Different Sectors)
        test2_data = {
            'Company': ['Boeing Co', 'General Motors', 'Netflix Inc', 'Uber Technologies', 'WeWork Inc'],
            'Date': ['2024-03-31'] * 5,
            'Revenue': [77000000000, 127000000000, 31000000000, 37000000000, 3000000000],
            'Expenses': [85000000000, 125000000000, 28000000000, 42000000000, 5000000000],
            'Net_Income': [-8000000000, 2000000000, 3000000000, -5000000000, -2000000000],
            'Sector': ['Aerospace', 'Automotive', 'Media', 'Transportation', 'Real Estate'],
            'Market_Cap': [120000000000, 60000000000, 180000000000, 80000000000, 5000000000]
        }
        
        # Test Dataset 3: Small Cap High Growth (Smaller Companies, High Margins)
        test3_data = {
            'Company': ['Zoom Video', 'Palantir Technologies', 'Snowflake Inc', 'CrowdStrike', 'Datadog Inc'],
            'Date': ['2024-03-31'] * 5,
            'Revenue': [4500000000, 2200000000, 2700000000, 3000000000, 2100000000],
            'Expenses': [3200000000, 2000000000, 2200000000, 1800000000, 1500000000],
            'Net_Income': [1300000000, 200000000, 500000000, 1200000000, 600000000],
            'Sector': ['Technology', 'Technology', 'Technology', 'Cybersecurity', 'Technology'],
            'Market_Cap': [25000000000, 35000000000, 45000000000, 55000000000, 28000000000]
        }
        
        # Test Dataset 4: Crisis Scenario (Major Losses, Economic Downturn)
        test4_data = {
            'Company': ['Bed Bath & Beyond', 'Hertz Global', 'AMC Entertainment', 'GameStop Corp', 'Blockbuster LLC'],
            'Date': ['2024-03-31'] * 5,
            'Revenue': [7500000000, 8300000000, 4500000000, 5900000000, 1200000000],
            'Expenses': [9500000000, 9800000000, 6200000000, 6100000000, 2800000000],
            'Net_Income': [-2000000000, -1500000000, -1700000000, -200000000, -1600000000],
            'Sector': ['Retail', 'Transportation', 'Entertainment', 'Retail', 'Entertainment'],
            'Market_Cap': [500000000, 1200000000, 8000000000, 12000000000, 100000000]
        }
        
        return [
            ("Large Cap Success Stories", pd.DataFrame(test1_data)),
            ("Mixed Performance Companies", pd.DataFrame(test2_data)),
            ("Small Cap High Growth", pd.DataFrame(test3_data)),
            ("Crisis Scenario Companies", pd.DataFrame(test4_data))
        ]
    
    def run_test_scenario(self, test_name: str, df: pd.DataFrame, test_gpt: bool = False) -> dict:
        """Run a complete test scenario on a dataset."""
        
        print(f"\n{'='*60}")
        print(f"RUNNING TEST: {test_name}")
        print(f"{'='*60}")
        
        results = {"test_name": test_name, "status": "PASS", "errors": []}
        
        try:
            # Save data temporarily
            temp_file = f"temp_{test_name.replace(' ', '_').lower()}.csv"
            df.to_csv(temp_file, index=False)
            
            # Load data into report generator
            self.report_generator.load_data(temp_file)
            print(f"✅ Data loaded successfully: {len(df)} companies")
            
            # Test 1: Basic Report Generation
            print("\n1. Testing Basic Report Generation...")
            basic_report = self.report_generator.generate_basic_report()
            results["basic_report"] = basic_report
            
            # Validate basic report
            required_fields = ['total_companies', 'total_revenue', 'total_net_income', 'profit_margin_avg']
            for field in required_fields:
                if field not in basic_report:
                    results["errors"].append(f"Missing field in basic report: {field}")
            
            print(f"   • Total Companies: {basic_report.get('total_companies', 0)}")
            print(f"   • Total Revenue: ${basic_report.get('total_revenue', 0):,.0f}")
            print(f"   • Total Net Income: ${basic_report.get('total_net_income', 0):,.0f}")
            print(f"   • Average Profit Margin: {basic_report.get('profit_margin_avg', 0):.2f}%")
            
            # Test 2: Company Insights
            print("\n2. Testing Company Insights...")
            company_insights = self.report_generator.get_company_insights()
            results["company_insights"] = len(company_insights)
            
            if len(company_insights) != len(df):
                results["errors"].append(f"Company insights count mismatch: expected {len(df)}, got {len(company_insights)}")
            
            print(f"   • Generated insights for {len(company_insights)} companies")
            
            # Show top performer
            if not company_insights.empty:
                top_company = company_insights.loc[company_insights['Net_Income_sum'].idxmax()]
                print(f"   • Top Performer: {top_company['Company']} (${top_company['Net_Income_sum']:,.0f} net income)")
            
            # Test 3: Sector Analysis (if sector data available)
            if 'Sector' in df.columns:
                print("\n3. Testing Sector Analysis...")
                sector_analysis = self.report_generator.get_sector_analysis()
                results["sector_analysis"] = len(sector_analysis)
                
                print(f"   • Analyzed {len(sector_analysis)} sectors")
                if not sector_analysis.empty:
                    best_sector = sector_analysis.loc[sector_analysis['Avg_Profit_Margin'].idxmax()]
                    print(f"   • Best Sector: {best_sector['Sector']} ({best_sector['Avg_Profit_Margin']:.1f}% avg margin)")
            
            # Test 4: Risk Assessment
            print("\n4. Testing Risk Assessment...")
            risk_assessment = self.report_generator.generate_risk_assessment()
            results["risk_assessment"] = risk_assessment
            
            print(f"   • High Debt Companies: {risk_assessment.get('high_debt_companies', 0)}")
            print(f"   • Low Profit Margin Companies: {risk_assessment.get('low_profit_margin_companies', 0)}")
            print(f"   • Average Volatility: {risk_assessment.get('average_volatility', 0):.2f}")
            
            if risk_assessment.get('companies_at_risk'):
                print(f"   • Companies at Risk: {', '.join(risk_assessment['companies_at_risk'])}")
            
            # Test 5: Top Performers Identification
            print("\n5. Testing Top Performers Identification...")
            top_performers = self.report_generator.identify_top_performers(top_n=3)
            results["top_performers"] = len(top_performers)
            
            print(f"   • Identified top {len(top_performers)} performers")
            for idx, company in top_performers.iterrows():
                print(f"     - {company['Company']}: {company['Profit_Margin']:.1f}% margin")
            
            # Test 6: Basic Summary Generation (Non-GPT)
            print("\n6. Testing Basic Summary Generation...")
            basic_summary = generate_basic_summary(basic_report)
            results["basic_summary_length"] = len(basic_summary)
            print(f"   • Generated summary: {len(basic_summary)} characters")
            
            # Test 7: GPT Analysis (if enabled and API key provided)
            if test_gpt:
                print("\n7. Testing GPT Analysis...")
                try:
                    # This would require a valid API key
                    gpt_analyzer = GPTFinancialAnalyzer()
                    executive_summary = gpt_analyzer.generate_executive_summary(basic_report)
                    results["gpt_analysis"] = "SUCCESS" if len(executive_summary) > 50 else "FAILED"
                    print(f"   • GPT Analysis: {results['gpt_analysis']}")
                except Exception as e:
                    results["gpt_analysis"] = f"FAILED: {str(e)}"
                    print(f"   • GPT Analysis: FAILED - {str(e)}")
            
            # Test 8: Data Validation
            print("\n8. Testing Data Validation...")
            validation_results = self.validate_data_integrity(df, basic_report)
            results["validation"] = validation_results
            
            for validation in validation_results:
                status = "✅" if validation["passed"] else "❌"
                print(f"   {status} {validation['test']}: {validation['message']}")
            
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            print(f"\n🎉 TEST COMPLETED: {test_name}")
            if results["errors"]:
                results["status"] = "FAILED"
                print(f"❌ Test failed with {len(results['errors'])} errors")
                for error in results["errors"]:
                    print(f"   • {error}")
            else:
                print("✅ All tests passed successfully!")
                
        except Exception as e:
            results["status"] = "ERROR"
            results["errors"].append(str(e))
            print(f"❌ TEST ERROR: {str(e)}")
        
        return results
    
    def validate_data_integrity(self, df: pd.DataFrame, basic_report: dict) -> list:
        """Validate data integrity and calculations."""
        
        validations = []
        
        # Test 1: Revenue calculation
        expected_total_revenue = df['Revenue'].sum()
        actual_total_revenue = basic_report.get('total_revenue', 0)
        validations.append({
            "test": "Revenue Calculation",
            "passed": abs(expected_total_revenue - actual_total_revenue) < 1000,
            "message": f"Expected: ${expected_total_revenue:,.0f}, Got: ${actual_total_revenue:,.0f}"
        })
        
        # Test 2: Net Income calculation
        expected_total_income = df['Net_Income'].sum()
        actual_total_income = basic_report.get('total_net_income', 0)
        validations.append({
            "test": "Net Income Calculation",
            "passed": abs(expected_total_income - actual_total_income) < 1000,
            "message": f"Expected: ${expected_total_income:,.0f}, Got: ${actual_total_income:,.0f}"
        })
        
        # Test 3: Company count
        expected_companies = df['Company'].nunique()
        actual_companies = basic_report.get('total_companies', 0)
        validations.append({
            "test": "Company Count",
            "passed": expected_companies == actual_companies,
            "message": f"Expected: {expected_companies}, Got: {actual_companies}"
        })
        
        # Test 4: Data types
        numeric_columns = ['Revenue', 'Expenses', 'Net_Income']
        all_numeric = all(pd.api.types.is_numeric_dtype(df[col]) for col in numeric_columns if col in df.columns)
        validations.append({
            "test": "Numeric Data Types",
            "passed": all_numeric,
            "message": "All financial columns are numeric" if all_numeric else "Some financial columns are not numeric"
        })
        
        # Test 5: No missing critical data
        critical_columns = ['Company', 'Revenue', 'Net_Income']
        missing_data = df[critical_columns].isnull().sum().sum()
        validations.append({
            "test": "Missing Critical Data",
            "passed": missing_data == 0,
            "message": f"No missing data" if missing_data == 0 else f"{missing_data} missing values found"
        })
        
        return validations
    
    def run_all_tests(self, test_gpt: bool = False):
        """Run all test scenarios."""
        
        print("🚀 STARTING COMPREHENSIVE FINANCIAL REPORT TESTING")
        print("=" * 80)
        
        test_datasets = self.create_test_datasets()
        all_results = []
        
        for test_name, df in test_datasets:
            result = self.run_test_scenario(test_name, df, test_gpt)
            all_results.append(result)
            self.test_results[test_name] = result
        
        # Summary Report
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 80)
        
        passed_tests = sum(1 for result in all_results if result["status"] == "PASS")
        failed_tests = sum(1 for result in all_results if result["status"] == "FAILED")
        error_tests = sum(1 for result in all_results if result["status"] == "ERROR")
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🚨 Errors: {error_tests}")
        print(f"📈 Success Rate: {(passed_tests / len(all_results)) * 100:.1f}%")
        
        # Detailed results
        for result in all_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAILED" else "🚨"
            print(f"\n{status_icon} {result['test_name']}: {result['status']}")
            
            if result["errors"]:
                for error in result["errors"]:
                    print(f"   • {error}")
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: test_results.json")
        
        return all_results

def main():
    """Main function to run tests."""
    
    print("Automated Financial Report Generator - Test Suite")
    print("=" * 60)
    
    # Check if GPT testing should be enabled
    test_gpt = False
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--test-gpt":
        test_gpt = True
        print("🤖 GPT testing enabled (requires valid OpenAI API key)")
    
    # Initialize tester
    tester = FinancialReportTester()
    
    # Run all tests
    results = tester.run_all_tests(test_gpt=test_gpt)
    
    # Exit with appropriate code
    success_rate = sum(1 for r in results if r["status"] == "PASS") / len(results)
    exit_code = 0 if success_rate == 1.0 else 1
    
    print(f"\n🏁 Testing completed with exit code: {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()