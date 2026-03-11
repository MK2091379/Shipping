import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import SessionLocal, User, AuditLog, verify_password, hash_password
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Tav Freight - Shipments Management", 
    page_icon="🚢",
    layout="centered",
)

# 2. Custom CSS for UI
st.markdown("""
    <style>
    .brand-text {
        font-size: 50px;
        font-family: 'Brush Script MT', cursive;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    .stButton > button {
        width: 100%;
        border-radius: 5px;
    }
    /* Centering headings for internal pages */
    .centered-header {
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- HEADER SECTION ---
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.image("ship_logo.png", use_container_width=True)
    
    st.markdown('<div class="brand-text">Tav Freight</div>', unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.session_state['username'] = None

    if not st.session_state['logged_in']:
        # --- AUTH SECTION ---
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            tab_login, tab_signup = st.tabs(["Sign In", "Sign Up"])
            with tab_login:
                with st.form("login_form"):
                    username = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
                    password = st.text_input("Password", type='password', placeholder="Password", label_visibility="collapsed")
                    submit_login = st.form_submit_button("Enter")
                    if submit_login:
                        if username and password:
                            db = SessionLocal()
                            user = db.query(User).filter(User.username == username).first()
                            if user and verify_password(password, user.password_hash):
                                st.session_state['logged_in'] = True
                                st.session_state['username'] = user.username
                                st.session_state['role'] = user.role
                                st.rerun()
                            else:
                                st.error("Invalid username or password")
                            db.close()
            with tab_signup:
                with st.form("signup_form"):
                    new_user = st.text_input("New Username", placeholder="New Username", label_visibility="collapsed")
                    new_pass = st.text_input("New Password", type='password', placeholder="New Password", label_visibility="collapsed")
                    submit_signup = st.form_submit_button("Create Account")
                    if submit_signup:
                        db = SessionLocal()
                        if db.query(User).filter(User.username == new_user).first():
                            st.error("Username already taken")
                        else:
                            user = User(username=new_user, password_hash=hash_password(new_pass), role="user")
                            db.add(user)
                            db.commit()
                            st.success("Account created! Please Sign In.")
                        db.close()
    else:
        # --- LOGGED IN AREA ---
        st.sidebar.markdown(f"### User: **{st.session_state['username']}**")
        st.sidebar.markdown(f"Role: `{st.session_state['role']}`")
        if st.sidebar.button("Log Out"):
            st.session_state['logged_in'] = False
            st.rerun()

        if st.session_state['role'] == "admin":
            admin_panel()
        else:
            search_panel()

def search_panel():
    st.markdown('<h2 class="centered-header">Container Search</h2>', unsafe_allow_html=True)
    
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            container_no = st.text_input("Container No *").strip()
        with col2:
            bl_no = st.text_input("BL Number (Optional)").strip()
        
        submit_search = st.form_submit_button("Track Shipment")

    if submit_search:
        if not container_no:
            st.warning("Please enter at least a Container Number.")
        else:
            db = SessionLocal()
            try:
                query = "SELECT * FROM shipments WHERE cntr_no = :c_no"
                params = {"c_no": container_no}
                if bl_no:
                    query += " AND (mbl_no = :bl OR hbl_no = :bl)"
                    params["bl"] = bl_no

                result = db.execute(text(query), params).fetchone()

                if result:
                    res_dict = result._asdict()
                    
                    # LOGGING SEARCH ACTION
                    user_obj = db.query(User).filter(User.username == st.session_state['username']).first()
                    new_log = AuditLog(user_id=user_obj.id, action="SEARCH_SUCCESS", target_value=container_no)
                    db.add(new_log)
                    db.commit()

                    st.success("Shipment Found")
                    
                    # Layout Results
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Status", res_dict.get('shipment_status', 'N/A'))
                    m2.metric("Sailing Date", str(res_dict.get('sailing_date1', 'N/A')))
                    m3.metric("Vessel", res_dict.get('vessel_voyage', 'N/A'))

                    st.markdown("---")
                    d1, d2 = st.columns(2)
                    with d1:
                        st.write(f"**Port of Loading:** {res_dict.get('port_of_loading', 'N/A')}")
                        st.write(f"**Port of Discharge:** {res_dict.get('port_of_discharge', 'N/A')}")
                    with d2:
                        st.write(f"**Consignee (HBL):**")
                        st.info(res_dict.get('hbl_consignee', 'No Data'))
                else:
                    st.error("No shipment found with these details.")
            finally:
                db.close()

def admin_panel():
    st.markdown('<h2 class="centered-header">Admin Dashboard</h2>', unsafe_allow_html=True)
    
    tab_users, tab_logs = st.tabs(["User Management", "Audit Logs"])
    
    db = SessionLocal()
    with tab_users:
        users = db.query(User).all()
        user_list = [{"ID": u.id, "Username": u.username, "Role": u.role, "Created": u.created_at} for u in users]
        st.table(pd.DataFrame(user_list))

    with tab_logs:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
        log_list = [{"User ID": l.user_id, "Action": l.action, "Target": l.target_value, "Time": l.timestamp} for l in logs]
        st.dataframe(pd.DataFrame(log_list), use_container_width=True)
    db.close()

if __name__ == '__main__':
    main()