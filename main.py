import streamlit as st
from auth import show_auth_page
from search import show_search_page
from admin import show_admin_page

# ۱. Setup (حتما باید اولین دستور باشد)
st.set_page_config(page_title="Tav Freight", page_icon="🚢", layout="centered")

# ۲. Global Styles & Branding
st.markdown("""
    <style>
    .brand-text { 
        font-size: 50px; 
        font-family: 'Brush Script MT', cursive; 
        text-align: center; 
        margin-top: -20px; 
        margin-bottom: 10px; 
    }
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    /* حذف حاشیه اضافی بالای لوگو */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ۳. Branding Logic (لوگو و متن برند)
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    st.image("ship_logo.png", use_container_width=True)
st.markdown('<div class="brand-text">Tav Freight</div>', unsafe_allow_html=True)

# ۴. Session State Init
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'role' not in st.session_state:
    st.session_state['role'] = "user"

# ۵. Routing Logic
if not st.session_state['logged_in']:
    show_auth_page()
else:
    # Sidebar Navigation
    st.sidebar.title(f"👤 Welcome, {st.session_state['username']}")
    
    page_options = ["Shipment Tracking"]
    if st.session_state['role'] == "admin":
        page_options.append("Admin Dashboard")
    
    choice = st.sidebar.radio("Navigation", page_options)
    
    st.sidebar.divider()
    if st.sidebar.button("Log Out", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

    # Page Rendering
    if choice == "Shipment Tracking":
        show_search_page()
    elif choice == "Admin Dashboard":
        show_admin_page()