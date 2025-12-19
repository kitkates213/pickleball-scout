import streamlit as st
import sqlite3
import pandas as pd
import time
from datetime import datetime, date

# --- CONFIGURATION ---
st.set_page_config(page_title="Dink Lab", page_icon="🧪", layout="wide")

# --- DATABASE SETUP ---
conn = sqlite3.connect('pickleball_data.db', check_same_thread=False)
c = conn.cursor()

# 1. Drill Data (Added 'duration' column)
# We use a trick to add the column if it doesn't exist yet
try:
    c.execute("ALTER TABLE drill_stats ADD COLUMN duration INTEGER")
except:
    pass # Column already exists

c.execute('''CREATE TABLE IF NOT EXISTS drill_stats
             (id INTEGER PRIMARY KEY, date TEXT, drill_name TEXT, 
              metric_value REAL, notes TEXT, duration INTEGER)''')

# 2. Tournament Schedule
c.execute('''CREATE TABLE IF NOT EXISTS my_schedule
             (id INTEGER PRIMARY KEY, name TEXT, start_date TEXT, 
              status TEXT, link TEXT)''')
conn.commit()

# --- SIDEBAR: PLAYER PROFILE ---
with st.sidebar:
    st.title("🧪 Dink Lab")
    st.caption("Assistant: Active")
    st.divider()
    
    # Quick Profile Stats
    df_sched = pd.read_sql_query("SELECT * FROM my_schedule WHERE status='Registered'", conn)
    upcoming_count = len(df_sched)
    st.metric("🏆 Registered Events", upcoming_count)
    
    st.info(f"**Current Level:** 3.5 - 4.0\n\n**Location:** 22030")

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["🔬 The Lab (Drills)", "📅 My Manager", "🔭 The Scout"])

# =========================================================
# TAB 1: THE LAB (Now with Timer!)
# =========================================================
with tab1:
    st.header("Daily Experiments (Drills)")
    
    # --- NEW: SESSION TIMER ---
    with st.expander("⏱️ Drill Timer", expanded=False):
        t_col1, t_col2 = st.columns([1,3])
        with t_col1:
            timer_minutes = st.number_input("Set Timer (min)", min_value=1, value=20)
        with t_col2:
            st.write(" ") # Spacer
            st.write(" ") 
            if st.button("▶️ Start Timer"):
                progress_text = "Drilling in progress... Focus!"
                my_bar = st.progress(0, text=progress_text)
                
                total_seconds = timer_minutes * 60
                
                for i in range(total_seconds):
                    # Update bar every second
                    percent_complete = (i + 1) / total_seconds
                    time_left = total_seconds - (i + 1)
                    mins_left = time_left // 60
                    secs_left = time_left % 60
                    
                    my_bar.progress(percent_complete, text=f"⏳ Time Remaining: {mins_left}:{secs_left:02d}")
                    time.sleep(1)
                
                my_bar.empty()
                st.success("🔔 TIME'S UP! Good work.")
                st.balloons()

    st.divider()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        drill_type = st.radio(
            "Select Experiment", 
            ["Dink Loyalty", "Transition Reset", "Drops vs Drives", "7-11 Singles"]
        )

    with col2:
        # --- DRILL INSTRUCTIONS ---
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
        c1, c2, c3 = st.columns(3)
        with c1:
            metric = st.number_input(metric_label, min_value=0.0)
        with c2:
            duration = st.number_input("Duration (Mins)", min_value=5, step=5, value=20)
        with c3:
            notes = st.text_input("Lab Notes", placeholder="e.g. Backhand reset felt stiff")

        if st.button("💾 Save Data to Lab Journal"):
            c.execute("INSERT INTO drill_stats (date, drill_name, metric_value, notes, duration) VALUES (?, ?, ?, ?, ?)", 
                      (date.today(), drill_type, metric, notes, duration))
            conn.commit()
            st.success("Entry logged!")

    # --- PROGRESS CHART ---
    st.divider()
    st.subheader("📊 Research Findings")
    df = pd.read_sql_query("SELECT * FROM drill_stats", conn)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter Logic
        chart_drill = st.selectbox("Select Drill to Visualize", df['drill_name'].unique())
        drill_data = df[df['drill_name'] == chart_drill]
        
        st.line_chart(drill_data, x='date', y='metric_value')
        
        # Show total time spent
        total_mins = drill_data['duration'].sum()
        st.caption(f"Total time spent on {chart_drill}: {total_mins} minutes")

