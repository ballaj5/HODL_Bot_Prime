# src/dashboard/app.py
import streamlit as st
import pandas as pd
import os
import ccxt
from datetime import datetime
import pytz
from src.utils.database import get_accuracy_stats, get_live_signals
from src.telegram.send_alert import send_test_alert

# --- Page Configuration & Styling ---
st.set_page_config(layout="wide", page_title="Crypto Trading Prediction")

# Figma-style CSS
st.markdown("""
<style>
    /* General styling */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1, h2, h3 { font-weight: 700; }
    /* Metric cards for accuracy */
    .metric-card { background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 1.5rem; text-align: center; }
    .metric-card h3 { font-size: 2.5rem; color: #2ECC71; }
    .metric-card p { font-size: 1rem; color: #A0AEC0; margin-top: 0.5rem; }
    /* Signal rows */
    .signal-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1fr; align-items: center; background-color: #161B22; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #30363D; }
    .coin-info { display: flex; align-items: center; gap: 1rem; }
    .coin-info img { width: 40px; height: 40px; }
    .confidence-text { font-size: 1.5rem; font-weight: bold; text-align: right; }
</style>
""", unsafe_allow_html=True)


# --- Header & Controls ---
st.title("Crypto Trading Prediction")

# Use session state to keep the confidence value
if 'confidence_threshold' not in st.session_state:
    st.session_state.confidence_threshold = 70.0

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("⚙️ Controls")
    
    # Confidence Threshold Slider
    st.session_state.confidence_threshold = st.slider(
        "Confidence Threshold (%)", 
        min_value=0.0, max_value=100.0, 
        value=st.session_state.confidence_threshold, 
        step=1.0,
        help="Filter signals displayed below by their minimum confidence level."
    )
    
    # --- CORRECTED TELEGRAM CONTROLS ---
    st.subheader("Telegram Alerts")
    ALERT_FLAG_PATH = "/workspace/data/alerts_on.flag"

    # This function is called ONLY when the toggle is clicked
    def toggle_alerts_state():
        if st.session_state.alerts_enabled:
            if not os.path.exists(ALERT_FLAG_PATH):
                open(ALERT_FLAG_PATH, 'a').close()
                st.toast("Alerts enabled!", icon="🔔")
        else:
            if os.path.exists(ALERT_FLAG_PATH):
                os.remove(ALERT_FLAG_PATH)
                st.toast("Alerts disabled.", icon="🔕")

    st.toggle(
        "Enable Alerts", 
        value=os.path.exists(ALERT_FLAG_PATH), 
        key="alerts_enabled", 
        on_change=toggle_alerts_state # This is the callback
    )

    if st.button("Send Test Alert"):
        send_test_alert()
        st.toast("Test alert sent!", icon="✅")


# --- Live Signals Display ---
st.header(f"Live Signals (Confidence ≥ {st.session_state.confidence_threshold:.0f}%)")

live_signals = get_live_signals(st.session_state.confidence_threshold)

if not live_signals:
    st.info("No signals meet the current criteria.")
else:
    # Display Header
    st.markdown("""
        <div class="signal-row" style="background-color: transparent; border: none; font-weight: bold; color: #A0AEC0;">
            <div>Coin</div>
            <div>Signal</div>
            <div>Timeframe</div>
            <div>Price at Alert</div>
            <div style="text-align: right;">Confidence</div>
        </div>
    """, unsafe_allow_html=True)

    for signal in live_signals:
        signal_dict = dict(signal)
        
        # Correctly format the symbol for the icon URL, handling special cases like '1000PEPE'
        icon_symbol = signal_dict['symbol'].lower()
        if '1000' in icon_symbol:
            icon_symbol = icon_symbol.replace('1000', '') # Changes '1000pepe' to 'pepe'
            
        icon_url = f"https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@1a63530be6e374711a8554f31b17e4cb92c25659/32/color/{icon_symbol}.png"
        signal_color = "#2ECC71" if signal_dict['signal'] == 'UP' else "#E74C3C"
        
        st.markdown(f"""
            <div class="signal-row">
                <div class="coin-info">
                    <img src="{icon_url}" onerror="this.style.display='none'">
                    <div><strong>{signal_dict['symbol']}</strong></div>
                </div>
                <div><strong style="color: {signal_color};">{signal_dict['signal']}</strong></div>
                <div>{signal_dict['timeframe']}</div>
                <div>${signal_dict.get('price_at_prediction', 0):,.4f}</div>
                <div class="confidence-text" style="color: {signal_color};">{signal_dict['confidence']:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)


# --- Accuracy Stats Section ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.header("Futures Perpetuals Accuracy")
    st.caption("Based on signals >70% confidence")
    perp_stats = get_accuracy_stats('perpetual')
    acc_col1, acc_col2, acc_col3 = st.columns(3)
    with acc_col1:
        st.markdown(f'<div class="metric-card"><h3>{perp_stats["24h"]:.1f}%</h3><p>Last 24h</p></div>', unsafe_allow_html=True)
    with acc_col2:
        st.markdown(f'<div class="metric-card"><h3>{perp_stats["7d"]:.1f}%</h3><p>Last 7d</p></div>', unsafe_allow_html=True)
    with acc_col3:
        st.markdown(f'<div class="metric-card"><h3>{perp_stats["30d"]:.1f}%</h3><p>Last 30d</p></div>', unsafe_allow_html=True)

with col2:
    st.header("Futures Predictions Accuracy")
    st.caption("Based on signals >70% confidence")
    pred_stats = get_accuracy_stats('prediction')
    acc_col4, acc_col5, acc_col6 = st.columns(3)
    with acc_col4:
        st.markdown(f'<div class="metric-card"><h3>{pred_stats["24h"]:.1f}%</h3><p>Last 24h</p></div>', unsafe_allow_html=True)
    with acc_col5:
        st.markdown(f'<div class="metric-card"><h3>{pred_stats["7d"]:.1f}%</h3><p>Last 7d</p></div>', unsafe_allow_html=True)
    with acc_col6:
        st.markdown(f'<div class="metric-card"><h3>{pred_stats["30d"]:.1f}%</h3><p>Last 30d</p></div>', unsafe_allow_html=True)