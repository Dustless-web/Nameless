import streamlit as st
from dashboard_styles import apply_neo_brutalism_styles
from dashboard_data import fetch_business_metrics, fetch_logs

# 1. Configuration
st.set_page_config(page_title="Basanti Terminal", page_icon="🏪", layout="wide")
apply_neo_brutalism_styles()

# 2. Page Header
st.title("🏪 Basanti: Live Terminal")
st.markdown("**// SYSTEM STATUS: ONLINE**")

try:
    # 3. Metrics Section
    metrics = fetch_business_metrics()
    col1, col2 = st.columns(2)
    col1.metric("TODAY'S REVENUE", f"₹ {metrics['revenue']}")
    col2.metric("MARKET UDHAAR", f"₹ {metrics['udhaar']}")

    st.divider()

    # 4. Main Content Tabs (Improvisation)
    tab1, tab2, tab3 = st.tabs(["📊 Transactions", "📦 Inventory", "📝 Debtors"])

    debtors_df, sales_df, inventory_df = fetch_logs()

    with tab1:
        st.header("RECENT ACTIVITY")
        st.dataframe(sales_df, use_container_width=True, hide_index=True)

    with tab2:
        st.header("STOCK LEVELS")
        if not inventory_df.empty:
            st.dataframe(inventory_df, use_container_width=True, hide_index=True)
        else:
            st.warning("INVENTORY EMPTY. UPLOAD CSV IN TELEGRAM.")

    with tab3:
        st.header("CREDIT OVERVIEW")
        if not debtors_df.empty:
            st.bar_chart(debtors_df.set_index('customer'), color="#03c988")
        else:
            st.info("NO ACTIVE DEBTORS.")

except Exception as e:
    st.error(f"SYSTEM FAULT: {e}")