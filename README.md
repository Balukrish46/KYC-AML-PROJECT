# AML Transaction Monitoring System

A comprehensive Anti-Money Laundering (AML) and Know Your Customer (KYC) transaction monitoring system that demonstrates end-to-end financial crime detection capabilities.

## 🎯 Project Overview

This project implements a production-ready AML monitoring system that:
- Detects suspicious transaction patterns using rule-based and ML-based methods
- Calculates comprehensive risk scores for customers and alerts
- Manages investigation cases with workflow automation
- Generates detailed investigation reports
- Provides interactive analytics dashboards

## 🚀 Features

### 1. Transaction Data Generation
- Generates realistic synthetic transaction data (5,000+ transactions)
- Includes AML typologies: structuring, layering, rapid movement
- Supports 100+ customer profiles with varying risk levels
- Configurable patterns and volumes

### 2. Rule-Based AML Detection
- **Structuring Detection**: Identifies smurfing patterns (transactions just below reporting thresholds)
- **Layering Detection**: Detects rapid fund movement through multiple accounts
- **Rapid Movement Detection**: Flags high-frequency transactions in short time windows
- **High-Risk Country Screening**: Monitors transactions to/from sanctioned jurisdictions
- **Round Amount Detection**: Identifies suspicious round number transactions

### 3. ML-Based Anomaly Detection
- **Isolation Forest**: Unsupervised learning for anomaly detection
- **DBSCAN Clustering**: Density-based clustering for pattern identification
- Feature engineering: temporal, amount, and customer behavior features
- Feature importance analysis for model interpretability

### 4. Risk Scoring System
- Multi-factor risk assessment for alerts
- Customer-level risk profiling
- Adjustable risk weights and thresholds
- Risk categorization (HIGH/MEDIUM/LOW)

### 5. Case Management
- Automated case creation from high-priority alerts
- Case assignment and workload balancing
- Investigation notes and evidence tracking
- Case resolution workflow

### 6. Report Generation
- Detailed investigation reports per case
- Summary reports with case statistics
- Excel exports with multiple sheets (Cases, Transactions, Customers)
- Timestamped audit trails

### 7. Analytics Dashboard
- Interactive visualizations using Plotly
- Alert distribution by type
- Customer risk distribution
- Transaction timeline analysis
- Case workload metrics
- HTML dashboard export

## 📋 System Requirements

- Python 3.8+
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- plotly
- openpyxl
- reportlab
- faker

## 🛠️ Installation

1. Clone the repository:
```bash
cd aml-transaction-monitoring
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Run the Complete System

Execute the main application to run the entire AML monitoring workflow:

```bash
python main.py
```

This will:
1. Generate synthetic transaction data
2. Run rule-based AML detection
3. Execute ML-based anomaly detection
4. Calculate risk scores
5. Create investigation cases
6. Generate reports
7. Create analytics dashboard

### Run Individual Components

#### Generate Data Only
```bash
python data_generator.py
```

#### Run Dashboard Standalone
```bash
python dashboard.py
```

## 📁 Project Structure

```
aml-transaction-monitoring/
├── main.py                    # Main application entry point
├── config.py                  # Configuration settings
├── data_generator.py          # Transaction data generation
├── aml_detector.py            # Rule-based AML detection
├── ml_detector.py             # ML-based anomaly detection
├── risk_scorer.py             # Risk scoring system
├── case_management.py         # Case management workflow
├── report_generator.py       # Report generation
├── dashboard.py              # Analytics dashboard
├── requirements.txt          # Python dependencies
├── data/                     # Data directory
│   ├── transactions.csv     # Transaction data
│   └── customers.csv        # Customer data
└── reports/                  # Output directory
    ├── report_*.txt         # Individual case reports
    ├── summary_report_*.txt # Summary reports
    ├── aml_report_*.xlsx    # Excel reports
    └── dashboard.html       # Interactive dashboard
```

## 🎓 Skills Demonstrated

This project demonstrates the following skills relevant to AML/KYC compliance roles:

### Technical Skills
- **Python Programming**: Advanced data processing and automation
- **Machine Learning**: Unsupervised learning for anomaly detection
- **Data Analysis**: Large-scale transaction pattern analysis
- **Statistical Analysis**: Risk scoring and probability assessment
- **Database Management**: Data generation and CSV processing

### AML/KYC Knowledge
- **AML Typologies**: Understanding of structuring, layering, smurfing
- **Risk Assessment**: Multi-factor risk evaluation
- **Compliance Workflow**: Case management and investigation processes
- **Regulatory Knowledge**: Sanctions screening and high-risk jurisdictions
- **Report Generation**: Audit-ready documentation

### Process Improvement
- **Automation**: End-to-end automated detection workflow
- **Efficiency**: ML-based detection reduces manual review
- **Scalability**: Handles thousands of transactions
- **Decision Making**: Risk-based prioritization
- **Stakeholder Management**: Case assignment and workload balancing

## 📊 System Results

Typical execution produces:
- **5,000 transactions** analyzed
- **100 customers** profiled
- **2,000+ alerts** generated across 7 detection types
- **10 high-priority investigation cases** created
- **Interactive dashboard** with visualizations

## 🔧 Configuration

Key settings in `config.py`:

```python
# Detection thresholds
STRUCTURING_THRESHOLD = 10000
STRUCTURING_TIME_WINDOW_DAYS = 2
RAPID_MOVEMENT_THRESHOLD = 5
RAPID_MOVEMENT_TIME_WINDOW_HOURS = 24

# Risk weights
RISK_WEIGHTS = {
    'amount_above_threshold': 30,
    'high_risk_country': 25,
    'rapid_movement': 20,
    # ...
}

# ML settings
ANOMALY_THRESHOLD = 0.1
```

## 📝 Output Files

After execution, check the `reports/` directory for:
- `report_CASE*.txt` - Individual investigation reports
- `summary_report_*.txt` - Overall case summary
- `aml_report_*.xlsx` - Excel export with all data
- `dashboard.html` - Interactive visual dashboard

## 🎯 Job Alignment

This project directly addresses the requirements for AML/KYC compliance roles:

- ✅ **Transaction Analysis**: Pattern identification and legitimacy verification
- ✅ **AML Typologies**: Detection of structuring, layering, and rapid movement
- ✅ **Risk Assessment**: Comprehensive customer and alert risk scoring
- ✅ **Investigation**: Thorough case management and evidence collection
- ✅ **Reporting**: Detailed investigation reports with audit trails
- ✅ **Process Improvement**: Automated workflow reduces manual effort
- ✅ **Stakeholder Management**: Case assignment and workload balancing
- ✅ **Data Analysis**: Handling large volumes of unstructured transaction data

## 🚧 Future Enhancements

Potential improvements:
- Real-time transaction monitoring integration
- Web-based UI for case management
- Integration with external sanctions databases (OpenSanctions)
- Alert tuning and false positive reduction
- Natural language processing for adverse media
- Network graph visualization for entity relationships
- API endpoints for system integration

## 📄 License

This project is for educational and demonstration purposes.

## 👤 Author

Developed as a demonstration of AML/KYC compliance capabilities.

## 🙏 Acknowledgments

- Scikit-learn for ML algorithms
- Plotly for interactive visualizations
- Faker for synthetic data generation
