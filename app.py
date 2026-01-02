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

# 1. Drill Data (Added 'player' column for separation)
try:
    c.execute("ALTER TABLE drill_stats ADD COLUMN player TEXT")
except:
    pass 
c.execute('''CREATE TABLE IF NOT EXISTS drill_stats
             (id INTEGER PRIMARY KEY, date TEXT, drill_name TEXT, 
              metric_value REAL, notes TEXT, duration INTEGER, player TEXT)''')

# 2. Tournament Schedule (Added 'player' column)
try:
    c.execute("ALTER TABLE my_schedule ADD COLUMN player TEXT")
except:
    pass
c.execute('''CREATE TABLE IF NOT EXISTS my_schedule
             (id INTEGER PRIMARY KEY, name TEXT, start_date TEXT, 
              status TEXT, link TEXT, player TEXT)''')
conn.commit()

# --- SIDEBAR: PLAYER PROFILE ---
with st.sidebar:
    st.title("🧪 Dink Lab")
    
    # --- NEW: PLAYER SELECTOR ---
    # This separates your data from Brad's!
    current_user = st.selectbox("Who is training?", ["Kit", "Brad", "Guest"])
    
    st.divider()
    
    # Quick Profile Stats (Filtered by User)
    df_sched = pd.read_sql_query("SELECT * FROM my_schedule WHERE status='Registered' AND player=?", conn, params=(current_user,))
    upcoming_count = len(df_sched)
    st.metric(f"{current_user}'s Events", upcoming_count)
    
    # --- DATA BACKUP (CRITICAL) ---
    st.divider()
    st.caption("💾 Data Management")
    st.info("⚠️ Updates wipe data! Download backup before updating code.")
    
    # Export Drills
    df_drills = pd.read_sql_query("SELECT * FROM drill_stats", conn)
    csv_drills = df_drills.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Drill Data", csv_drills, "drills_backup.csv", "text/csv")

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["🔬 The Lab (Drills)", "📅 My Manager", "🔭 The Scout"])

# =========================================================
# TAB 1: THE LAB (New Metrics)
# =========================================================
with tab1:
    st.header(f"Daily Experiments: {current_user}")
    
    # --- DRILL TIMER ---
    with st.expander("⏱️ Drill Timer", expanded=False):
        t_col1, t_col2 = st.columns([1,3])
        with t_col1:
            timer_minutes = st.number_input("Set Timer (min)", min_value=1, value=20)
        with t_col2:
            st.write(" ") 
            st.write(" ") 
            b1, b2 = st.columns([1,1])
            with b1:
                start_timer = st.button("▶️ Start", type="primary")
            with b2:
                stop_timer = st.button("⏹️ Stop")
            
            if start_timer:
                progress_text = "Drilling in progress... Focus!"
                my_bar = st.progress(0, text=progress_text)
                total_seconds = timer_minutes * 60
                for i in range(total_seconds):
                    percent_complete = (i + 1) / total_seconds
                    time_left = total_seconds - (i + 1)
                    mins_left = time_left // 60
                    secs_left = time_left % 60
                    my_bar.progress(percent_complete, text=f"⏳ Time Remaining: {mins_left}:{secs_left:02d}")
                    time.sleep(1)
                my_bar.empty()
                st.success("🔔 TIME'S UP!")
                st.balloons()
            
            if stop_timer:
                st.info("Timer Stopped.")

    st.divider()

    col1, col2 = st.columns([1, 2])
    
    with col1:
        drill_type = st.radio(
            "Select Experiment", 
            ["Dink Loyalty", "Transition Reset", "Drops vs Drives", "7-11 Singles"]
        )

    with col2:
        # --- NEW COOPERATIVE METRICS ---
        if drill_type == "Dink Loyalty":
            st.subheader("🛡️ Dink Loyalty")
            st.markdown("""
            **Goal:** Reduce errors. A "Perfect Game" is 0 errors.
            **Protocol:** Cross-court dinking only. No speed-ups.
            **Metric:** How many Unforced Errors did YOU make in this game?
            """)
            metric_label = "My Unforced Errors (Aim for 0)"

        elif drill_type == "Transition Reset":
            st.subheader("🧱 Transition Reset")
            st.markdown("""
            **Goal:** Reset hard drives into the kitchen.
            **Metric:** How many successful resets out of 10 feeds?
            """)
            metric_label = "Successful Resets (out of 10)"

        elif drill_type == "Drops vs Drives":
            st.subheader("🧠 Drops vs Drives")
            st.markdown("""
            **Goal:** Decision quality.
            **Metric:** +1 point for correct choice (Drop vs Drive) AND execution.
            """)
            metric_label = "Score (Max 20)"

        elif drill_type == "7-11 Singles":
            st.subheader("🏃 7-11 Singles")
            st.markdown("""
            **Goal:** Score points, regardless of winning.
            **Metric:** How many points did YOU score? (If at net, aim for 7. If back, aim for 11).
            """)
            metric_label = "Points Scored"

        # --- LOGGING FORM ---
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            metric = st.number_input(metric_label, min_value=0.0)
        with c2:
            duration = st.number_input("Duration (Mins)", min_value=5, step=5, value=20)
        with c3:
            notes = st.text_input("Lab Notes", placeholder="e.g. Felt rushed")

        if st.button("💾 Save Data"):
            # Saves with the Current User Name!
            c.execute("INSERT INTO drill_stats (date, drill_name, metric_value, notes, duration, player) VALUES (?, ?, ?, ?, ?, ?)", 
                      (date.today(), drill_type, metric, notes, duration, current_user))
            conn.commit()
            st.success(f"Entry logged for {current_user}!")

    # --- PROGRESS CHART (User Specific) ---
    st.divider()
    st.subheader(f"📊 {current_user}'s Progress")
    
    # Filter by CURRENT USER
    df = pd.read_sql_query("SELECT * FROM drill_stats WHERE player=?", conn, params=(current_user,))
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        chart_drill = st.selectbox("Select Drill to Visualize", df['drill_name'].unique())
        drill_data = df[df['drill_name'] == chart_drill]
        st.line_chart(drill_data, x='date', y='metric_value')
        
        # Show total time
        total_mins = drill_data['duration'].sum()
        st.caption(f"Total time spent on {chart_drill}: {total_mins} minutes")
    else:
        st.info(f"No data yet for {current_user}.")

