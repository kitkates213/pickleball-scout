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

# 1. Drill Data
try:
    c.execute("ALTER TABLE drill_stats ADD COLUMN player TEXT")
except:
    pass 
try:
    c.execute("ALTER TABLE drill_stats ADD COLUMN duration INTEGER")
except:
    pass

c.execute('''CREATE TABLE IF NOT EXISTS drill_stats
             (id INTEGER PRIMARY KEY, date TEXT, drill_name TEXT, 
              metric_value REAL, notes TEXT, duration INTEGER, player TEXT)''')

# 2. Tournament Schedule
try:
    c.execute("ALTER TABLE my_schedule ADD COLUMN player TEXT")
except:
    pass
c.execute('''CREATE TABLE IF NOT EXISTS my_schedule
             (id INTEGER PRIMARY KEY, name TEXT, start_date TEXT, 
              status TEXT, link TEXT, player TEXT)''')
conn.commit()

# --- SIDEBAR: PLAYER PROFILE & BACKUPS ---
with st.sidebar:
    st.title("🧪 Dink Lab")
    
    # Player Selector
    current_user = st.selectbox("Who is training?", ["Kit", "Brad", "Guest"])
    
    st.divider()
    
    # Stats
    df_sched = pd.read_sql_query("SELECT * FROM my_schedule WHERE status='Registered' AND player=?", conn, params=(current_user,))
    upcoming_count = len(df_sched)
    st.metric(f"{current_user}'s Events", upcoming_count)
    
    # --- DATA BACKUP SECTION ---
    st.divider()
    st.caption("💾 Backup & Export")
    st.info("Download these before updating code!")
    
    # 1. Drills Backup
    df_drills = pd.read_sql_query("SELECT * FROM drill_stats", conn)
    csv_drills = df_drills.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Drill History", csv_drills, "drills_backup.csv", "text/csv")
    
    # 2. Schedule Backup
    df_all_sched = pd.read_sql_query("SELECT * FROM my_schedule", conn)
    csv_sched = df_all_sched.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Tournament Schedule", csv_sched, "schedule_backup.csv", "text/csv")

# --- MAIN TABS ---
# Added Tab 4 for Settings/Restore
tab1, tab2, tab3, tab4 = st.tabs(["🔬 The Lab", "📅 Manager", "🔭 Scout", "⚙️ Settings"])

# =========================================================
# TAB 1: THE LAB
# =========================================================
with tab1:
    st.header(f"Daily Experiments: {current_user}")
    
    # DRILL TIMER
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
        # METRICS
        if drill_type == "Dink Loyalty":
            st.subheader("🛡️ Dink Loyalty")
            st.markdown("**Goal:** Reduce errors. **Metric:** Unforced Errors (Aim for 0).")
            metric_label = "My Unforced Errors"

        elif drill_type == "Transition Reset":
            st.subheader("🧱 Transition Reset")
            st.markdown("**Goal:** Reset hard drives. **Metric:** Successful resets (out of 10).")
            metric_label = "Successful Resets"

        elif drill_type == "Drops vs Drives":
            st.subheader("🧠 Drops vs Drives")
            st.markdown("**Goal:** Decision quality. **Metric:** +1 for correct choice & execution.")
            metric_label = "Score (Max 20)"

        elif drill_type == "7-11 Singles":
            st.subheader("🏃 7-11 Singles")
            st.markdown("**Goal:** Score points. **Metric:** Points Scored (Aim for 7 or 11).")
            metric_label = "Points Scored"

        # LOGGING
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            metric = st.number_input(metric_label, min_value=0.0)
        with c2:
            duration = st.number_input("Duration (Mins)", min_value=5, step=5, value=20)
        with c3:
            notes = st.text_input("Lab Notes", placeholder="e.g. Felt rushed")

        if st.button("💾 Save Data"):
            c.execute("INSERT INTO drill_stats (date, drill_name, metric_value, notes, duration, player) VALUES (?, ?, ?, ?, ?, ?)", 
                      (date.today(), drill_type, metric, notes, duration, current_user))
            conn.commit()
            st.success(f"Entry logged for {current_user}!")

    # CHART
    st.divider()
    st.subheader(f"📊 {current_user}'s Progress")
    df = pd.read_sql_query("SELECT * FROM drill_stats WHERE player=?", conn, params=(current_user,))
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        chart_drill = st.selectbox("Select Drill to Visualize", df['drill_name'].unique())
        drill_data = df[df['drill_name'] == chart_drill]
        st.line_chart(drill_data, x='date', y='metric_value')
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
    df_all = pd.read_sql_query("SELECT * FROM my_schedule WHERE player=? ORDER BY start_date", conn, params=(current_user,))
    
    if not df_all.empty:
        df_all['start_date'] = pd.to_datetime(df_all['start_date']).dt.date
        today = date.today()
        upcoming = df_all[df_all['start_date'] >= today]
        past = df_all[df_all['start_date'] < today]
        
        st.write("### 🚀 Upcoming & Wishlist")
        for index, row in upcoming.iterrows():
            status_icon = "🟢 REGISTERED" if row['status'] == "Registered" else "🟡 WISHLIST"
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

# =========================================================
# TAB 4: SETTINGS (RESTORE DATA)
# =========================================================
with tab4:
    st.header("⚙️ Data Settings & Restore")
    st.write("Use this screen to reload your data after an app update.")
    
    st.divider()
    
    # --- RESTORE DRILLS ---
    st.subheader("1. Restore Drill History")
    uploaded_drills = st.file_uploader("Upload 'drills_backup.csv'", type="csv")
    
    if uploaded_drills is not None:
        if st.button("🔄 Process Drill Restore"):
            try:
                # Read CSV
                df_restore = pd.read_csv(uploaded_drills)
                
                # Clean: Drop the old 'id' column if it exists (let the new DB generate new IDs)
                if 'id' in df_restore.columns:
                    df_restore = df_restore.drop(columns=['id'])
                
                # Insert into DB
                df_restore.to_sql('drill_stats', conn, if_exists='append', index=False)
                st.success(f"Success! Restored {len(df_restore)} drill entries.")
                st.balloons()
            except Exception as e:
                st.error(f"Error restoring drills: {e}")

    st.divider()

    # --- RESTORE SCHEDULE ---
    st.subheader("2. Restore Tournament Schedule")
    uploaded_sched = st.file_uploader("Upload 'schedule_backup.csv'", type="csv")
    
    if uploaded_sched is not None:
        if st.button("🔄 Process Schedule Restore"):
            try:
                # Read CSV
                df_restore_sched = pd.read_csv(uploaded_sched)
                
                # Clean: Drop 'id' column
                if 'id' in df_restore_sched.columns:
                    df_restore_sched = df_restore_sched.drop(columns=['id'])
                
                # Insert into DB
                df_restore_sched.to_sql('my_schedule', conn, if_exists='append', index=False)
                st.success(f"Success! Restored {len(df_restore_sched)} tournament events.")
                st.balloons()
            except Exception as e:
                st.error(f"Error restoring schedule: {e}")
