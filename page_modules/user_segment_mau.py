import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Security utility import
try:
    from security_utils import SecurityUtils
except ImportError:
    # Define default class if security_utils is not available
    class SecurityUtils:
        @staticmethod
        def log_data_access(user, data_type, record_count, ip_address=None):
            pass

# Portfolio sample data generation function
def get_sample_user_counts_data():
    """Generate sample user count data for portfolio demonstration"""
    return pd.DataFrame({
        "Total Users": [185470],
        "App Users": [98320],
        "Non-App Users": [87150]
    })

def get_sample_mau_data():
    """Generate sample MAU data with realistic patterns"""
    months = ['202401', '202402', '202403', '202404', '202405', '202406', 
              '202407', '202408', '202409', '202410', '202411', '202412']
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    data = []
    for month in months:
        # Generate realistic MAU patterns (higher on weekends, seasonal trends)
        base_count = np.random.randint(8000, 15000)
        
        for weekday in weekdays:
            # Weekend effect (higher MAU on weekends)
            weekend_multiplier = 1.3 if weekday in ["Saturday", "Sunday"] else 1.0
            count = int(base_count * weekend_multiplier * np.random.uniform(0.8, 1.2))
            
            data.append({
                'ORDER_MONTH': month,
                'JOIN_WEEKDAY': weekday,
                'MAU_COUNT': count
            })
    
    return pd.DataFrame(data)

def get_sample_user_segments_data():
    """Generate sample user segment data"""
    segments = ["Heavy Users", "Regular Users", "Light Users", "Dormant Users", "New Users"]
    
    data = []
    for i, segment in enumerate(segments):
        # Generate realistic user counts per segment
        if segment == "Heavy Users":
            count = np.random.randint(8000, 12000)
        elif segment == "Regular Users":
            count = np.random.randint(25000, 35000)
        elif segment == "Light Users":
            count = np.random.randint(15000, 25000)
        elif segment == "Dormant Users":
            count = np.random.randint(20000, 30000)
        else:  # New Users
            count = np.random.randint(5000, 10000)
        
        # Create user IDs for the segment
        for user_id in range(1, count + 1):
            data.append({
                'SEGMENT': segment,
                'USERID': f"{segment[:3].upper()}{user_id:06d}"
            })
    
    return pd.DataFrame(data)

