# src/dashboard/app.py
import dash
from dash import html, dcc, dash_table, Input, Output
import pandas as pd
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Crypto Bot Dashboard"

def load_jsonl(filepath):
    """Loads a .jsonl file into a pandas DataFrame."""
    if not os.path.exists(filepath):
        logging.warning(f"File not found: {filepath}, returning empty DataFrame.")
        return pd.DataFrame()
    try:
        with open(filepath, "r") as f:
            lines = [json.loads(line.strip()) for line in f if line.strip()]
        if not lines: return pd.DataFrame()
        return pd.DataFrame(lines)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error reading {filepath}: {e}")
        return pd.DataFrame()

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1("🧠 LLM Insights Dashboard", style={'textAlign': 'center', 'color': '#4a4a4a'}),
    dcc.Tabs(id="tabs-main", value='tab-alerts', children=[
        dcc.Tab(label="✅ LLM Alerts Sent", value='tab-alerts'),
        dcc.Tab(label="⚠️ Skipped Alerts", value='tab-skipped'),
    ]),
    html.Div(id='tabs-content'),
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])

@app.callback(Output('tabs-content', 'children'),
              Input('tabs-main', 'value'),
              Input('interval-component', 'n_intervals'))
def render_content(tab, n):
    """Renders the content of the selected tab and updates on an interval."""
    if tab == 'tab-alerts':
        df = load_jsonl("logs/alerts_log.jsonl")
        title = "LLM-Based Alerts (Confidence ≥ 70%)"
    elif tab == 'tab-skipped':
        df = load_jsonl("logs/skipped_llm_alerts.jsonl")
        title = "LLM Alerts Skipped (Confidence < 70%)"
    else:
        return html.Div()

    if df.empty:
        return html.Div([html.H3(title), html.P("No data to display yet.")])

    return html.Div([
        html.H3(title, style={'color': '#6a6a6a'}),
        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=15,
            style_table={"overflowX": "auto"},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ]
        )
    ])

if __name__ == "__main__":
    # Corrected method call from app.run_server to app.run
    app.run(debug=True, host="0.0.0.0", port=8050)