# =========================================================
# TAB 2: MY MANAGER
# =========================================================
with tab2:
    st.header(f"📅 Tournament Manager: {current_user}")
    
    with st.expander("➕ Add Tournament", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Tournament Name")
            new_date = st.date_input("Date")
        with c2:
            new_status = st.selectbox("Status", ["Interested (Wishlist)", "Registered", "Completed"])
            new_link = st.text_input("Link (Optional)")
            
        if st.button("Add to Schedule"):
            check_date = str(new_date)
            # Check conflicts ONLY for current user
            existing = pd.read_sql_query("SELECT * FROM my_schedule WHERE start_date=? AND player=?", conn, params=(check_date, current_user))
            
            if not existing.empty:
                conflict_name = existing.iloc[0]['name']
                st.warning(f"⚠️ Conflict: You ({current_user}) already have '{conflict_name}' on this day.")
                if st.button("Add Anyway"):
                    c.execute("INSERT INTO my_schedule (name, start_date, status, link, player) VALUES (?, ?, ?, ?, ?)", 
                              (new_name, new_date, new_status, new_link, current_user))
                    conn.commit()
                    st.success(f"Added '{new_name}'!")
                    st.rerun()
            else:
                c.execute("INSERT INTO my_schedule (name, start_date, status, link, player) VALUES (?, ?, ?, ?, ?)", 
                          (new_name, new_date, new_status, new_link, current_user))
                conn.commit()
                st.success("Added!")
                st.rerun()

    st.divider()
    st.subheader("My Calendar")
    
    # Fetch Data for CURRENT USER
    df_all = pd.read_sql_query("SELECT * FROM my_schedule WHERE player=? ORDER BY start_date", conn, params=(current_user,))
    
    if not df_all.empty:
        df_all['start_date'] = pd.to_datetime(df_all['start_date']).dt.date
        today = date.today()
        upcoming = df_all[df_all['start_date'] >= today]
        past = df_all[df_all['start_date'] < today]
        
        st.write("### 🚀 Upcoming & Wishlist")
        for index, row in upcoming.iterrows():
            if row['status'] == "Registered":
                status_icon = "🟢 REGISTERED"
            else:
                status_icon = "🟡 WISHLIST"

            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"🗓️ {row['start_date']} | {status_icon}")
                with col_b:
                    if row['link']:
                        st.markdown(f"[Link]({row['link']})")
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        c.execute("DELETE FROM my_schedule WHERE id=?", (row['id'],))
                        conn.commit()
                        st.rerun()

        if not past.empty:
            with st.expander("📜 Past Events"):
                st.dataframe(past[['name', 'start_date', 'status']])
    else:
        st.info(f"No events found for {current_user}.")

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