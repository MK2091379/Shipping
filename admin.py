import streamlit as st
import pandas as pd
from database import SessionLocal, User, AuditLog

def show_admin_page():
    st.markdown('<h2 style="text-align: center;">Admin Dashboard</h2>', unsafe_allow_html=True)
    tab_u, tab_l = st.tabs(["Users", "Audit Logs"])
    db = SessionLocal()
    
    with tab_u:
        users = db.query(User).all()
        st.table([{"ID": u.id, "User": u.username, "Role": u.role} for u in users])
        
    with tab_l:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50).all()
        st.dataframe([{"User": l.user_id, "Action": l.action, "Target": l.target_value, "Time": l.timestamp} for l in logs])
    db.close()