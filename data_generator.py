"""
Transaction Data Generator for AML Testing
Generates realistic transaction data including suspicious patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
import config

fake = Faker()
np.random.seed(42)
random.seed(42)


class TransactionGenerator:
    """Generate synthetic transaction data with AML patterns"""

    def __init__(self, num_customers=100, num_transactions=5000):
        self.num_customers = num_customers
        self.num_transactions = num_transactions
        self.customers = self._generate_customers()

    def _generate_customers(self):
        """Generate customer profiles"""
        customers = []
        for i in range(self.num_customers):
            is_high_risk = i < 10  # 10% high risk customers
            customer = {
                'customer_id': f'CUST{i+1:05d}',
                'name': fake.name(),
                'country': random.choice(config.HIGH_RISK_COUNTRIES) if is_high_risk else fake.country(),
                'customer_type': random.choice(['individual', 'corporate']),
                'account_age_days': random.randint(30, 3650),
                'is_high_risk': is_high_risk,
                'registration_date': fake.date_between(start_date='-5y', end_date='today')
            }
            customers.append(customer)
        return customers

    def _generate_normal_transactions(self, num_txns):
        """Generate normal transaction patterns"""
        transactions = []
        start_date = datetime.now() - timedelta(days=90)

        for _ in range(num_txns):
            customer = random.choice(self.customers)
            txn_date = start_date + timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            # Normal transaction amounts (log-normal distribution)
            amount = np.random.lognormal(mean=7, sigma=1.5)

            transaction = {
                'transaction_id': f'TXN{random.randint(100000, 999999)}',
                'customer_id': customer['customer_id'],
                'transaction_date': txn_date,
                'amount': round(amount, 2),
                'currency': 'USD',
                'transaction_type': random.choice(['transfer', 'payment', 'withdrawal', 'deposit']),
                'counterparty': fake.company(),
                'counterparty_country': fake.country(),
                'description': fake.sentence(),
                'is_suspicious': False,
                'aml_pattern': None
            }
            transactions.append(transaction)

        return transactions

    def _generate_structuring_pattern(self, num_txns=50):
        """Generate structuring (smurfing) pattern - below-threshold transactions"""
        transactions = []
        start_date = datetime.now() - timedelta(days=30)

        for i in range(num_txns):
            customer = random.choice([c for c in self.customers if c['is_high_risk']])
            txn_date = start_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(9, 17),
                minutes=random.randint(0, 59)
            )

            # Just below threshold (e.g., $9,000 - $9,900)
            amount = random.uniform(9000, 9900)

            transaction = {
                'transaction_id': f'TXN{random.randint(100000, 999999)}',
                'customer_id': customer['customer_id'],
                'transaction_date': txn_date,
                'amount': round(amount, 2),
                'currency': 'USD',
                'transaction_type': 'transfer',
                'counterparty': fake.company(),
                'counterparty_country': random.choice(config.HIGH_RISK_COUNTRIES),
                'description': 'Business transfer',
                'is_suspicious': True,
                'aml_pattern': 'structuring'
            }
            transactions.append(transaction)

        return transactions

    def _generate_layering_pattern(self, num_txns=30):
        """Generate layering pattern - rapid movement through multiple accounts"""
        transactions = []
        start_date = datetime.now() - timedelta(days=7)

        # Create a chain of transactions
        customer = random.choice([c for c in self.customers if c['is_high_risk']])
        base_amount = 50000

        for i in range(num_txns):
            txn_date = start_date + timedelta(
                hours=random.randint(0, 168),  # Within 7 days
                minutes=random.randint(0, 59)
            )

            # Decreasing amounts as money moves through chain
            amount = base_amount * (0.9 ** i) + random.uniform(-1000, 1000)

            transaction = {
                'transaction_id': f'TXN{random.randint(100000, 999999)}',
                'customer_id': customer['customer_id'],
                'transaction_date': txn_date,
                'amount': round(amount, 2),
                'currency': 'USD',
                'transaction_type': 'transfer',
                'counterparty': f'INTERMEDIARY_{i}',
                'counterparty_country': fake.country(),
                'description': f'Layering step {i+1}',
                'is_suspicious': True,
                'aml_pattern': 'layering'
            }
            transactions.append(transaction)

        return transactions

    def _generate_rapid_movement_pattern(self, num_txns=40):
        """Generate rapid movement pattern - many transactions in short time"""
        transactions = []
        start_date = datetime.now() - timedelta(days=1)

        customer = random.choice([c for c in self.customers if c['is_high_risk']])

        for i in range(num_txns):
            txn_date = start_date + timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59)
            )

            amount = random.uniform(5000, 15000)

            transaction = {
                'transaction_id': f'TXN{random.randint(100000, 999999)}',
                'customer_id': customer['customer_id'],
                'transaction_date': txn_date,
                'amount': round(amount, 2),
                'currency': 'USD',
                'transaction_type': 'transfer',
                'counterparty': fake.company(),
                'counterparty_country': fake.country(),
                'description': 'Multiple transfers',
                'is_suspicious': True,
                'aml_pattern': 'rapid_movement'
            }
            transactions.append(transaction)

        return transactions

    def generate_dataset(self):
        """Generate complete dataset with all patterns"""
        print("Generating transaction dataset...")

        # Generate normal transactions
        normal_txns = self._generate_normal_transactions(self.num_transactions - 120)
        print(f"Generated {len(normal_txns)} normal transactions")

        # Generate suspicious patterns
        structuring = self._generate_structuring_pattern(50)
        print(f"Generated {len(structuring)} structuring pattern transactions")

        layering = self._generate_layering_pattern(30)
        print(f"Generated {len(layering)} layering pattern transactions")

        rapid_movement = self._generate_rapid_movement_pattern(40)
        print(f"Generated {len(rapid_movement)} rapid movement pattern transactions")

        # Combine all transactions
        all_transactions = normal_txns + structuring + layering + rapid_movement

        # Create DataFrame
        df = pd.DataFrame(all_transactions)
        df = df.sort_values('transaction_date').reset_index(drop=True)

        print(f"\nTotal transactions generated: {len(df)}")
        print(f"Suspicious transactions: {df['is_suspicious'].sum()}")
        print(f"Suspicious rate: {df['is_suspicious'].sum() / len(df) * 100:.2f}%")

        return df, self.customers


if __name__ == '__main__':
    generator = TransactionGenerator(num_customers=100, num_transactions=5000)
    transactions_df, customers = generator.generate_dataset()

    # Save to CSV
    transactions_df.to_csv('data/transactions.csv', index=False)
    print("\n[OK] Transaction data saved to data/transactions.csv")

    # Save customer data
    customers_df = pd.DataFrame(customers)
    customers_df.to_csv('data/customers.csv', index=False)
    print("[OK] Customer data saved to data/customers.csv")
