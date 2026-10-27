"""
Case Management System
Manages alert lifecycle, investigation workflow, and resolution
"""

import pandas as pd
from datetime import datetime
import json


class CaseManager:
    """Manage alert investigation cases"""

    def __init__(self, alerts_df, transactions_df, customers_df):
        self.alerts = alerts_df
        self.transactions = transactions_df
        self.customers = customers_df
        self.cases = []
        self.case_id_counter = 1

    def create_case(self, alert_id, assigned_to='Analyst'):
        """Create a new investigation case for an alert"""
        alert = self.alerts[self.alerts['alert_id'] == alert_id]

        if alert.empty:
            print(f"Alert {alert_id} not found")
            return None

        alert = alert.iloc[0]

        case = {
            'case_id': f'CASE{self.case_id_counter:05d}',
            'alert_id': alert_id,
            'customer_id': alert['customer_id'],
            'assigned_to': assigned_to,
            'created_date': datetime.now(),
            'status': 'open',
            'priority': alert['risk_category'],
            'risk_score': alert['adjusted_risk_score'],
            'alert_type': alert['alert_type'],
            'transaction_ids': alert['transaction_ids'],
            'investigation_notes': [],
            'evidence': [],
            'resolution': None,
            'resolved_date': None
        }

        self.cases.append(case)
        self.case_id_counter += 1

        print(f"[OK] Created case {case['case_id']} for alert {alert_id}")

        return case

    def add_investigation_note(self, case_id, note, author='Analyst'):
        """Add investigation note to a case"""
        case = next((c for c in self.cases if c['case_id'] == case_id), None)

        if case:
            case['investigation_notes'].append({
                'timestamp': datetime.now(),
                'author': author,
                'note': note
            })
            print(f"[OK] Added note to case {case_id}")
        else:
            print(f"Case {case_id} not found")

    def add_evidence(self, case_id, evidence_type, description, data):
        """Add evidence to a case"""
        case = next((c for c in self.cases if c['case_id'] == case_id), None)

        if case:
            case['evidence'].append({
                'type': evidence_type,
                'description': description,
                'data': data,
                'timestamp': datetime.now()
            })
            print(f"[OK] Added evidence to case {case_id}")
        else:
            print(f"Case {case_id} not found")

    def resolve_case(self, case_id, resolution, notes=''):
        """Resolve a case"""
        case = next((c for c in self.cases if c['case_id'] == case_id), None)

        if case:
            case['status'] = 'resolved'
            case['resolution'] = resolution
            case['resolved_date'] = datetime.now()

            if notes:
                self.add_investigation_note(case_id, f"Resolution: {notes}")

            print(f"[OK] Resolved case {case_id} as: {resolution}")
        else:
            print(f"Case {case_id} not found")

    def get_case_details(self, case_id):
        """Get detailed information about a case"""
        case = next((c for c in self.cases if c['case_id'] == case_id), None)

        if case:
            # Get customer information
            customer = self.customers[self.customers['customer_id'] == case['customer_id']].iloc[0]

            # Get transaction details
            case_txns = self.transactions[
                self.transactions['transaction_id'].isin(case['transaction_ids'])
            ]

            details = {
                'case': case,
                'customer': customer.to_dict(),
                'transactions': case_txns.to_dict('records'),
                'transaction_count': len(case_txns),
                'total_amount': case_txns['amount'].sum()
            }

            return details
        else:
            return None

    def get_case_summary(self):
        """Get summary of all cases"""
        if not self.cases:
            return None

        summary = {
            'total_cases': len(self.cases),
            'open_cases': len([c for c in self.cases if c['status'] == 'open']),
            'resolved_cases': len([c for c in self.cases if c['status'] == 'resolved']),
            'high_priority': len([c for c in self.cases if c['priority'] == 'HIGH']),
            'medium_priority': len([c for c in self.cases if c['priority'] == 'MEDIUM']),
            'low_priority': len([c for c in self.cases if c['priority'] == 'LOW']),
            'resolutions': {}
        }

        # Count resolutions
        for case in self.cases:
            if case['resolution']:
                summary['resolutions'][case['resolution']] = summary['resolutions'].get(case['resolution'], 0) + 1

        return summary

    def auto_assign_cases(self, num_analysts=3):
        """Auto-assign cases to analysts based on workload"""
        print("\nAuto-assigning cases to analysts...")

        # Track analyst workload
        analyst_workload = {f'Analyst_{i+1}': 0 for i in range(num_analysts)}

        # Assign high priority cases first
        high_priority = [c for c in self.cases if c['priority'] == 'HIGH' and c['assigned_to'] == 'Analyst']
        medium_priority = [c for c in self.cases if c['priority'] == 'MEDIUM' and c['assigned_to'] == 'Analyst']
        low_priority = [c for c in self.cases if c['priority'] == 'LOW' and c['assigned_to'] == 'Analyst']

        all_cases = high_priority + medium_priority + low_priority

        for case in all_cases:
            # Find analyst with lowest workload
            min_analyst = min(analyst_workload, key=analyst_workload.get)
            case['assigned_to'] = min_analyst
            analyst_workload[min_analyst] += 1

        print(f"[OK] Assigned {len(all_cases)} cases to {num_analysts} analysts")
        for analyst, count in analyst_workload.items():
            print(f"  {analyst}: {count} cases")

    def get_cases_by_analyst(self, analyst_name):
        """Get all cases assigned to a specific analyst"""
        return [c for c in self.cases if c['assigned_to'] == analyst_name]

    def export_cases_to_df(self):
        """Export cases to DataFrame for analysis"""
        case_data = []

        for case in self.cases:
            case_data.append({
                'case_id': case['case_id'],
                'alert_id': case['alert_id'],
                'customer_id': case['customer_id'],
                'assigned_to': case['assigned_to'],
                'created_date': case['created_date'],
                'status': case['status'],
                'priority': case['priority'],
                'risk_score': case['risk_score'],
                'alert_type': case['alert_type'],
                'resolution': case['resolution'],
                'resolved_date': case['resolved_date'],
                'investigation_notes_count': len(case['investigation_notes']),
                'evidence_count': len(case['evidence'])
            })

        return pd.DataFrame(case_data)
