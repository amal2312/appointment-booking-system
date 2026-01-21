import streamlit as st
import pandas as pd
from db.database import get_all_bookings
from datetime import datetime


def admin_dashboard_page():
    """Admin Dashboard with Quick Stats & Search"""
    
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.5rem;'>📊 Admin Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
    
    bookings = get_all_bookings()

    if not bookings:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
        border: 1px solid rgba(102, 126, 234, 0.3); border-radius: 16px; backdrop-filter: blur(10px);'>
            <h2 style='color: #e0e7ff;'>📭 No Bookings Yet</h2>
            <p style='color: #c7d2fe;'>Appointments will appear here once they're made</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Convert to DataFrame with proper column names
    df = pd.DataFrame(bookings, columns=['id', 'name', 'email', 'phone', 'date', 'time', 'status', 'created_at'])
    
    # ========== QUICK STATS SECTION ==========
    st.markdown("<h3 style='color: #e0e7ff; margin: 2rem 0 1rem 0;'>📈 Quick Stats</h3>", unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("📅 Total Bookings", len(df))
    
    with metric_col2:
        try:
            upcoming = len(df[pd.to_datetime(df['date']) >= datetime.now().date()])
            st.metric("⏳ Upcoming", upcoming)
        except:
            st.metric("⏳ Upcoming", len(df))
    
    with metric_col3:
        st.metric("👥 Patients", df['name'].nunique())
    
    with metric_col4:
        st.metric("✉️ Contacts", df['email'].nunique())
    
    st.markdown("---")
    
    # ========== SEARCH SECTION ==========
    st.markdown("<h3 style='color: #e0e7ff;'>🔍 Search Bookings</h3>", unsafe_allow_html=True)
    
    search_col1, search_col2 = st.columns(2)
    
    with search_col1:
        search_name = st.text_input("🔎 Search by patient name:", key="search_name", placeholder="Enter name...")
    
    with search_col2:
        search_email = st.text_input("✉️ Search by email:", key="search_email", placeholder="Enter email...")
    
    filtered_df = df.copy()
    
    if search_name:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_name, case=False, na=False)]
    
    if search_email:
        filtered_df = filtered_df[filtered_df['email'].str.contains(search_email, case=False, na=False)]
    
    if len(filtered_df) > 0:
        st.markdown(f"<p style='color: #38ef7d; font-weight: 600;'>✅ Found {len(filtered_df)} booking(s)</p>", unsafe_allow_html=True)
        
        # Format dates for display
        display_df = filtered_df.copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(display_df, width='stretch')
    else:
        if search_name or search_email:
            st.warning("❌ No bookings match your search criteria")
        else:
            st.info("💡 Enter a name or email to search")
    
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: #8892b0; font-size: 0.85rem;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        unsafe_allow_html=True
    )
