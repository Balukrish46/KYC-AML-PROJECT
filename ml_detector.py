"""
ML-based Anomaly Detection for AML
Uses unsupervised learning to detect unusual transaction patterns
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import config


class MLAnomalyDetector:
    """Machine learning-based anomaly detection"""

    def __init__(self, transactions_df):
        self.transactions = transactions_df.copy()
        self.transactions['transaction_date'] = pd.to_datetime(self.transactions['transaction_date'])
        self.features = None
        self.scaler = StandardScaler()
        self.isolation_forest = None
        self.dbscan = None
        self.anomalies = []

    def extract_features(self):
        """Extract features for ML models"""
        print("Extracting features for ML models...")

        df = self.transactions.copy()

        # Temporal features
        df['hour_of_day'] = df['transaction_date'].dt.hour
        df['day_of_week'] = df['transaction_date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

        # Amount features
        df['is_round_amount'] = (df['amount'] % 1000 == 0).astype(int)
        df['amount_log'] = np.log1p(df['amount'])

        # Customer features (transaction frequency and amounts)
        customer_stats = df.groupby('customer_id').agg({
            'amount': ['mean', 'std', 'count'],
            'transaction_date': ['min', 'max']
        }).reset_index()

        customer_stats.columns = ['customer_id', 'avg_amount', 'std_amount',
                                  'txn_count', 'first_txn', 'last_txn']

        df = df.merge(customer_stats, on='customer_id', how='left')

        # Z-score of amount relative to customer's average
        df['amount_zscore'] = (df['amount'] - df['avg_amount']) / (df['std_amount'] + 1e-6)

        # Select features for ML
        feature_cols = config.FEATURES + ['amount_log', 'amount_zscore', 'txn_count']

        self.features = df[feature_cols].fillna(0)

        print(f"[OK] Extracted {len(feature_cols)} features")
        print(f"[OK] Feature shape: {self.features.shape}")

        return self.features

    def train_isolation_forest(self):
        """Train Isolation Forest for anomaly detection"""
        print("\nTraining Isolation Forest...")

        # Scale features
        scaled_features = self.scaler.fit_transform(self.features)

        # Train Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=config.ANOMALY_THRESHOLD,
            random_state=42,
            n_estimators=100
        )

        self.isolation_forest.fit(scaled_features)

        # Predict anomalies
        predictions = self.isolation_forest.predict(scaled_features)
        anomaly_scores = self.isolation_forest.score_samples(scaled_features)

        # Add to transactions
        self.transactions['isolation_anomaly'] = predictions == -1
        self.transactions['isolation_score'] = anomaly_scores

        # Create alerts for anomalies
        anomalies = self.transactions[self.transactions['isolation_anomaly']]

        for _, txn in anomalies.iterrows():
            details = {
                'anomaly_score': round(txn['isolation_score'], 4),
                'amount': txn['amount']
            }
            if 'hour_of_day' in txn:
                details['hour_of_day'] = txn['hour_of_day']
            if 'amount_zscore' in txn:
                details['amount_zscore'] = round(txn['amount_zscore'], 2)

            self.anomalies.append({
                'alert_id': f'MLIF{len(self.anomalies)+1:05d}',
                'alert_type': 'ml_isolation_forest',
                'customer_id': txn['customer_id'],
                'transaction_ids': [txn['transaction_id']],
                'detection_date': pd.Timestamp.now(),
                'risk_score': int(abs(txn['isolation_score']) * 100),
                'details': details,
                'status': 'open'
            })

        print(f"[OK] Isolation Forest detected {len(anomalies)} anomalies")

    def train_dbscan(self):
        """Train DBSCAN for clustering-based anomaly detection"""
        print("\nTraining DBSCAN...")

        # Scale features
        scaled_features = self.scaler.transform(self.features)

        # Train DBSCAN
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        clusters = self.dbscan.fit_predict(scaled_features)

        # Add cluster labels
        self.transactions['cluster'] = clusters

        # Points with cluster = -1 are anomalies
        anomalies = self.transactions[self.transactions['cluster'] == -1]

        for _, txn in anomalies.iterrows():
            details = {
                'cluster': -1,
                'amount': txn['amount']
            }
            if 'hour_of_day' in txn:
                details['hour_of_day'] = txn['hour_of_day']

            self.anomalies.append({
                'alert_id': f'MLDB{len(self.anomalies)+1:05d}',
                'alert_type': 'ml_dbscan',
                'customer_id': txn['customer_id'],
                'transaction_ids': [txn['transaction_id']],
                'detection_date': pd.Timestamp.now(),
                'risk_score': 70,
                'details': details,
                'status': 'open'
            })

        print(f"[OK] DBSCAN detected {len(anomalies)} anomalies")

    def run_detection(self):
        """Run all ML-based detections"""
        print("\n" + "="*60)
        print("RUNNING ML-BASED ANOMALY DETECTION")
        print("="*60 + "\n")

        self.extract_features()
        self.train_isolation_forest()
        self.train_dbscan()

        print(f"\n[OK] Total ML anomalies detected: {len(self.anomalies)}")

        return pd.DataFrame(self.anomalies)

    def get_feature_importance(self):
        """Get feature importance based on anomaly scores"""
        if self.isolation_forest is None:
            return None

        # Calculate feature importance using correlation with anomaly scores
        scaled_features = self.scaler.transform(self.features)
        anomaly_scores = self.isolation_forest.score_samples(scaled_features)

        importance = {}
        for i, col in enumerate(self.features.columns):
            correlation = np.corrcoef(scaled_features[:, i], anomaly_scores)[0, 1]
            importance[col] = abs(correlation)

        return sorted(importance.items(), key=lambda x: x[1], reverse=True)