# =========================================================
# TAB 2: MY MANAGER (The Assistant)
# =========================================================
with tab2:
    st.header("📅 Tournament Manager")
    
    # 1. ADD NEW EVENT (With Conflict Checker!)
    with st.expander("➕ Add Tournament to Schedule", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Tournament Name")
            new_date = st.date_input("Date")
        with c2:
            new_status = st.selectbox("Status", ["Interested (Wishlist)", "Registered", "Completed"])
            new_link = st.text_input("Link (Optional)")
            
        if st.button("Add to Schedule"):
            # CONFLICT CHECKER
            existing = pd.read_sql_query("SELECT * FROM my_schedule WHERE start_date=?", conn, params=(new_date,))
            
            if not existing.empty:
                conflict_name = existing.iloc[0]['name']
                st.warning(f"⚠️ **Conflict Detected!** You already have '{conflict_name}' scheduled for {new_date}.")
                if st.button("Add Anyway (Ignore Conflict)"):
                    c.execute("INSERT INTO my_schedule (name, start_date, status, link) VALUES (?, ?, ?, ?)", 
                              (new_name, new_date, new_status, new_link))
                    conn.commit()
                    st.success(f"Added '{new_name}'!")
                    st.rerun()
            else:
                c.execute("INSERT INTO my_schedule (name, start_date, status, link) VALUES (?, ?, ?, ?)", 
                          (new_name, new_date, new_status, new_link))
                conn.commit()
                st.success(f"Added '{new_name}' to your {new_status} list.")
                st.rerun()

    # 2. VIEW SCHEDULE
    st.divider()
    st.subheader("My Calendar")
    
    df_all = pd.read_sql_query("SELECT * FROM my_schedule ORDER BY start_date", conn)
    
    if not df_all.empty:
        df_all['start_date'] = pd.to_datetime(df_all['start_date']).dt.date
        today = date.today()
        
        # Split into Lists
        upcoming = df_all[df_all['start_date'] >= today]
        past = df_all[df_all['start_date'] < today]
        
        # Display logic
        st.write("### 🚀 Upcoming & Wishlist")
        if upcoming.empty:
            st.info("No upcoming events found.")
            
        for index, row in upcoming.iterrows():
            # Color coding
            if row['status'] == "Registered":
                status_icon = "🟢 REGISTERED"
                border_color = "green" # visual cue logic
            else:
                status_icon = "🟡 WISHLIST"
                border_color = "yellow"

            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"🗓️ {row['start_date']} | {status_icon}")
                with col_b:
                    if row['link']:
                        st.markdown(f"[View Link]({row['link']})")
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        c.execute("DELETE FROM my_schedule WHERE id=?", (row['id'],))
                        conn.commit()
                        st.rerun()

        if not past.empty:
            with st.expander("📜 Past Events"):
                st.dataframe(past[['name', 'start_date', 'status']])
    else:
        st.info("Your schedule is empty. Add a tournament above!")

# =========================================================
# TAB 3: THE SCOUT
# =========================================================
with tab3:
    st.header("🔭 The Scout")
    st.markdown("""
    **Status:** Robot functionality limited by cloud firewalls.
    **Protocol:** Use the Direct Uplink below to find events, then **add them to the 'My Manager' tab** to track them.
    """)
    
    TARGET_URL = "https://pickleballtournaments.com/search?show_all=true&zoom_level=7&current_page=1&tournament_filter=local"
    st.link_button("🔗 Open Live Results (Virginia/Local)", TARGET_URL)