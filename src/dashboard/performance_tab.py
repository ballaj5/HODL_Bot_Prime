# src/dashboard/performance_tab.py
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from datetime import datetime, timedelta
import random # Used for simulating outcomes

def load_performance_data():
    """
    Loads prediction data and simulates outcomes for performance tracking.
    In a real-world scenario, you would join this with actual outcome data.
    """
    try:
        df = pd.read_json("logs/alerts_log.jsonl", lines=True)
        if df.empty:
            return pd.DataFrame(columns=['timestamp', 'is_correct'])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # --- Outcome Simulation ---
        # This is a placeholder. In a real system, you would have a separate
        # process that records the actual market outcome after a prediction.
        random.seed(42)
        df['is_correct'] = [random.random() < 0.75 for _ in range(len(df))] # Simulate a 75% accuracy
        
        return df[['timestamp', 'is_correct']]
    except (FileNotFoundError, ValueError):
        return pd.DataFrame(columns=['timestamp', 'is_correct'])

def calculate_accuracy_metrics(df: pd.DataFrame):
    """Calculates accuracy for 24-hour, 7-day, and 30-day periods."""
    now = datetime.utcnow()
    metrics = {
        'Last 24 Hours': 0.0,
        'Last 7 Days': 0.0,
        'Last 30 Days': 0.0
    }
    
    if df.empty:
        return metrics

    # Filter data for each period and calculate accuracy
    df_24h = df[df['timestamp'] >= now - timedelta(days=1)]
    if not df_24h.empty:
        metrics['Last 24 Hours'] = df_24h['is_correct'].mean() * 100

    df_7d = df[df['timestamp'] >= now - timedelta(days=7)]
    if not df_7d.empty:
        metrics['Last 7 Days'] = df_7d['is_correct'].mean() * 100

    df_30d = df[df['timestamp'] >= now - timedelta(days=30)]
    if not df_30d.empty:
        metrics['Last 30 Days'] = df_30d['is_correct'].mean() * 100
        
    return metrics

def create_performance_chart(metrics: dict):
    """Creates a Figma-style bar chart for the performance metrics."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        marker_color='#4A90E2',
        text=[f'{v:.1f}%' for v in metrics.values()],
        textposition='auto',
        hoverinfo='none'
    ))

    fig.update_layout(
        title_text='Model Prediction Accuracy',
        title_x=0.5,
        yaxis=dict(range=[0, 100], title='Accuracy (%)'),
        xaxis=dict(tickfont=dict(size=14)),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color="black"),
        showlegend=False,
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    return fig

def render_performance_tab():
    """Renders the full performance tab layout."""
    df = load_performance_data()
    metrics = calculate_accuracy_metrics(df)
    chart = create_performance_chart(metrics)
    
    return html.Div([
        dcc.Graph(figure=chart)
    ])
