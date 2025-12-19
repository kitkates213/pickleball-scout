import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import webbrowser

# Try importing the scout script
try:
    import scout
except ImportError:
    st.warning("⚠️ scout.py not found. The 'Scout' tab will be disabled.")

# --- DATABASE SETUP ---
conn = sqlite3.connect('pickleball_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS drill_stats
             (id INTEGER PRIMARY KEY, date TEXT, drill_name TEXT, 
              metric_value REAL, notes TEXT)''')
conn.commit()

# --- APP HEADER ---
st.set_page_config(page_title="Dink Lab", page_icon="🧪")
st.title("🧪 Dink Lab")
st.caption(f"Experiment. Quantify. Improve. | HQ: Fairfax, VA (22030)")

# --- TABS ---
tab1, tab2 = st.tabs(["🔬 The Lab (Drills)", "🔭 The Scout (Tournaments)"])

# --- TAB 1: DRILLS (No changes here, keeping your data safe) ---
with tab1:
    st.header("Daily Experiments")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        drill_type = st.radio("Select Experiment", 
            ["Dink Loyalty", "Transition Reset", "Drops vs Drives", "7-11 Singles"])

    with col2:
        if drill_type == "Dink Loyalty":
            st.subheader("🛡️ Dink Loyalty")
            st.markdown("**Goal:** Win the patience war. No speed-ups allowed.")
            metric_label = "Did you win? (1=Win, 0=Loss)"
        elif drill_type == "Transition Reset":
            st.subheader("🧱 Transition Reset")
            st.markdown("**Goal:** Reset hard drives into the kitchen. Move forward on success.")
            metric_label = "Successful Resets (out of 10)"
        elif drill_type == "Drops vs Drives":
            st.subheader("🧠 Drops vs Drives")
            st.markdown("**Goal:** Deep ball = DROP. Short ball = DRIVE. +1 for correct choice & execution.")
            metric_label = "Score (Max 20)"
        elif drill_type == "7-11 Singles":
            st.subheader("🏃 7-11 Singles")
            st.markdown("**Goal:** You (at net) win 7 points before partner (at baseline) wins 11.")
            metric_label = "Did you win? (1=Win, 0=Loss)"

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            metric = st.number_input(metric_label, min_value=0.0)
        with c2:
            notes = st.text_input("Lab Notes", placeholder="e.g., Backhand reset felt stiff")

        if st.button("💾 Save Data"):
            c.execute("INSERT INTO drill_stats (date, drill_name, metric_value, notes) VALUES (?, ?, ?, ?)", 
                      (date.today(), drill_type, metric, notes))
            conn.commit()
            st.success("Entry logged!")

    st.divider()
    st.subheader("📊 Research Findings")
    df = pd.read_sql_query("SELECT * FROM drill_stats", conn)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        chart_drill = st.selectbox("Select Drill to Visualize", df['drill_name'].unique())
        drill_data = df[df['drill_name'] == chart_drill]
        st.line_chart(drill_data, x='date', y='metric_value')

# --- TAB 2: THE SCOUT (Updated!) ---
with tab2:
    st.header("🔭 Tournament Scout")
    st.write(f"Scanning target sector: **22030 (Local)**")
    
    # The "User Preferred" Link
    TARGET_URL = "https://pickleballtournaments.com/search?show_all=true&zoom_level=7&current_page=1&tournament_filter=local"

    if st.button("🚀 Launch Scout Robot"):
        # UPDATED TEXT LABEL
        with st.spinner("Initializing satellite link... (Accessing PickleballTournaments.com)"):
            try:
                results = scout.run_scout()
                
                if results:
                    st.success(f"Mission Success: {len(results)} Tournaments Detected")
                    for t in results:
                        st.markdown(f"### {t['name']}")
                        st.caption(f"🗓️ {t['date']} | 📍 {t['location']}")
                        st.markdown(f"[➡️ **Register Here**]({t['link']})")
                        st.divider()
                else:
                    # THE FAIL-SAFE: If robot returns 0 results, show the manual link
                    st.warning("⚠️ Stealth Mode Active: The robot was blocked by the website's firewall.")
                    st.info("Don't worry! I have generated a Direct Uplink to the live results:")
                    st.link_button("🔗 Open Live Tournament Results (Virginia/Local)", TARGET_URL)
                    
            except Exception as e:
                st.error(f"Mission Failed: {e}")
                st.link_button("🔗 Open Live Results Manually", TARGET_URL)