def show_page(session, brand=None, schema=None, role=None):
    # Brand-specific dynamic query configuration
    brand = brand or "BRAND_A"
    schema = schema or f"ANALYSIS_{brand}"
    table_prefix = f"DT_{brand}"
    
    # Get current user information
    current_user = st.session_state.get("username", "unknown")
    client_ip = st.session_state.get("client_ip", "unknown")
    
    # Brand-specific text mapping
    brand_texts = {
        "BRAND_A": {
            "title": "Coffee Brand A",
            "short": "Brand A",
            "app_name": "Order App A"
        },
        "BRAND_B": {
            "title": "Coffee Brand B", 
            "short": "Brand B",
            "app_name": "Order App B"
        }
    }
    
    # Get current brand text (default: BRAND_A)
    current_brand = brand_texts.get(brand, brand_texts["BRAND_A"])
    
    st.title(f"📊 User Segmentation & MAU Analysis")
    st.markdown(f"## Key User Metrics - {current_brand['title']}")
    
    # User count data - using sample data for portfolio
    df_user_counts = get_sample_user_counts_data()
    
    # Log data access
    total_records = len(df_user_counts)
    SecurityUtils.log_data_access(
        user=current_user,
        data_type=f"{brand}_USER_COUNTS",
        record_count=total_records,
        ip_address=client_ip
    )
    
    # Melt dataframe for visualization
    df_melted = df_user_counts[['App Users', 'Non-App Users']].melt(var_name='User Type', value_name='Count')
    
    # Visualization: Stacked bar chart
    fig_user_counts = px.bar(
        df_melted,
        x='User Type',
        y='Count',
        color='User Type',
        title=f'{current_brand["title"]} - App Users vs Non-App Users',
        labels={'Count': 'Number of Users', 'User Type': 'User Category'},
        color_discrete_sequence=['#B8865B', '#D9B48C']
    )
    st.plotly_chart(fig_user_counts, use_container_width=True)
    
    # Display additional information
    st.dataframe(df_user_counts.reset_index(drop=True), use_container_width=True)
    
    # Add section spacing
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 2. MAU Users (Monthly/Weekly)
    mau_data = get_sample_mau_data()
    
    # Convert ORDER_MONTH to 'YYYY-MM' format and create sorting column
    mau_data['ORDER_MONTH_STR'] = mau_data['ORDER_MONTH'].apply(lambda x: f"{str(x)[:4]}-{str(x)[4:]}")
    mau_data['ORDER_MONTH'] = pd.to_datetime(mau_data['ORDER_MONTH'], format='%Y%m')
    
    # Calculate monthly MAU user count
    monthly_mau = mau_data.groupby('ORDER_MONTH')['MAU_COUNT'].sum().reset_index()
    monthly_mau['ORDER_MONTH_STR'] = monthly_mau['ORDER_MONTH'].dt.strftime('%Y-%m')
    
    # Generate Plotly Bar Chart
    st.header(f"{current_brand['title']} MAU Users (Monthly)")
    st.markdown(f"""
    - **Analysis Purpose**: Track {current_brand['title']} monthly active users (MAU) and identify trends.
    - **Data Period**: January 2024 to December 2024
    - **Key Metrics**: 
        - New Users
        - Returning Users
        - Total Users
    - **Note**: Each monthly data can be filtered for in-depth analysis.
    """)

    # Column division
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Key Insights")
        st.markdown(f"""
        - **January**: {current_brand['title']} had the highest user count.
        - **March**: Usage slightly decreased.
        - **December**: Year-end season showed increased usage.
        """)
    
    with col2:
        st.markdown("#### User Demographics")
        st.markdown(f"""
        - **Largest User Group**: 20s age group
        - **Highest Growth Month**: June
        - **Returning User Rate**: 70%
        """)

    # Highlight emphasis (Markdown + HTML styling)
    st.markdown(f"""
    <div style="background-color: #F5E6C8; padding: 10px; border-radius: 5px;">
    <strong>💡 Key Point:</strong> 
    {current_brand['title']} data analysis can identify <u><strong>potential growth opportunities</u></strong>.
    </div>
    """, unsafe_allow_html=True)
    
    fig = px.bar(
        monthly_mau, 
        x='ORDER_MONTH_STR', 
        y='MAU_COUNT', 
        text='MAU_COUNT',
        title=f"{current_brand['title']} Monthly MAU Users",
        color_discrete_sequence=["#5C2D06"]
    )
    
    # Set text position and format
    fig.update_traces(textposition='outside')
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(monthly_mau, use_container_width=True)
    
    # Create weekly MAU user chart
    st.header(f"{current_brand['title']} MAU Users (Monthly/Weekly)")
    
    # Set weekday order
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Weekly rainbow color mapping (same as new subscribers page)
    weekday_color_map = {
        "Monday": "tomato",
        "Tuesday": "orange",
        "Wednesday": "gold",
        "Thursday": "limegreen",
        "Friday": "dodgerblue",
        "Saturday": "purple",
        "Sunday": "pink"
    }
    
    weekday_chart = px.bar(
        mau_data, 
        x='ORDER_MONTH_STR', 
        y='MAU_COUNT', 
        color='JOIN_WEEKDAY', 
        title=f"{current_brand['title']} Monthly/Weekly MAU Users",
        labels={"JOIN_WEEKDAY": "Weekday", "MAU_COUNT": "User Count", "ORDER_MONTH_STR": "Month"},
        category_orders={"JOIN_WEEKDAY": weekday_order},  # Fix weekday order
        color_discrete_map=weekday_color_map,  # Apply rainbow color mapping
    )
    
    # Set x-axis order for sorting (sort bar chart bars by month in ascending order)
    weekday_chart.update_layout(xaxis={'categoryorder':'category ascending'})
    
    st.plotly_chart(weekday_chart, use_container_width=True)
    st.dataframe(mau_data, use_container_width=True)
    st.markdown("<br><br><br>", unsafe_allow_html = True)
    
    # User segment data - using sample data for portfolio
    df_user_segments = get_sample_user_segments_data()
    
    # 3. User segment status (color-coded visualization)
    st.header(f"{current_brand['title']} User Segment Status")
    st.markdown(f"""
    - **Analysis Purpose**: Analyze user behavior patterns and segment characteristics for {current_brand['title']}.
    - **Segment Categories**: Heavy Users, Regular Users, Light Users, Dormant Users, New Users
    - **Business Value**: Enable targeted marketing and personalized service strategies.
    """)
    
    # Calculate segment statistics
    segment_counts = df_user_segments['SEGMENT'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    # Create pie chart for segment distribution
    fig_pie = px.pie(
        segment_counts, 
        values='Count', 
        names='Segment',
        title=f"{current_brand['title']} User Segment Distribution",
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Create bar chart for segment counts
    fig_segments = px.bar(
        segment_counts,
        x='Segment',
        y='Count',
        color='Segment',
        title=f"{current_brand['title']} User Count by Segment",
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    )
    st.plotly_chart(fig_segments, use_container_width=True)
    
    # Display segment summary table
    st.subheader("Segment Summary")
    segment_summary = segment_counts.copy()
    segment_summary['Percentage'] = (segment_summary['Count'] / segment_summary['Count'].sum() * 100).round(2)
    segment_summary['Percentage_Display'] = segment_summary['Percentage'].astype(str) + '%'
    
    st.dataframe(segment_summary, use_container_width=True)
    
    # Business insights
    st.markdown(f"""
    <div style="background-color: #E8F4FD; padding: 15px; border-radius: 5px;">
    <h4>📈 Business Insights</h4>
    <ul>
        <li><strong>Heavy Users</strong>: Premium service targets, loyalty program candidates</li>
        <li><strong>Regular Users</strong>: Core customer base, retention focus</li>
        <li><strong>Light Users</strong>: Engagement improvement opportunities</li>
        <li><strong>Dormant Users</strong>: Re-engagement campaign targets</li>
        <li><strong>New Users</strong>: Onboarding optimization focus</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Add download functionality
    st.markdown("---")
    st.subheader("Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download User Counts"):
            csv = df_user_counts.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{brand}_user_counts.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Download MAU Data"):
            csv = mau_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{brand}_mau_data.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📥 Download Segment Data"):
            csv = segment_counts.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{brand}_segment_summary.csv",
                mime="text/csv"
            )
    
    # Portfolio note
    st.markdown("""
    ---
    **📝 Portfolio Note**: This analysis uses sample data that mimics real customer behavior patterns. 
    In production, this would connect to live data warehouses with millions of user records.
    """) 