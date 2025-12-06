import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json

# --- SETUP FIREBASE ---
# We check if Firebase is already initialized to avoid errors when the app refreshes
if not firebase_admin._apps:
    # Load the secret key from Streamlit's internal secrets management
    key_dict = json.loads(st.secrets["textkey"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- APP LAYOUT ---
st.title("⚡ Energy Price Sentinel")

# Create tabs for the two main functions
tab1, tab2 = st.tabs(["📝 Data Drop", "📈 Market Dashboard"])

# --- TAB 1: DATA ENTRY ---
with tab1:
    st.header("Add Competitor Price")
    with st.form("price_form"):
        # The Inputs
        col1, col2 = st.columns(2)
        provider = col1.selectbox("Brand", [
            "Origin", "AGL", "EnergyAustralia", "Red Energy", 
            "Lumo Energy", "Alinta", "Simply Energy", "Powershop", 
            "Momentum", "Tango", "OVO", "Sumo", "Dodo", "Kogan", 
            "1st Energy", "GloBird", "Blue NRG", "CovaU", "Diamond", "Amber"
        ])
        fuel = col2.selectbox("Fuel Type", ["Electricity", "Gas"])
        
        state = st.selectbox("State", ["VIC", "NSW", "QLD", "SA"])
        zone = st.radio("Zone", ["Metro", "Regional"], horizontal=True)
        
        # User only enters monthly; we calc the rest
        monthly_cost = st.number_input("Monthly Cost ($)", min_value=0.0, step=0.1)
        
        # Submit Button
        submitted = st.form_submit_button("💾 Save Price")
        
        if submitted:
            # Prepare data package
            new_data = {
                "date": pd.Timestamp.now(),
                "provider": provider,
                "fuel": fuel,
                "state": state,
                "zone": zone,
                "monthly": monthly_cost,
                "yearly": monthly_cost * 12
            }
            # Send to Firebase
            db.collection("prices").add(new_data)
            st.success(f"Saved: {provider} - ${monthly_cost}/mo")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.header("Competitor Trends")
    
    # 1. Fetch Data
    docs = db.collection("prices").stream()
    data = [doc.to_dict() for doc in docs]
    
    if data:
        df = pd.DataFrame(data)
        
        # 2. Filters
        st.subheader("Filters")
        f_state = st.selectbox("Filter State", df['state'].unique())
        f_fuel = st.selectbox("Filter Fuel", df['fuel'].unique())
        f_zone = st.selectbox("Filter Zone", df['zone'].unique())
        
        # Apply Filters
        mask = (df['state'] == f_state) & (df['fuel'] == f_fuel) & (df['zone'] == f_zone)
        filtered_df = df[mask]
        
        if not filtered_df.empty:
            # 3. Best Price Table
            st.markdown("### 🏆 Leaderboard (Cheapest First)")
            leaderboard = filtered_df.sort_values("yearly").groupby("provider").last()
            st.dataframe(leaderboard[["yearly", "monthly"]].sort_values("yearly"))
            
            # 4. Chart
            st.markdown("### 📊 Price History")
            st.line_chart(filtered_df, x="date", y="monthly", color="provider")
        else:
            st.warning("No data found for these filters.")
    else:
        st.info("Database is empty. Go to 'Data Drop' to add your first price!")
        # ... (rest of the script remains the same)

# --- TAB 1: DATA ENTRY ---
with tab1:
    st.header("Add Competitor Price")
    with st.form("price_form"):
        # The Inputs
        col1, col2 = st.columns(2)
        provider = col1.selectbox("Brand", [
            # ... (your 20 providers list)
        ])
        fuel = col2.selectbox("Fuel Type", ["Electricity", "Gas"])
        
        state = st.selectbox("State", ["VIC", "NSW", "QLD", "SA"])
        zone = st.radio("Zone", ["Metro", "Regional"], horizontal=True)
        
        # ADD THIS NEW FIELD (or similar)
        annual_usage = st.number_input("Annual Usage (kWh/MJ)", min_value=1000.0, step=100.0) 
        
        monthly_cost = st.number_input("Monthly Cost ($)", min_value=0.0, step=0.1)
        
        # Submit Button
        submitted = st.form_submit_button("💾 Save Price")
        
        if submitted:
            # Prepare data package
            new_data = {
                "date": pd.Timestamp.now(),
                "provider": provider,
                "fuel": fuel,
                "state": state,
                "zone": zone,
                "annual_usage": annual_usage, # NEW FIELD
                "monthly": monthly_cost,
                "yearly": monthly_cost * 12
            }
            # Send to Firebase
            db.collection("prices").add(new_data)
            st.success(f"Saved: {provider} - ${monthly_cost}/mo")

# ... (rest of the script remains the same)

