"""
Analytics Dashboard for AML Transaction Monitoring
Visualizes alerts, risks, and investigation metrics
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class AMLDashboard:
    """Create interactive dashboards for AML monitoring"""

    def __init__(self, transactions_df, alerts_df, customer_risks_df, cases_df):
        self.transactions = transactions_df
        self.alerts = alerts_df
        self.customer_risks_df = customer_risks_df
        self.cases = cases_df

    def create_alert_distribution_chart(self):
        """Create pie chart showing alert distribution by type"""
        alert_counts = self.alerts['alert_type'].value_counts()

        fig = go.Figure(data=[go.Pie(
            labels=alert_counts.index,
            values=alert_counts.values,
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])

        fig.update_layout(
            title='Alert Distribution by Type',
            height=500,
            showlegend=True
        )

        return fig

    def create_risk_distribution_chart(self):
        """Create bar chart showing customer risk distribution"""
        risk_counts = self.customer_risks_df['risk_category'].value_counts()

        fig = go.Figure(data=[go.Bar(
            x=risk_counts.index,
            y=risk_counts.values,
            marker_color=['red', 'orange', 'green']
        )])

        fig.update_layout(
            title='Customer Risk Distribution',
            xaxis_title='Risk Category',
            yaxis_title='Number of Customers',
            height=400
        )

        return fig

    def create_transaction_timeline(self):
        """Create line chart showing transaction volume over time"""
        self.transactions['transaction_date'] = pd.to_datetime(self.transactions['transaction_date'])
        daily_txns = self.transactions.groupby(self.transactions['transaction_date'].dt.date).size()

        fig = go.Figure(data=[go.Scatter(
            x=daily_txns.index,
            y=daily_txns.values,
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        )])

        fig.update_layout(
            title='Transaction Volume Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Transactions',
            height=400
        )

        return fig

    def create_case_workload_chart(self):
        """Create bar chart showing analyst workload"""
        if 'assigned_to' not in self.cases.columns:
            return None

        workload = self.cases['assigned_to'].value_counts()

        fig = go.Figure(data=[go.Bar(
            x=workload.index,
            y=workload.values,
            marker_color=px.colors.qualitative.Pastel1
        )])

        fig.update_layout(
            title='Case Workload by Analyst',
            xaxis_title='Analyst',
            yaxis_title='Number of Cases',
            height=400
        )

        return fig

    def create_risk_score_distribution(self):
        """Create histogram of customer risk scores"""
        fig = go.Figure(data=[go.Histogram(
            x=self.customer_risks_df['risk_score'],
            nbinsx=20,
            marker_color='purple',
            opacity=0.7
        )])

        fig.update_layout(
            title='Customer Risk Score Distribution',
            xaxis_title='Risk Score',
            yaxis_title='Number of Customers',
            height=400
        )

        return fig

    def create_alert_risk_score_chart(self):
        """Create scatter plot of alerts by risk score"""
        fig = go.Figure(data=[go.Scatter(
            x=self.alerts.index,
            y=self.alerts['risk_score'],
            mode='markers',
            marker=dict(
                size=8,
                color=self.alerts['risk_score'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Risk Score')
            ),
            text=self.alerts['alert_type'],
            hovertemplate='<b>%{text}</b><br>Risk Score: %{y}<extra></extra>'
        )])

        fig.update_layout(
            title='Alert Risk Scores',
            xaxis_title='Alert Index',
            yaxis_title='Risk Score',
            height=400
        )

        return fig

    def create_summary_dashboard(self):
        """Create comprehensive summary dashboard"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Alert Distribution', 'Risk Distribution',
                          'Transaction Timeline', 'Case Workload',
                          'Risk Score Distribution', 'Alert Risk Scores'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}],
                   [{'type': 'scatter'}, {'type': 'bar'}],
                   [{'type': 'histogram'}, {'type': 'scatter'}]]
        )

        # Alert Distribution
        alert_counts = self.alerts['alert_type'].value_counts()
        fig.add_trace(go.Pie(
            labels=alert_counts.index,
            values=alert_counts.values,
            hole=0.4
        ), row=1, col=1)

        # Risk Distribution
        risk_counts = self.customer_risks_df['risk_category'].value_counts()
        fig.add_trace(go.Bar(
            x=risk_counts.index,
            y=risk_counts.values,
            marker_color=['red', 'orange', 'green']
        ), row=1, col=2)

        # Transaction Timeline
        self.transactions['transaction_date'] = pd.to_datetime(self.transactions['transaction_date'])
        daily_txns = self.transactions.groupby(self.transactions['transaction_date'].dt.date).size()
        fig.add_trace(go.Scatter(
            x=daily_txns.index,
            y=daily_txns.values,
            mode='lines+markers'
        ), row=2, col=1)

        # Case Workload
        if 'assigned_to' in self.cases.columns:
            workload = self.cases['assigned_to'].value_counts()
            fig.add_trace(go.Bar(
                x=workload.index,
                y=workload.values
            ), row=2, col=2)

        # Risk Score Distribution
        fig.add_trace(go.Histogram(
            x=self.customer_risks_df['risk_score'],
            nbinsx=20
        ), row=3, col=1)

        # Alert Risk Scores
        fig.add_trace(go.Scatter(
            x=self.alerts.index,
            y=self.alerts['risk_score'],
            mode='markers'
        ), row=3, col=2)

        fig.update_layout(
            title_text='AML Transaction Monitoring Dashboard',
            height=1200,
            showlegend=False
        )

        return fig

    def generate_html_report(self, filename='reports/dashboard.html'):
        """Generate HTML dashboard report"""
        import os

        if not os.path.exists('reports'):
            os.makedirs('reports')

        # Create individual charts
        alert_dist = self.create_alert_distribution_chart()
        risk_dist = self.create_risk_distribution_chart()
        timeline = self.create_transaction_timeline()
        workload = self.create_case_workload_chart()
        risk_hist = self.create_risk_score_distribution()
        alert_risk = self.create_alert_risk_score_chart()

        # Create summary dashboard
        summary = self.create_summary_dashboard()

        # Save to HTML
        with open(filename, 'w') as f:
            f.write('<html><head><title>AML Dashboard</title></head><body>')
            f.write('<h1>AML Transaction Monitoring Dashboard</h1>')

            f.write('<h2>Summary Dashboard</h2>')
            f.write(summary.to_html(full_html=False, include_plotlyjs='cdn'))

            f.write('<h2>Alert Distribution</h2>')
            f.write(alert_dist.to_html(full_html=False, include_plotlyjs='cdn'))

            f.write('<h2>Risk Distribution</h2>')
            f.write(risk_dist.to_html(full_html=False, include_plotlyjs='cdn'))

            f.write('<h2>Transaction Timeline</h2>')
            f.write(timeline.to_html(full_html=False, include_plotlyjs='cdn'))

            if workload:
                f.write('<h2>Case Workload</h2>')
                f.write(workload.to_html(full_html=False, include_plotlyjs='cdn'))

            f.write('<h2>Risk Score Distribution</h2>')
            f.write(risk_hist.to_html(full_html=False, include_plotlyjs='cdn'))

            f.write('<h2>Alert Risk Scores</h2>')
            f.write(alert_risk.to_html(full_html=False, include_plotlyjs='cdn'))

            f.write('</body></html>')

        print(f"[OK] Generated HTML dashboard: {filename}")

        return filename


