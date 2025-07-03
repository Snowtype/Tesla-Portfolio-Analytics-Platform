import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import io

def show_page(session, top_placeholder=None, brand=None, schema=None, role=None):
    # Brand-specific dynamic query generation settings
    brand = brand or "TPC"
    schema = schema or f"ANALYSIS_{brand}"
    
    # Brand-specific text mapping
    brand_texts = {
        "TPC": {
            "title": "Tesla Coffee",
            "short": "Tesla",
            "app_name": "TeslaOrder"
        },
        "MMC": {
            "title": "RoboBrew Coffee", 
            "short": "RoboBrew",
            "app_name": "RoboBrewOrder"
        }
    }
    
    # Get current brand text (default: TPC)
    current_brand = brand_texts.get(brand, brand_texts["TPC"])
    
    st.title(f"📌 {current_brand['title']} New/Signature Non-Purchasing Customers")
    
    # Description section
    with st.expander("📋 Analysis Description", expanded=False):
        st.markdown(f"""
        **This analysis targets the following customers:**
        
        - 📅 **Customers who purchased beverages within the last 30 days** (Active customers)
        - ❌ **Customers who have not purchased new products** (Products with BADGE_NEW=1)
        - ❌ **Customers who have not purchased signature products** (Products with 'signature' in the name)
        
        **Data Source:** `COMPANY_DW.{schema}.DT_{brand}_NON_NEW_SIG_CUSTOMERS`
        
        **Usage:**
        - Identify target customers for new/signature product marketing
        - Customer segmentation and customized promotion planning
        - Product recommendation system improvement
        """)
    
    try:
        # 1. Summary metrics query
        @st.cache_data(ttl=1800)  # 30 minute cache
        def get_summary_metrics(schema, brand):
            summary_query = f"""
            SELECT 
                COUNT(DISTINCT UID) as TOTAL_CUSTOMERS,
                MAX(LAST_ORDER_DATE) as LATEST_DATE,
                MIN(LAST_ORDER_DATE) as EARLIEST_DATE
            FROM COMPANY_DW.{schema}.DT_{brand}_NON_NEW_SIG_CUSTOMERS
            """
            return session.sql(summary_query).to_pandas()
        
        summary_data = get_summary_metrics(schema, brand)
        
        if summary_data.empty:
            st.warning("No data available. Please check the table.")
            return
        
        # 2. Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📊 Total Target Customers",
                value=f"{summary_data['TOTAL_CUSTOMERS'].iloc[0]:,} customers"
            )
        
        with col2:
            latest_date = summary_data['LATEST_DATE'].iloc[0]
            if latest_date:
                st.metric(
                    label="📅 Latest Order Date",
                    value=latest_date.strftime('%Y-%m-%d') if hasattr(latest_date, 'strftime') else str(latest_date)
                )
        
        with col3:
            earliest_date = summary_data['EARLIEST_DATE'].iloc[0]
            if earliest_date:
                st.metric(
                    label="📅 Earliest Order Date",
                    value=earliest_date.strftime('%Y-%m-%d') if hasattr(earliest_date, 'strftime') else str(earliest_date)
                )
        
        st.divider()
        
        # 3. Daily customer count trend chart
        @st.cache_data(ttl=1800)  # 30 minute cache
        def get_daily_trend(schema, brand):
            trend_query = f"""
            SELECT 
                LAST_ORDER_DATE,
                COUNT(DISTINCT UID) as CUSTOMER_COUNT
            FROM COMPANY_DW.{schema}.DT_{brand}_NON_NEW_SIG_CUSTOMERS
            WHERE LAST_ORDER_DATE >= CURRENT_DATE - 30
            GROUP BY LAST_ORDER_DATE
            ORDER BY LAST_ORDER_DATE DESC
            LIMIT 30
            """
            return session.sql(trend_query).to_pandas()
        
        trend_data = get_daily_trend(schema, brand)
        
        if not trend_data.empty:
            st.subheader("📈 Daily Target Customer Count Trend (Last 30 Days)")
            
            # Convert date column to datetime
            trend_data['LAST_ORDER_DATE'] = pd.to_datetime(trend_data['LAST_ORDER_DATE'])
            trend_data = trend_data.sort_values('LAST_ORDER_DATE')
            
            # Create line chart
            fig_line = px.line(
                trend_data, 
                x='LAST_ORDER_DATE', 
                y='CUSTOMER_COUNT',
                title=f"{current_brand['title']} New/Signature Non-Purchasing Customer Count Trend",
                labels={
                    'LAST_ORDER_DATE': 'Last Order Date',
                    'CUSTOMER_COUNT': 'Customer Count'
                }
            )
            
            fig_line.update_traces(
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8, color='#FF6B6B')
            )
            
            fig_line.update_layout(
                xaxis_title="Last Order Date",
                yaxis_title="Customer Count",
                hovermode='x unified',
                showlegend=False
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Also provide bar chart
            fig_bar = px.bar(
                trend_data, 
                x='LAST_ORDER_DATE', 
                y='CUSTOMER_COUNT',
                title=f"{current_brand['title']} New/Signature Non-Purchasing Customer Count (Bar Chart)",
                labels={
                    'LAST_ORDER_DATE': 'Last Order Date',
                    'CUSTOMER_COUNT': 'Customer Count'
                }
            )
            
            fig_bar.update_traces(marker_color='#4ECDC4')
            fig_bar.update_layout(
                xaxis_title="Last Order Date",
                yaxis_title="Customer Count",
                showlegend=False
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.divider()
        
        # 4. Weekly aggregation chart
        @st.cache_data(ttl=1800)  # 30 minute cache
        def get_weekly_trend(schema, brand):
            weekly_query = f"""
            SELECT 
                DATE_TRUNC('WEEK', LAST_ORDER_DATE) as WEEK_START,
                COUNT(DISTINCT UID) as CUSTOMER_COUNT
            FROM COMPANY_DW.{schema}.DT_{brand}_NON_NEW_SIG_CUSTOMERS
            WHERE LAST_ORDER_DATE >= CURRENT_DATE - 56  -- 8 weeks
            GROUP BY DATE_TRUNC('WEEK', LAST_ORDER_DATE)
            ORDER BY WEEK_START DESC
            """
            return session.sql(weekly_query).to_pandas()
        
        weekly_data = get_weekly_trend(schema, brand)
        
        if not weekly_data.empty:
            st.subheader("📊 Weekly Target Customer Count (Last 8 Weeks)")
            
            # Add week information
            weekly_data['WEEK_START'] = pd.to_datetime(weekly_data['WEEK_START'])
            weekly_data = weekly_data.sort_values('WEEK_START')
            weekly_data['WEEK_LABEL'] = weekly_data['WEEK_START'].dt.strftime('%Y-%m-%d') + ' Week'
            
            fig_weekly = px.bar(
                weekly_data,
                x='WEEK_LABEL',
                y='CUSTOMER_COUNT',
                title=f"{current_brand['title']} Weekly New/Signature Non-Purchasing Customer Count",
                labels={
                    'WEEK_LABEL': 'Week',
                    'CUSTOMER_COUNT': 'Customer Count'
                }
            )
            
            fig_weekly.update_traces(marker_color='#95E1D3')
            fig_weekly.update_layout(
                xaxis_title="Week",
                yaxis_title="Customer Count",
                xaxis_tickangle=-45,
                showlegend=False
            )
            
            st.plotly_chart(fig_weekly, use_container_width=True)
        
        st.divider()
        
        # 5. Data download section
        st.subheader("💾 Data Download")
        
        @st.cache_data(ttl=1800)  # 30 minute cache
        def get_full_customer_list(schema, brand):
            full_query = f"""
            SELECT 
                UID as CustomerID,
                LAST_ORDER_DATE as LastOrderDate
            FROM COMPANY_DW.{schema}.DT_{brand}_NON_NEW_SIG_CUSTOMERS
            ORDER BY LAST_ORDER_DATE DESC, UID
            """
            return session.sql(full_query).to_pandas()
        
        if st.button("📋 View Full Customer List", type="secondary"):
            with st.spinner("Loading data..."):
                full_data = get_full_customer_list(schema, brand)
                
                if not full_data.empty:
                    st.success(f"Retrieved {len(full_data):,} customer records.")
                    
                    # Data preview
                    st.subheader("📋 Data Preview (Top 100)")
                    st.dataframe(full_data.head(100), use_container_width=True)
                    
                    # CSV download button
                    csv_buffer = io.StringIO()
                    full_data.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                    csv_data = csv_buffer.getvalue()
                    
                    current_date = datetime.now().strftime('%Y%m%d')
                    filename = f"{current_brand['short']}_NewSignature_NonPurchasingCustomers_{current_date}.csv"
                    
                    st.download_button(
                        label="📥 Download CSV File",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        type="primary"
                    )
                else:
                    st.warning("No data available for download.")
        
        # 6. Additional insights
        st.divider()
        
        with st.expander("💡 Marketing Utilization Ideas", expanded=False):
            st.markdown(f"""
            ### 🎯 Target Marketing Strategy
            
            **1. New Product Promotion**
            - Provide new product discount coupons to these customers
            - Invite to new product free tasting events
            - Personalized message: "Experience new flavors"
            
            **2. Signature Product Recommendation**
            - Introduce {current_brand['title']} representative signature menu
            - Signature product bundle discount (beverage + dessert)
            - Double points for signature product purchases
            
            **3. Personalized Marketing**
            - Customized recommendations based on customer order history
            - Recommend new/signature products similar to usual order patterns
            - Push notifications based on preferred time/day
            
            **4. Retention Enhancement**
            - Next visit discount coupon for new/signature product purchases
            - Rewards for consecutive purchases
            - VIP customer exclusive new product preview events
            """)
    
    except Exception as e:
        st.error(f"Error occurred while loading data: {str(e)}")
        st.info("Please check Snowflake connection or table name.")
        
        # Display debugging information
        with st.expander("🔍 Debug Information", expanded=False):
            st.code(f"""
            Schema: {schema}
            Brand: {brand}
            Table: COMPANY_DW.{schema}.DT_{brand}_NON_NEW_SIG_CUSTOMERS
            
            Expected columns:
            - UID (customer ID)
            - LAST_ORDER_DATE (date of last beverage purchase)
            """) 