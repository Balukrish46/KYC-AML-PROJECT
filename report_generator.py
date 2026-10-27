"""
Investigation Report Generator
Creates detailed investigation reports for AML cases
"""

import pandas as pd
from datetime import datetime
import os
import config


class ReportGenerator:
    """Generate investigation reports for AML cases"""

    def __init__(self, case_manager, transactions_df, customers_df):
        self.case_manager = case_manager
        self.transactions = transactions_df
        self.customers = customers_df

        # Create output directory if it doesn't exist
        if not os.path.exists(config.REPORT_OUTPUT_DIR):
            os.makedirs(config.REPORT_OUTPUT_DIR)

    def generate_case_report(self, case_id):
        """Generate detailed investigation report for a case"""
        case_details = self.case_manager.get_case_details(case_id)

        if not case_details:
            print(f"Case {case_id} not found")
            return None

        case = case_details['case']
        customer = case_details['customer']
        transactions = case_details['transactions']

        # Build report
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("AML INVESTIGATION REPORT")
        report_lines.append("="*80)
        report_lines.append("")

        # Case Information
        report_lines.append("CASE INFORMATION")
        report_lines.append("-" * 80)
        report_lines.append(f"Case ID: {case['case_id']}")
        report_lines.append(f"Alert ID: {case['alert_id']}")
        report_lines.append(f"Status: {case['status'].upper()}")
        report_lines.append(f"Priority: {case['priority']}")
        report_lines.append(f"Risk Score: {case['risk_score']}")
        report_lines.append(f"Alert Type: {case['alert_type']}")
        report_lines.append(f"Assigned To: {case['assigned_to']}")
        report_lines.append(f"Created: {case['created_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        if case['resolved_date']:
            report_lines.append(f"Resolved: {case['resolved_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Customer Information
        report_lines.append("CUSTOMER INFORMATION")
        report_lines.append("-" * 80)
        report_lines.append(f"Customer ID: {customer['customer_id']}")
        report_lines.append(f"Name: {customer['name']}")
        report_lines.append(f"Country: {customer['country']}")
        report_lines.append(f"Customer Type: {customer['customer_type']}")
        report_lines.append(f"Account Age: {customer['account_age_days']} days")
        report_lines.append(f"Registration Date: {customer['registration_date']}")
        report_lines.append("")

        # Transaction Details
        report_lines.append("TRANSACTION DETAILS")
        report_lines.append("-" * 80)
        report_lines.append(f"Number of Transactions: {case_details['transaction_count']}")
        report_lines.append(f"Total Amount: ${case_details['total_amount']:,.2f}")
        report_lines.append("")

        if transactions:
            report_lines.append("Transaction List:")
            report_lines.append("-" * 80)
            for txn in transactions:
                report_lines.append(f"  - {txn['transaction_id']}")
                report_lines.append(f"    Date: {txn['transaction_date']}")
                report_lines.append(f"    Amount: ${txn['amount']:,.2f}")
                report_lines.append(f"    Type: {txn['transaction_type']}")
                report_lines.append(f"    Counterparty: {txn['counterparty']}")
                report_lines.append(f"    Country: {txn['counterparty_country']}")
                report_lines.append("")

        # Investigation Notes
        if case['investigation_notes']:
            report_lines.append("INVESTIGATION NOTES")
            report_lines.append("-" * 80)
            for note in case['investigation_notes']:
                report_lines.append(f"[{note['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] {note['author']}")
                report_lines.append(f"  {note['note']}")
                report_lines.append("")

        # Evidence
        if case['evidence']:
            report_lines.append("EVIDENCE COLLECTED")
            report_lines.append("-" * 80)
            for evidence in case['evidence']:
                report_lines.append(f"Type: {evidence['type']}")
                report_lines.append(f"Description: {evidence['description']}")
                report_lines.append(f"Timestamp: {evidence['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                report_lines.append("")

        # Resolution
        if case['resolution']:
            report_lines.append("RESOLUTION")
            report_lines.append("-" * 80)
            report_lines.append(f"Final Resolution: {case['resolution'].upper()}")
            report_lines.append("")

        # Footer
        report_lines.append("="*80)
        report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("="*80)

        # Save report
        report_text = "\n".join(report_lines)
        filename = f"{config.REPORT_OUTPUT_DIR}/report_{case_id}.txt"
        with open(filename, 'w') as f:
            f.write(report_text)

        print(f"[OK] Generated report for case {case_id}: {filename}")

        return filename

    def generate_summary_report(self):
        """Generate summary report of all cases"""
        summary = self.case_manager.get_case_summary()

        if not summary:
            print("No cases to summarize")
            return None

        report_lines = []
        report_lines.append("="*80)
        report_lines.append("AML CASE MANAGEMENT SUMMARY REPORT")
        report_lines.append("="*80)
        report_lines.append("")
        report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Overall Statistics
        report_lines.append("OVERALL STATISTICS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Cases: {summary['total_cases']}")
        report_lines.append(f"Open Cases: {summary['open_cases']}")
        report_lines.append(f"Resolved Cases: {summary['resolved_cases']}")
        report_lines.append("")

        # Priority Distribution
        report_lines.append("PRIORITY DISTRIBUTION")
        report_lines.append("-" * 80)
        report_lines.append(f"High Priority: {summary['high_priority']}")
        report_lines.append(f"Medium Priority: {summary['medium_priority']}")
        report_lines.append(f"Low Priority: {summary['low_priority']}")
        report_lines.append("")

        # Resolution Breakdown
        if summary['resolutions']:
            report_lines.append("RESOLUTION BREAKDOWN")
            report_lines.append("-" * 80)
            for resolution, count in summary['resolutions'].items():
                report_lines.append(f"{resolution}: {count}")
            report_lines.append("")

        # Footer
        report_lines.append("="*80)

        # Save report
        report_text = "\n".join(report_lines)
        filename = f"{config.REPORT_OUTPUT_DIR}/summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report_text)

        print(f"[OK] Generated summary report: {filename}")

        return filename

    def generate_excel_report(self):
        """Generate Excel report with all cases and transactions"""
        cases_df = self.case_manager.export_cases_to_df()

        # Create Excel writer
        filename = f"{config.REPORT_OUTPUT_DIR}/aml_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Cases sheet
            cases_df.to_excel(writer, sheet_name='Cases', index=False)

            # Transactions sheet
            self.transactions.to_excel(writer, sheet_name='Transactions', index=False)

            # Customers sheet
            self.customers.to_excel(writer, sheet_name='Customers', index=False)

        print(f"[OK] Generated Excel report: {filename}")

        return filename
