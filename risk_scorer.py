"""
Risk Scoring System
Calculates comprehensive risk scores for alerts and customers
"""

import pandas as pd
import numpy as np
import config


class RiskScorer:
    """Calculate risk scores for alerts and customers"""

    def __init__(self, alerts_df, transactions_df, customers_df):
        self.alerts = alerts_df
        self.transactions = transactions_df
        self.customers = customers_df
        self.customer_risk_scores = {}

    def calculate_alert_risk(self, alert):
        """Calculate comprehensive risk score for an alert"""
        base_score = alert['risk_score']

        # Adjust based on customer profile
        customer = self.customers[self.customers['customer_id'] == alert['customer_id']]
        if not customer.empty:
            customer = customer.iloc[0]

            # High-risk country customer
            if customer['is_high_risk']:
                base_score += 15

            # New customer (less than 90 days)
            if customer['account_age_days'] < 90:
                base_score += 10

            # Corporate customers might have higher risk
            if customer['customer_type'] == 'corporate':
                base_score += 5

        # Adjust based on transaction patterns
        alert_txns = self.transactions[
            self.transactions['transaction_id'].isin(alert['transaction_ids'])
        ]

        if not alert_txns.empty:
            # High amount
            if alert_txns['amount'].max() > 50000:
                base_score += 10

            # Multiple transactions
            if len(alert_txns) > 5:
                base_score += 5

        # Cap at 100
        return min(100, base_score)

    def calculate_customer_risk(self, customer_id):
        """Calculate overall risk score for a customer"""
        if customer_id in self.customer_risk_scores:
            return self.customer_risk_scores[customer_id]

        customer = self.customers[self.customers['customer_id'] == customer_id]
        if customer.empty:
            return 0

        customer = customer.iloc[0]
        base_score = 0

        # Base risk from customer profile
        if customer['is_high_risk']:
            base_score += 30

        if customer['customer_type'] == 'corporate':
            base_score += 10

        if customer['account_age_days'] < 90:
            base_score += 15
        elif customer['account_age_days'] < 365:
            base_score += 5

        # Risk from alerts
        customer_alerts = self.alerts[self.alerts['customer_id'] == customer_id]

        if not customer_alerts.empty:
            # Add alert scores weighted by recency
            for _, alert in customer_alerts.iterrows():
                alert_risk = self.calculate_alert_risk(alert)
                base_score += alert_risk * 0.3

        # Risk from transaction patterns
        customer_txns = self.transactions[self.transactions['customer_id'] == customer_id]

        if not customer_txns.empty:
            # High volume of transactions
            if len(customer_txns) > 100:
                base_score += 10

            # High total amount
            total_amount = customer_txns['amount'].sum()
            if total_amount > 1000000:
                base_score += 15

            # High average amount
            avg_amount = customer_txns['amount'].mean()
            if avg_amount > 50000:
                base_score += 10

        # Cap at 100
        final_score = min(100, int(base_score))
        self.customer_risk_scores[customer_id] = final_score

        return final_score

    def get_risk_category(self, score):
        """Get risk category based on score"""
        if score >= 70:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'

    def calculate_all_customer_risks(self):
        """Calculate risk scores for all customers"""
        print("\nCalculating customer risk scores...")

        for customer_id in self.customers['customer_id']:
            self.calculate_customer_risk(customer_id)

        # Create customer risk DataFrame
        risk_data = []
        for customer_id, score in self.customer_risk_scores.items():
            customer = self.customers[self.customers['customer_id'] == customer_id].iloc[0]
            risk_data.append({
                'customer_id': customer_id,
                'customer_name': customer['name'],
                'country': customer['country'],
                'customer_type': customer['customer_type'],
                'risk_score': score,
                'risk_category': self.get_risk_category(score),
                'account_age_days': customer['account_age_days']
            })

        risk_df = pd.DataFrame(risk_data)
        risk_df = risk_df.sort_values('risk_score', ascending=False)

        print(f"[OK] Calculated risk scores for {len(risk_df)} customers")
        print(f"  High risk: {len(risk_df[risk_df['risk_category'] == 'HIGH'])}")
        print(f"  Medium risk: {len(risk_df[risk_df['risk_category'] == 'MEDIUM'])}")
        print(f"  Low risk: {len(risk_df[risk_df['risk_category'] == 'LOW'])}")

        return risk_df

    def prioritize_alerts(self):
        """Prioritize alerts based on calculated risk scores"""
        print("\nPrioritizing alerts...")

        for idx, alert in self.alerts.iterrows():
            adjusted_score = self.calculate_alert_risk(alert)
            self.alerts.at[idx, 'adjusted_risk_score'] = adjusted_score
            self.alerts.at[idx, 'risk_category'] = self.get_risk_category(adjusted_score)

        # Sort by adjusted risk score
        self.alerts = self.alerts.sort_values('adjusted_risk_score', ascending=False)

        print(f"[OK] Prioritized {len(self.alerts)} alerts")

        return self.alerts
