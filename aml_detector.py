"""
AML Detection Rules Engine
Implements rule-based detection for common AML typologies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config


class AMLDetector:
    """Rule-based AML pattern detection"""

    def __init__(self, transactions_df, customers_df):
        self.transactions = transactions_df.copy()
        self.customers = customers_df
        self.alerts = []

    def detect_structuring(self):
        """
        Detect structuring (smurfing) pattern:
        Multiple transactions just below reporting threshold
        """
        print("Detecting structuring pattern...")

        # Group by customer and time window
        self.transactions['transaction_date'] = pd.to_datetime(self.transactions['transaction_date'])

        for customer_id in self.transactions['customer_id'].unique():
            customer_txns = self.transactions[self.transactions['customer_id'] == customer_id].copy()
            customer_txns = customer_txns.sort_values('transaction_date')

            # Sliding window approach
            for i, txn in customer_txns.iterrows():
                window_start = txn['transaction_date']
                window_end = window_start + timedelta(days=config.STRUCTURING_TIME_WINDOW_DAYS)

                # Get transactions in window
                window_txns = customer_txns[
                    (customer_txns['transaction_date'] >= window_start) &
                    (customer_txns['transaction_date'] <= window_end)
                ]

                # Check if multiple transactions below threshold
                below_threshold = window_txns[window_txns['amount'] < config.STRUCTURING_THRESHOLD]

                if len(below_threshold) >= 3:
                    total_amount = below_threshold['amount'].sum()

                    # Create alert if total exceeds threshold significantly
                    if total_amount > config.STRUCTURING_THRESHOLD * 1.5:
                        alert = {
                            'alert_id': f'STR{len(self.alerts)+1:05d}',
                            'alert_type': 'structuring',
                            'customer_id': customer_id,
                            'transaction_ids': below_threshold['transaction_id'].tolist(),
                            'detection_date': datetime.now(),
                            'risk_score': min(85, 50 + len(below_threshold) * 5),
                            'details': {
                                'transaction_count': len(below_threshold),
                                'total_amount': round(total_amount, 2),
                                'time_window_days': config.STRUCTURING_TIME_WINDOW_DAYS,
                                'average_amount': round(total_amount / len(below_threshold), 2)
                            },
                            'status': 'open'
                        }
                        self.alerts.append(alert)

        print(f"[OK] Found {len([a for a in self.alerts if a['alert_type'] == 'structuring'])} structuring alerts")

    def detect_layering(self):
        """
        Detect layering pattern:
        Rapid movement of funds through multiple accounts
        """
        print("Detecting layering pattern...")

        for customer_id in self.transactions['customer_id'].unique():
            customer_txns = self.transactions[self.transactions['customer_id'] == customer_id].copy()
            customer_txns = customer_txns.sort_values('transaction_date')

            # Look for chains of transactions
            if len(customer_txns) < 5:
                continue

            # Check for rapid sequence of transactions to different counterparties
            for i in range(len(customer_txns) - 5):
                window = customer_txns.iloc[i:i+5]

                # Check if within short time period
                time_diff = (window['transaction_date'].max() - window['transaction_date'].min()).total_seconds() / 3600

                if time_diff < 48:  # Within 48 hours
                    # Check if different counterparties
                    unique_counterparties = window['counterparty'].nunique()

                    if unique_counterparties >= 3:
                        # Check decreasing amounts (typical of layering)
                        amounts = window['amount'].values
                        is_decreasing = all(amounts[i] >= amounts[i+1] * 0.9 for i in range(len(amounts)-1))

                        if is_decreasing:
                            alert = {
                                'alert_id': f'LAY{len(self.alerts)+1:05d}',
                                'alert_type': 'layering',
                                'customer_id': customer_id,
                                'transaction_ids': window['transaction_id'].tolist(),
                                'detection_date': datetime.now(),
                                'risk_score': 90,
                                'details': {
                                    'transaction_count': len(window),
                                    'time_span_hours': round(time_diff, 2),
                                    'unique_counterparties': unique_counterparties,
                                    'total_amount': round(window['amount'].sum(), 2)
                                },
                                'status': 'open'
                            }
                            self.alerts.append(alert)

        print(f"[OK] Found {len([a for a in self.alerts if a['alert_type'] == 'layering'])} layering alerts")

    def detect_rapid_movement(self):
        """
        Detect rapid movement pattern:
        Many transactions in very short time period
        """
        print("Detecting rapid movement pattern...")

        for customer_id in self.transactions['customer_id'].unique():
            customer_txns = self.transactions[self.transactions['customer_id'] == customer_id].copy()
            customer_txns = customer_txns.sort_values('transaction_date')

            if len(customer_txns) < config.RAPID_MOVEMENT_THRESHOLD:
                continue

            # Sliding window for rapid transactions
            for i in range(len(customer_txns) - config.RAPID_MOVEMENT_THRESHOLD + 1):
                window = customer_txns.iloc[i:i+config.RAPID_MOVEMENT_THRESHOLD]

                time_diff = (window['transaction_date'].max() - window['transaction_date'].min()).total_seconds() / 3600

                if time_diff <= config.RAPID_MOVEMENT_TIME_WINDOW_HOURS:
                    alert = {
                        'alert_id': f'RAP{len(self.alerts)+1:05d}',
                        'alert_type': 'rapid_movement',
                        'customer_id': customer_id,
                        'transaction_ids': window['transaction_id'].tolist(),
                        'detection_date': datetime.now(),
                        'risk_score': 75,
                        'details': {
                            'transaction_count': len(window),
                            'time_span_hours': round(time_diff, 2),
                            'total_amount': round(window['amount'].sum(), 2),
                            'average_amount': round(window['amount'].mean(), 2)
                        },
                        'status': 'open'
                    }
                    self.alerts.append(alert)

        print(f"[OK] Found {len([a for a in self.alerts if a['alert_type'] == 'rapid_movement'])} rapid movement alerts")

    def detect_high_risk_countries(self):
        """
        Detect transactions to/from high-risk jurisdictions
        """
        print("Detecting high-risk country transactions...")

        high_risk_txns = self.transactions[
            self.transactions['counterparty_country'].isin(config.HIGH_RISK_COUNTRIES)
        ]

        for _, txn in high_risk_txns.iterrows():
            alert = {
                'alert_id': f'HRC{len(self.alerts)+1:05d}',
                'alert_type': 'high_risk_country',
                'customer_id': txn['customer_id'],
                'transaction_ids': [txn['transaction_id']],
                'detection_date': datetime.now(),
                'risk_score': 60,
                'details': {
                    'country': txn['counterparty_country'],
                    'amount': txn['amount'],
                    'counterparty': txn['counterparty']
                },
                'status': 'open'
            }
            self.alerts.append(alert)

        print(f"[OK] Found {len([a for a in self.alerts if a['alert_type'] == 'high_risk_country'])} high-risk country alerts")

    def detect_round_amounts(self):
        """
        Detect suspicious round amounts (often indicate manual structuring)
        """
        print("Detecting suspicious round amounts...")

        # Define round amount as ending in 000 or with very few decimal places
        self.transactions['is_round_amount'] = self.transactions['amount'].apply(
            lambda x: x % 1000 == 0 or (x * 100) % 100 == 0
        )

        round_txns = self.transactions[
            (self.transactions['is_round_amount']) &
            (self.transactions['amount'] > 5000)
        ]

        for _, txn in round_txns.iterrows():
            alert = {
                'alert_id': f'RND{len(self.alerts)+1:05d}',
                'alert_type': 'round_amount',
                'customer_id': txn['customer_id'],
                'transaction_ids': [txn['transaction_id']],
                'detection_date': datetime.now(),
                'risk_score': 30,
                'details': {
                    'amount': txn['amount'],
                    'is_exactly_round': txn['amount'] % 1000 == 0
                },
                'status': 'open'
            }
            self.alerts.append(alert)

        print(f"[OK] Found {len([a for a in self.alerts if a['alert_type'] == 'round_amount'])} round amount alerts")

    def run_all_detections(self):
        """Run all AML detection rules"""
        print("\n" + "="*60)
        print("RUNNING AML DETECTION RULES")
        print("="*60 + "\n")

        self.detect_structuring()
        self.detect_layering()
        self.detect_rapid_movement()
        self.detect_high_risk_countries()
        self.detect_round_amounts()

        print(f"\n[OK] Total alerts generated: {len(self.alerts)}")

        return pd.DataFrame(self.alerts)

    def get_alert_summary(self):
        """Get summary statistics of alerts"""
        if not self.alerts:
            return None

        alerts_df = pd.DataFrame(self.alerts)

        summary = {
            'total_alerts': len(alerts_df),
            'alerts_by_type': alerts_df['alert_type'].value_counts().to_dict(),
            'average_risk_score': alerts_df['risk_score'].mean(),
            'high_risk_alerts': len(alerts_df[alerts_df['risk_score'] >= 70]),
            'medium_risk_alerts': len(alerts_df[(alerts_df['risk_score'] >= 40) & (alerts_df['risk_score'] < 70)]),
            'low_risk_alerts': len(alerts_df[alerts_df['risk_score'] < 40])
        }

        return summary
