"""
Configuration settings for AML Transaction Monitoring System
"""

# AML Detection Thresholds
STRUCTURING_THRESHOLD = 10000  # Amount threshold for structuring detection
STRUCTURING_TIME_WINDOW_DAYS = 2  # Time window for structuring
RAPID_MOVEMENT_THRESHOLD = 5  # Number of transactions in short time
RAPID_MOVEMENT_TIME_WINDOW_HOURS = 24
HIGH_RISK_COUNTRIES = [
    'Afghanistan', 'North Korea', 'Iran', 'Syria', 'Yemen',
    'Myanmar', 'South Sudan', 'Somalia', 'Libya'
]

# Risk Scoring Weights
RISK_WEIGHTS = {
    'amount_above_threshold': 30,
    'high_risk_country': 25,
    'rapid_movement': 20,
    'round_amount': 10,
    'unusual_timing': 10,
    'new_customer': 5
}

# ML Model Settings
ANOMALY_THRESHOLD = 0.1  # Isolation Forest contamination
FEATURES = ['amount', 'hour_of_day', 'day_of_week', 'is_weekend', 'is_round_amount']

# Report Settings
REPORT_OUTPUT_DIR = 'reports'