if __name__ == '__main__':
    # Load data
    transactions = pd.read_csv('data/transactions.csv')
    customers = pd.read_csv('data/customers.csv')

    # Generate sample alerts for testing
    alerts_data = []
    for i in range(100):
        alerts_data.append({
            'alert_id': f'ALERT{i:05d}',
            'alert_type': ['structuring', 'layering', 'rapid_movement', 'high_risk_country'][i % 4],
            'customer_id': f'CUST{(i % 10)+1:05d}',
            'risk_score': 30 + (i % 7) * 10,
            'status': 'open'
        })
    alerts = pd.DataFrame(alerts_data)

    # Generate sample customer risks
    customer_risks = []
    for i in range(10):
        score = 100 if i < 3 else (70 if i < 6 else 30)
        customer_risks.append({
            'customer_id': f'CUST{i+1:05d}',
            'customer_name': f'Customer {i+1}',
            'country': 'US',
            'customer_type': 'individual',
            'risk_score': score,
            'risk_category': 'HIGH' if score >= 70 else 'LOW',
            'account_age_days': 100 + i * 50
        })
    customer_risks_df = pd.DataFrame(customer_risks)

    # Generate sample cases
    cases_data = []
    for i in range(10):
        cases_data.append({
            'case_id': f'CASE{i+1:05d}',
            'alert_id': f'ALERT{i:05d}',
            'customer_id': f'CUST{(i % 10)+1:05d}',
            'assigned_to': f'Analyst_{(i % 3)+1}',
            'status': 'open',
            'priority': 'HIGH' if i < 5 else 'MEDIUM',
            'risk_score': 80 if i < 5 else 50
        })
    cases = pd.DataFrame(cases_data)

    # Create dashboard
    dashboard = AMLDashboard(transactions, alerts, customer_risks_df, cases)
    dashboard.generate_html_report()
