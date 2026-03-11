import streamlit as st
from database import SessionLocal, User, verify_password, hash_password

def show_auth_page():
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        tab_login, tab_signup = st.tabs(["Sign In", "Sign Up"])
        
        with tab_login:
            # استفاده از کانتینر معمولی به جای st.form
            username = st.text_input("Username", placeholder="Username", label_visibility="collapsed", key="l_user")
            password = st.text_input("Password", type='password', placeholder="Password", label_visibility="collapsed", key="l_pass")
            
            # دکمه ورود معمولی
            if st.button("Enter", use_container_width=True, key="l_btn"):
                if username and password:
                    db = SessionLocal()
                    user = db.query(User).filter(User.username == username).first()
                    if user and verify_password(password, user.password_hash):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = user.username
                        st.session_state['role'] = user.role
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                    db.close()
                else:
                    st.warning("Please fill all fields")

        with tab_signup:
            new_user = st.text_input("New Username", placeholder="New Username", label_visibility="collapsed", key="s_user")
            new_pass = st.text_input("New Password", type='password', placeholder="New Password", label_visibility="collapsed", key="s_pass")
            
            if st.button("Create Account", use_container_width=True, key="s_btn"):
                if new_user and new_pass:
                    db = SessionLocal()
                    if db.query(User).filter(User.username == new_user).first():
                        st.error("Username taken")
                    else:
                        db.add(User(username=new_user, password_hash=hash_password(new_pass), role="user"))
                        db.commit()
                        st.success("Account created! Please Sign In.")
                    db.close()