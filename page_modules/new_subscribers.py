import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

# Security utility import
try:
    from security_utils import SecurityUtils
except ImportError:
    class SecurityUtils:
        @staticmethod
        def log_data_access(user, data_type, record_count, ip_address=None):
            pass

# Sample data generation functions
def get_sample_new_subscribers_data():
    """Generate sample new subscriber data for portfolio demonstration"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    weekdays_english = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    age_groups = ["20s", "30s", "40s", "50s", "60+"]
    
    data = []
    for date in dates:
        weekday = weekdays_english[date.weekday()]
        
        # Weekend effect and seasonal patterns
        base_count = 150 if weekday in ["Saturday", "Sunday"] else 100
        
        # Seasonal effects
        month = date.month
        if month in [1, 12]:  # New Year effect
            seasonal_multiplier = 1.4
        elif month in [6, 7, 8]:  # Summer boost
            seasonal_multiplier = 1.2
        elif month in [3, 4, 5]:  # Spring growth
            seasonal_multiplier = 1.1
        else:
            seasonal_multiplier = 1.0
        
        total_subscribers = int(base_count * seasonal_multiplier * np.random.uniform(0.7, 1.3))
        
        # Age group distribution
        for age_group in age_groups:
            if age_group in ["20s", "30s"]:
                count = int(total_subscribers * np.random.uniform(0.25, 0.35))
            elif age_group == "40s":
                count = int(total_subscribers * np.random.uniform(0.15, 0.25))
            else:
                count = int(total_subscribers * np.random.uniform(0.05, 0.15))
            
            data.append({
                'NEW_SUBSCRIBER_DATE': date.strftime('%Y-%m-%d'),
                'JOIN_WEEKDAY': weekday,
                'AGE_GROUP': age_group,
                'NEW_SUBSCRIBER_COUNT': count
            })
    
    return pd.DataFrame(data)

def show_page(session, top_placeholder, month_options, brand=None, schema=None, role=None):
    # Brand configuration
    brand = brand or "BRAND_A"
    schema = schema or f"ANALYSIS_{brand}"
    table_prefix = f"DT_{brand}"
    
    # Get current user info
    current_user = st.session_state.get("username", "unknown")
    client_ip = st.session_state.get("client_ip", "unknown")
    
    # Brand text mapping
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
    
    current_brand = brand_texts.get(brand, brand_texts["BRAND_A"])
    
    st.title(f"📈 Daily New Subscribers Analysis")
    st.markdown(f"## {current_brand['title']} - Growth Tracking")
    
    # Sidebar controls
    with top_placeholder.container():
        st.markdown("### 🗓️ Period Selection")
        
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.selectbox("Start Year", [2023, 2024], index=1, key="new_sub_start_year")
            start_month = st.selectbox("Start Month", list(month_options.keys()), index=0, key="new_sub_start_month")
        
        with col2:
            end_year = st.selectbox("End Year", [2023, 2024], index=1, key="new_sub_end_year")
            end_month = st.selectbox("End Month", list(month_options.keys()), index=11, key="new_sub_end_month")
        
        # Age group filter
        st.markdown("### 👥 Age Group Filter")
        age_groups = ["All", "20s", "30s", "40s", "50s", "60+"]
        selected_age_group = st.selectbox("Select Age Group", age_groups, key="age_group_filter")
        
        # Apply filters button
        apply_filters = st.button("🔍 Apply Filters", key="apply_new_sub_filters")
    
    # Get sample data for portfolio
    df_new_subscribers = get_sample_new_subscribers_data()
    
    # Log data access
    SecurityUtils.log_data_access(
        user=current_user,
        data_type=f"{brand}_NEW_SUBSCRIBERS",
        record_count=len(df_new_subscribers),
        ip_address=client_ip
    )
    
    # Convert date column
    df_new_subscribers['NEW_SUBSCRIBER_DATE'] = pd.to_datetime(df_new_subscribers['NEW_SUBSCRIBER_DATE'])
    
    # Apply filters
    if apply_filters or 'filtered_data' not in st.session_state:
        # Date range filter
        start_date = pd.to_datetime(f"{start_year}-{start_month}-01")
        if end_month == "12":
            end_date = pd.to_datetime(f"{end_year}-12-31")
        else:
            next_month = str(int(end_month) + 1).zfill(2)
            end_date = pd.to_datetime(f"{end_year}-{next_month}-01") - pd.Timedelta(days=1)
        
        filtered_data = df_new_subscribers[
            (df_new_subscribers['NEW_SUBSCRIBER_DATE'] >= start_date) &
            (df_new_subscribers['NEW_SUBSCRIBER_DATE'] <= end_date)
        ]
        
        # Age group filter
        if selected_age_group != "All":
            filtered_data = filtered_data[filtered_data['AGE_GROUP'] == selected_age_group]
        
        st.session_state['filtered_data'] = filtered_data
    else:
        filtered_data = st.session_state['filtered_data']
    
    # Analysis results
    if not filtered_data.empty:
        # Daily trend analysis
        st.header("📊 Daily Subscriber Trends")
        
        daily_data = filtered_data.groupby('NEW_SUBSCRIBER_DATE')['NEW_SUBSCRIBER_COUNT'].sum().reset_index()
        daily_data['Date_Display'] = daily_data['NEW_SUBSCRIBER_DATE'].dt.strftime('%Y-%m-%d')
        
        # Create line chart
        fig_daily = px.line(
            daily_data,
            x='NEW_SUBSCRIBER_DATE',
            y='NEW_SUBSCRIBER_COUNT',
            title=f"{current_brand['title']} Daily New Subscribers Trend",
            labels={'NEW_SUBSCRIBER_COUNT': 'New Subscribers', 'NEW_SUBSCRIBER_DATE': 'Date'}
        )
        fig_daily.update_traces(line_color='#1f77b4', line_width=2)
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Weekday analysis
        st.header("📅 Weekly Pattern Analysis")
        
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_color_map = {
            "Monday": "tomato",
            "Tuesday": "orange", 
            "Wednesday": "gold",
            "Thursday": "limegreen",
            "Friday": "dodgerblue",
            "Saturday": "purple",
            "Sunday": "pink"
        }
        
        weekday_data = filtered_data.groupby('JOIN_WEEKDAY')['NEW_SUBSCRIBER_COUNT'].sum().reset_index()
        weekday_data['JOIN_WEEKDAY'] = pd.Categorical(weekday_data['JOIN_WEEKDAY'], categories=weekday_order, ordered=True)
        weekday_data = weekday_data.sort_values('JOIN_WEEKDAY')
        
        fig_weekday = px.bar(
            weekday_data,
            x='JOIN_WEEKDAY',
            y='NEW_SUBSCRIBER_COUNT',
            color='JOIN_WEEKDAY',
            title=f"{current_brand['title']} New Subscribers by Weekday",
            labels={'NEW_SUBSCRIBER_COUNT': 'Total New Subscribers', 'JOIN_WEEKDAY': 'Day of Week'},
            color_discrete_map=weekday_color_map
        )
        st.plotly_chart(fig_weekday, use_container_width=True)
        
        # Age group analysis
        st.header("👥 Age Group Distribution")
        
        age_data = filtered_data.groupby('AGE_GROUP')['NEW_SUBSCRIBER_COUNT'].sum().reset_index()
        
        # Pie chart for age distribution
        fig_age_pie = px.pie(
            age_data,
            values='NEW_SUBSCRIBER_COUNT',
            names='AGE_GROUP',
            title=f"{current_brand['title']} New Subscribers by Age Group",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
        )
        st.plotly_chart(fig_age_pie, use_container_width=True)
        
        # Bar chart for age group
        fig_age_bar = px.bar(
            age_data,
            x='AGE_GROUP',
            y='NEW_SUBSCRIBER_COUNT',
            color='AGE_GROUP',
            title=f"{current_brand['title']} New Subscribers Count by Age Group",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
        )
        st.plotly_chart(fig_age_bar, use_container_width=True)
        
        # Summary statistics
        st.header("📈 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_subscribers = filtered_data['NEW_SUBSCRIBER_COUNT'].sum()
        avg_daily = filtered_data.groupby('NEW_SUBSCRIBER_DATE')['NEW_SUBSCRIBER_COUNT'].sum().mean()
        max_daily = filtered_data.groupby('NEW_SUBSCRIBER_DATE')['NEW_SUBSCRIBER_COUNT'].sum().max()
        min_daily = filtered_data.groupby('NEW_SUBSCRIBER_DATE')['NEW_SUBSCRIBER_COUNT'].sum().min()
        
        with col1:
            st.metric("Total New Subscribers", f"{total_subscribers:,}")
        
        with col2:
            st.metric("Average Daily", f"{avg_daily:.1f}")
        
        with col3:
            st.metric("Peak Day", f"{max_daily:,}")
        
        with col4:
            st.metric("Lowest Day", f"{min_daily:,}")
        
        # Business insights
        st.markdown("""
        <div style="background-color: #E8F4FD; padding: 15px; border-radius: 5px;">
        <h4>🎯 Business Insights</h4>
        <ul>
            <li><strong>Weekend Effect</strong>: Typically higher sign-ups on weekends</li>
            <li><strong>Age Demographics</strong>: 20s and 30s represent the largest user segments</li>
            <li><strong>Seasonal Patterns</strong>: New Year and summer periods show increased activity</li>
            <li><strong>Growth Opportunities</strong>: Target marketing campaigns during peak periods</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Data export
        st.markdown("---")
        st.subheader("📥 Data Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download Daily Data"):
                csv = daily_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{brand}_daily_new_subscribers.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Download Detailed Data"):
                csv = filtered_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{brand}_new_subscribers_detailed.csv",
                    mime="text/csv"
                )
        
        # Display data table
        st.subheader("📋 Data Table")
        st.dataframe(filtered_data.head(100), use_container_width=True)
        
    else:
        st.warning("⚠️ No data found for the selected criteria. Please adjust your filters.")
    
    # Portfolio note
    st.markdown("""
    ---
    **📝 Portfolio Note**: This analysis demonstrates growth tracking capabilities using sample data. 
    In production, this would analyze real subscriber data to identify growth patterns and optimization opportunities.
    """) 