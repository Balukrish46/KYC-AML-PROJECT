"""
AML Transaction Monitoring System - Main Application
Demonstrates end-to-end AML detection workflow
"""

import pandas as pd
import numpy as np
from data_generator import TransactionGenerator
from aml_detector import AMLDetector
from ml_detector import MLAnomalyDetector
from risk_scorer import RiskScorer
from case_management import CaseManager
from report_generator import ReportGenerator
from dashboard import AMLDashboard
import config


def main():
    """Main application workflow"""
    print("\n" + "="*80)
    print("AML TRANSACTION MONITORING SYSTEM")
    print("="*80 + "\n")

    # Step 1: Generate Data
    print("STEP 1: GENERATING TRANSACTION DATA")
    print("-" * 80)
    generator = TransactionGenerator(num_customers=100, num_transactions=5000)
    transactions_df, customers = generator.generate_dataset()
    customers_df = pd.DataFrame(customers)

    # Save data
    import os
    if not os.path.exists('data'):
        os.makedirs('data')

    transactions_df.to_csv('data/transactions.csv', index=False)
    customers_df.to_csv('data/customers.csv', index=False)
    print("\n[OK] Data generation complete\n")

    # Step 2: Run Rule-Based Detection
    print("\nSTEP 2: RUNNING RULE-BASED AML DETECTION")
    print("-" * 80)
    aml_detector = AMLDetector(transactions_df, customers_df)
    rule_alerts = aml_detector.run_all_detections()
    rule_summary = aml_detector.get_alert_summary()
    print("\nRule-Based Detection Summary:")
    for key, value in rule_summary.items():
        print(f"  {key}: {value}")
    print()

    # Step 3: Run ML-Based Detection
    print("\nSTEP 3: RUNNING ML-BASED ANOMALY DETECTION")
    print("-" * 80)
    ml_detector = MLAnomalyDetector(transactions_df)
    ml_alerts = ml_detector.run_detection()

    # Get feature importance
    feature_importance = ml_detector.get_feature_importance()
    if feature_importance:
        print("\nFeature Importance:")
        for feature, importance in feature_importance[:5]:
            print(f"  {feature}: {importance:.4f}")
    print()

    # Step 4: Combine All Alerts
    print("\nSTEP 4: COMBINING ALERTS FROM ALL SOURCES")
    print("-" * 80)
    all_alerts = pd.concat([rule_alerts, ml_alerts], ignore_index=True)
    print(f"[OK] Total alerts from all sources: {len(all_alerts)}")
    print()

    # Step 5: Calculate Risk Scores
    print("\nSTEP 5: CALCULATING RISK SCORES")
    print("-" * 80)
    risk_scorer = RiskScorer(all_alerts, transactions_df, customers_df)
    prioritized_alerts = risk_scorer.prioritize_alerts()
    customer_risks = risk_scorer.calculate_all_customer_risks()
    print()

    # Step 6: Case Management
    print("\nSTEP 6: CREATING INVESTIGATION CASES")
    print("-" * 80)
    case_manager = CaseManager(prioritized_alerts, transactions_df, customers_df)

    # Create cases for high-risk alerts
    high_risk_alerts = prioritized_alerts[prioritized_alerts['risk_category'] == 'HIGH'].head(10)
    for _, alert in high_risk_alerts.iterrows():
        case_manager.create_case(alert['alert_id'])

    # Auto-assign cases
    case_manager.auto_assign_cases(num_analysts=3)

    # Get case summary
    case_summary = case_manager.get_case_summary()
    print("\nCase Summary:")
    for key, value in case_summary.items():
        print(f"  {key}: {value}")
    print()

    # Step 7: Generate Reports
    print("\nSTEP 7: GENERATING REPORTS")
    print("-" * 80)
    report_generator = ReportGenerator(case_manager, transactions_df, customers_df)

    # Generate case reports for first 5 cases
    cases = case_manager.cases[:5]
    for case in cases:
        report_generator.generate_case_report(case['case_id'])

    # Generate summary report
    report_generator.generate_summary_report()

    # Generate Excel report
    report_generator.generate_excel_report()
    print()

    # Step 8: Generate Dashboard
    print("\nSTEP 8: GENERATING ANALYTICS DASHBOARD")
    print("-" * 80)
    dashboard = AMLDashboard(transactions_df, all_alerts, customer_risks, case_manager.export_cases_to_df())
    dashboard.generate_html_report()
    print()

    # Step 9: Display Results
    print("\n" + "="*80)
    print("SYSTEM RESULTS SUMMARY")
    print("="*80)

    print(f"\n[STATS] TRANSACTIONS ANALYZED: {len(transactions_df):,}")
    print(f"[STATS] CUSTOMERS: {len(customers_df):,}")
    print(f"[STATS] TOTAL ALERTS GENERATED: {len(all_alerts):,}")
    print(f"[STATS] INVESTIGATION CASES CREATED: {len(case_manager.cases):,}")

    print(f"\n[ALERTS] ALERTS BY TYPE:")
    alert_type_counts = all_alerts['alert_type'].value_counts()
    for alert_type, count in alert_type_counts.items():
        print(f"  - {alert_type}: {count}")

    print(f"\n[RISK] HIGH-RISK CUSTOMERS:")
    high_risk_customers = customer_risks[customer_risks['risk_category'] == 'HIGH'].head(5)
    for _, customer in high_risk_customers.iterrows():
        print(f"  - {customer['customer_name']} (Score: {customer['risk_score']}) - {customer['country']}")

    print(f"\n[WORKLOAD] CASE WORKLOAD:")
    for i in range(3):
        analyst = f'Analyst_{i+1}'
        cases = case_manager.get_cases_by_analyst(analyst)
        print(f"  - {analyst}: {len(cases)} cases")

    print("\n" + "="*80)
    print("[OK] AML MONITORING SYSTEM EXECUTION COMPLETE")
    print("="*80 + "\n")

    # Return key data for further analysis
    return {
        'transactions': transactions_df,
        'customers': customers_df,
        'alerts': all_alerts,
        'customer_risks': customer_risks,
        'cases': case_manager.export_cases_to_df()
    }


if __name__ == '__main__':
    results = main()
