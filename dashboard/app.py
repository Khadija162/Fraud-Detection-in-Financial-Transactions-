import os
import requests
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
st.set_page_config(page_title="FraudShield", layout="wide")
st.title("FraudShield · Fraud Operations")
st.caption("Fraud analytics and model diagnostics — demo, not financial advice")

def fetch(path):
    try:
        r = requests.get(API + path, timeout=6)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return {}

health = fetch("/ready")
metrics = fetch("/metrics")
st.metric("Model available", "Yes" if health.get("ready") else "No")
if metrics.get("available") is not False and metrics:
    a, b, c = st.columns(3)
    a.metric("PR-AUC", f"{metrics.get('average_precision', 0):.3f}")
    b.metric("Recall", f"{metrics.get('recall', 0):.3f}")
    c.metric("Precision", f"{metrics.get('precision', 0):.3f}")
    st.caption("Evaluation metrics from the locally trained model; inspect dataset provenance.")
else:
    st.info("Run the data pipeline and model training to see evaluation metrics.")

gold = fetch("/gold/daily").get("rows", [])
if gold:
    st.subheader("Daily transaction volumes")
    st.dataframe(gold, use_container_width=True)
else:
    st.info("Gold aggregates not available yet.")
st.warning("No public authentication is configured. Keep the demo on localhost.")
