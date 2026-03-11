import streamlit as st
from sqlalchemy import text
from database import SessionLocal, User, AuditLog

def clean_data(data_dict):
    return {k: (str(v) if v is not None and str(v).lower() != 'none' else "-") for k, v in data_dict.items()}

def display_info(label, value):
    """تابع کمکی برای نمایش اطلاعات بدون محدودیت فضا"""
    st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <p style="color: #808495; font-size: 0.85rem; margin-bottom: 2px;">{label}</p>
            <p style="color: white; font-size: 1.1rem; font-weight: 500; margin-top: 0; line-height: 1.2;">{value}</p>
        </div>
    """, unsafe_allow_html=True)

def show_search_page():
    st.markdown('<h2 style="text-align: center;">Shipment Tracking</h2>', unsafe_allow_html=True)
    
    # نمایش نام ستون‌ها برای اطمینان از صحت نام‌ها
    # if st.checkbox("Show Database Schema"):
    #     with SessionLocal() as db:
    #         res = db.execute(text("SELECT * FROM shipments LIMIT 0"))
    #         st.write(res.keys())
    
    with st.container(border=True):
        with st.form("search_form"):
            col1, col2, col3 = st.columns(3)
            cntr_no = col1.text_input("Cntr No *", key="c_input", autocomplete="off").strip().upper()
            hbl_no = col2.text_input("HBL NO **", key="h_input", autocomplete="off").strip().upper()
            job_no = col3.text_input("Job NO **", key="j_input", autocomplete="off").strip().upper()
            st.markdown('<div style="color: #808495; font-size: 0.8rem; margin-top: -15px;">* Mandatory | ** At least one required</div>', unsafe_allow_html=True)
            submit = st.form_submit_button("Track Shipment", use_container_width=True, type="primary")

        if submit:
            if not cntr_no:
                st.error("Cntr No is mandatory.")
                return
            if not (hbl_no or job_no):
                st.error("You must provide either an HBL NO or a Job NO.")
                return

            with SessionLocal() as db:
                # استفاده از TRIM و UPPER برای دقت ۱۰۰ درصد در جستجو و جلوگیری از تداخل
                query_str = "SELECT * FROM shipments WHERE UPPER(TRIM(cntr_no)) = :c_no"
                params = {"c_no": cntr_no}

                if hbl_no:
                    query_str += " AND UPPER(TRIM(hbl_no)) = :h_no"
                    params["h_no"] = hbl_no
                
                if job_no:
                    query_str += " AND UPPER(TRIM(job_no)) = :j_no"
                    params["j_no"] = job_no

                # اجرای کوئری (خارج از شرط‌های بالا)
                result = db.execute(text(query_str), params).fetchone()

                if result:
                    res = clean_data(result._asdict())
                    
                    # ثبت لاگ
                    user_obj = db.query(User).filter(User.username == st.session_state.get('username')).first()
                    if user_obj:
                        db.add(AuditLog(user_id=user_obj.id, action="SEARCH", target_value=cntr_no))
                        db.commit()

                    st.success(f"Results for Container: {cntr_no}")
                    st.divider()

                    # --- نمایش اطلاعات اصلی با چیدمان بازتر ---
                    st.subheader("📦 Shipment Overview")
                    
                    # استفاده از ۲ ستون به جای ۳ ستون برای فضای بیشتر
                    m_col1, m_col2 = st.columns(2)
                    
                    with m_col1:
                        display_info("Shipment Status", res.get('shipment_status'))
                        display_info("Sailing Date", res.get('sailing_date1'))
                        display_info("PoL", res.get('port_of_loading'))
                        display_info("Shipper", res.get('hbl_shipper'))
                        display_info("VSL/VOY", res.get('vessel_voyage'))

                    with m_col2:
                        display_info("BL Date", res.get('bl_date'))
                        display_info("PoD", res.get('port_of_discharge'))
                        display_info("Pre Carriage", res.get('precarriage1'))
                        display_info("HBL CNEE", res.get('hbl_consignee'))
                        # می‌توانید فیلد دیگری اینجا اضافه کنید

                    st.divider()

                    # --- View Full Details ---
                    with st.expander("View Full Details"):
                        cols = st.columns(2)
                        # نمایش به صورت کلید و مقدار متنی ساده
                        for i, (key, value) in enumerate(res.items()):
                            col_idx = i % 2
                            label = key.replace('_', ' ').upper()
                            cols[col_idx].write(f"**{label}**: {value}")
                else:
                    st.error("No shipment found.")