"""Streamlit monitoring and manual inference UI."""
import os
import requests
import streamlit as st
st.set_page_config(page_title="Fraud Detection Control Center", layout="wide")
st.title("Financial Transaction Fraud Detection")
st.caption("Portfolio demonstration with synthetic/public PaySim transactions")
api = os.getenv("API_URL", "http://localhost:8000")
try:
    health = requests.get(api + "/health", timeout=4).json()
    st.info(f"API: {health['status']} | Trained model present: {health['model_available']}")
except (requests.RequestException, ValueError, KeyError):
    st.warning("API is unavailable; start FastAPI first.")
a, b, c = st.columns(3)
step = a.number_input("Simulation hour", min_value=0, value=10)
kind = b.selectbox("Type", ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT", "CASH_IN"])
amount = c.number_input("Amount", min_value=0.0, value=1000.0)
old_origin = st.number_input("Origin balance before", value=2000.0)
new_origin = st.number_input("Origin balance after", value=1000.0)
old_dest = st.number_input("Destination balance before", value=0.0)
new_dest = st.number_input("Destination balance after", value=1000.0)
if st.button("Analyze transaction"):
    payload = {"step": step, "type": kind, "amount": amount, "oldbalanceOrg": old_origin, "newbalanceOrig": new_origin, "oldbalanceDest": old_dest, "newbalanceDest": new_dest}
    try:
        response = requests.post(api + "/predict", json=payload, timeout=10)
        if response.ok:
            result = response.json()
            st.metric("Fraud probability", f"{result['fraud_probability']:.1%}")
            st.warning("Flagged for review") if result["fraud_flag"] else st.success("Below alert threshold")
        else:
            st.error(f"API error {response.status_code}: {response.text}")
    except requests.RequestException as exc:
        st.error(f"Prediction request failed: {exc}")
st.caption("Scores are research predictions, not decisions about a real person.")
