import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

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

with tab1:
    st.header("Daily Experiments")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        drill_type = st.radio(
            "Select Experiment", 
            ["Dink Loyalty", "Transition Reset", "Drops vs Drives", "7-11 Singles"]
        )

    with col2:
        # --- DRILL INSTRUCTIONS ENGINE ---
        if drill_type == "Dink Loyalty":
            st.subheader("🛡️ Dink Loyalty")
            st.markdown("""
            **The Goal:** Consistency under pressure. Win the "patience war."
            
            **⚗️ Setup:**
            * **You:** Kitchen Line (Left or Right)
            * **Partner:** Kitchen Line (Cross-court from you)
            * *Zone:* Use only half the kitchen (cross-court slice).
            
            **🧪 Protocol:**
            1.  Start a dink rally cross-court.
            2.  **RULE:** You are NOT allowed to speed up the ball.
            3.  If you hit high/hard, you lose the point.
            4.  You only win if *they* hit the net or out.
            
            **📈 Metric:** Game to 10. Did you win? (1=Yes, 0=No)
            """)
            metric_label = "Did you win? (1=Win, 0=Loss)"

        elif drill_type == "Transition Reset":
            st.subheader("🧱 Transition Reset")
            st.markdown("""
            **The Goal:** Survive the "Kill Zone" and neutralize aggressive shots.
            
            **⚗️ Setup:**
            * **You:** Start at Baseline.
            * **Partner:** Kitchen Line (with a bucket of balls).
            
            **🧪 Protocol:**
            1.  Partner feeds hard, fast drives at your feet/body.
            2.  You must hit a soft **Reset** (drop into their kitchen).
            3.  After every successful reset, take one step forward.
            4.  If you pop it up or miss, stay or step back.
            5.  Goal is to make it all the way to the kitchen line.
            
            **📈 Metric:** Success Rate (e.g., "7" means you reset 7 out of 10 balls successfully).
            """)
            metric_label = "Successful Resets (out of 10)"

        elif drill_type == "Drops vs Drives":
            st.subheader("🧠 Drops vs Drives (Decision Matrix)")
            st.markdown("""
            **The Goal:** Instant decision making based on ball depth.
            
            **⚗️ Setup:**
            * **You:** Baseline.
            * **Partner:** Kitchen Line.
            
            **🧪 Protocol:**
            1.  Partner hits balls to you (mix of deep and short).
            2.  **Deep Ball?** Hit a DROP (soft arc).
            3.  **Short Ball?** Hit a DRIVE (flat/fast).
            4.  **Scoring:** * +1 point for a correct decision AND execution.
                * 0 points if you drive a deep ball or drop a short ball.
            
            **📈 Metric:** Total Score out of 20 reps.
            """)
            metric_label = "Score (Max 20)"

        elif drill_type == "7-11 Singles":
            st.subheader("🏃 7-11 Singles")
            st.markdown("""
            **The Goal:** Practice closing out points at the net vs. passing shots.
            
            **⚗️ Setup:**
            * **You:** Kitchen Line (The "7").
            * **Partner:** Baseline (The "11").
            
            **🧪 Protocol:**
            1.  Play out the point using full singles court (or skinny singles).
            2.  You (at net) need to win **7 points** before your partner (at baseline) wins **11 points**.
            
            **📈 Metric:** Did you win? (1=Yes, 0=No)
            """)
            metric_label = "Did you win? (1=Win, 0=Loss)"

        # --- LOGGING FORM ---
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            metric = st.number_input(metric_label, min_value=0.0)
        with c2:
            notes = st.text_input("Lab Notes", placeholder="e.g., Backhand reset felt stiff")

        if st.button("💾 Save Data to Lab Journal"):
            c.execute("INSERT INTO drill_stats (date, drill_name, metric_value, notes) VALUES (?, ?, ?, ?)", 
                      (date.today(), drill_type, metric, notes))
            conn.commit()
            st.success("Entry logged!")

    # --- PROGRESS CHART ---
    st.divider()
    st.subheader("📊 Research Findings")
    df = pd.read_sql_query("SELECT * FROM drill_stats", conn)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Simple filter for the chart
        chart_drill = st.selectbox("Select Drill to Visualize", df['drill_name'].unique())
        drill_data = df[df['drill_name'] == chart_drill]
        
        st.line_chart(drill_data, x='date', y='metric_value')
        
        with st.expander("View Raw Data"):
            st.dataframe(drill_data.sort_values(by='date', ascending=False))

# --- TAB 2: THE SCOUT ---
with tab2:
    st.header("🔭 Tournament Scout")
    st.write(f"Scanning target sector: **22030 (50 mile radius)**")
    
    if st.button("🚀 Launch Scout Robot"):
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
                    st.warning("No tournaments found. The robot visited the site but couldn't extract data. Check the layout.")
            except Exception as e:
                st.error(f"Mission Failed: {e}")