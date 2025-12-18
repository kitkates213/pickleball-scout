import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Import the scout script we just wrote (make sure scout.py is in the same folder)
try:
    import scout
except ImportError:
    st.warning("scout.py not found. The 'Scout' button won't work yet.")

# --- DATABASE SETUP (Runs once when app starts) ---
conn = sqlite3.connect('pickleball_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS drill_stats
             (id INTEGER PRIMARY KEY, date TEXT, drill_name TEXT, 
              metric_value REAL, notes TEXT)''')
conn.commit()

# --- APP INTERFACE ---
st.title("Pickleball Tracker & Scout 🥒")
st.subheader(f"Player Level: 3.5 - 4.0 | Location: 22030")

# --- TAB 1: THE COACH (Drills) ---
tab1, tab2 = st.tabs(["The Coach (Drills)", "The Scout (Tournaments)"])

with tab1:
    st.header("Log Today's Work")
    
    col1, col2 = st.columns(2)
    
    with col1:
        drill_type = st.selectbox(
            "Select Drill", 
            ["7-11 (Singles)", "Dink Loyalty", "Transition Reset", "Drops vs Drives"]
        )
    
    # Dynamic description based on selection
    if drill_type == "Drops vs Drives":
        st.info("🎯 **Goal:** From baseline, hit 10 Drops and 10 Drives. Score +1 for every successful shot.")
        metric_label = "Total Successful Shots (out of 20)"
    elif drill_type == "7-11 (Singles)":
        st.info("🎯 **Goal:** Win 7 points before partner wins 11. You are at net.")
        metric_label = "Did you win? (1=Yes, 0=No)"
    else:
        metric_label = "Score / Success Rate"

    with col2:
        metric = st.number_input(metric_label, min_value=0.0)
        notes = st.text_input("Notes (e.g., 'Forehand drive felt long')")

    if st.button("Save Drill Session"):
        c.execute("INSERT INTO drill_stats (date, drill_name, metric_value, notes) VALUES (?, ?, ?, ?)", 
                  (date.today(), drill_type, metric, notes))
        conn.commit()
        st.success("Saved!")

    st.divider()
    
    # Progress Chart
    st.subheader("Progress Over Time")
    df = pd.read_sql_query("SELECT * FROM drill_stats", conn)
    
    if not df.empty:
        # Convert date string to datetime objects for better graphing
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter by the drill selected above so the chart isn't messy
        drill_data = df[df['drill_name'] == drill_type]
        
        if not drill_data.empty:
            st.line_chart(drill_data, x='date', y='metric_value')
            st.dataframe(drill_data.sort_values(by='date', ascending=False).head(5))
        else:
            st.write(f"No data yet for {drill_type}.")

# --- TAB 2: THE SCOUT ---
with tab2:
    st.header("Tournament Scout")
    st.write("Click below to send the robot to search specifically for events near Fairfax/NoVA.")
    
    if st.button("Launch Scout Robot 🤖"):
        with st.spinner("Scouting the internet... this takes about 10-20 seconds..."):
            try:
                # Run the function from our scout.py file
                results = scout.run_scout() 
                
                if results:
                    st.success(f"Found {len(results)} tournaments!")
                    for tourney in results:
                        st.markdown(f"**{tourney['name']}**")
                        st.markdown(f"[Link to Register]({tourney['link']})")
                        st.divider()
                else:
                    st.warning("No tournaments found matching 'Fairfax' or 'Virginia' right now.")
            except Exception as e:
                st.error(f"Error running scout: {e}")