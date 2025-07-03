import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date, time
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
    
    st.title(f"⏰ {current_brand['title']} Regional Hourly Popular Product Sales Trends")
    
    # Description section
    with st.expander("📋 Analysis Description", expanded=False):
        st.markdown(f"""
        **This analysis provides time-based regional product sales patterns:**
        
        🕐 **Time-based Analysis**
        - Regional popular products TOP 5 by specific time periods
        - Product sales trend changes by time period
        - Peak time and low time identification
        
        🗺️ **Regional Analysis**
        - Regional time preference differences
        - Regional customized operation time optimization
        - Regional product demand pattern analysis
        
        **Data Source:**
        - `COMPANY_DW.{schema}.DT_{brand}_HOURLY_PRODUCT_SALES_BY_REGION`
        
        **Usage:**
        - Time-based store operation optimization
        - Regional customized product display strategy
        - Peak time staffing plan
        """)
    
    # 1. First load data to secure filter options (new_subscribers.py method)
    try:
        @st.cache_data(ttl=1800)  # 30 minute cache
        def get_sales_data(schema, brand):
            query = f"""
            SELECT 
                ADDR_CODE,
                ITEM_NAME,
                ORDER_TIMESTAMP,
                ORDER_COUNT
            FROM COMPANY_DW.{schema}.DT_{brand}_HOURLY_PRODUCT_SALES_BY_REGION
            WHERE ORDER_TIMESTAMP IS NOT NULL
            ORDER BY ORDER_TIMESTAMP, ADDR_CODE, ORDER_COUNT DESC
            """
            return session.sql(query).to_pandas()
        
        # Load data
        raw_data = get_sales_data(schema, brand)
        
        if raw_data.empty:
            st.warning("No data available. Please check the table.")
            return
        
        # Data preprocessing
        raw_data['ORDER_TIMESTAMP'] = pd.to_datetime(raw_data['ORDER_TIMESTAMP'])
        raw_data['DATE'] = raw_data['ORDER_TIMESTAMP'].dt.date
        raw_data['HOUR'] = raw_data['ORDER_TIMESTAMP'].dt.hour
        
        # Extract available options
        available_regions = sorted(raw_data['ADDR_CODE'].unique())
        available_products = sorted(raw_data['ITEM_NAME'].unique())
        
        # 2. Place all filters in top_placeholder.container()
        if top_placeholder:
            with top_placeholder.container():
                st.subheader("🔍 Filter Settings")
                
                # Date range selection
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Start Date",
                        value=date(2025, 1, 1),  # Set default value
                        key="hourly_start_date"
                    )
                with col2:
                    end_date = st.date_input(
                        "End Date",
                        value=date.today(),  # Set default value
                        key="hourly_end_date"
                    )
                
                # Time range selection
                col3, col4 = st.columns(2)
                with col3:
                    start_hour = st.selectbox(
                        "Start Time",
                        options=list(range(24)),
                        index=0,
                        format_func=lambda x: f"{x:02d}:00",
                        key="hourly_start_hour"
                    )
                with col4:
                    end_hour = st.selectbox(
                        "End Time",
                        options=list(range(24)),
                        index=23,
                        format_func=lambda x: f"{x:02d}:00",
                        key="hourly_end_hour"
                    )
                
                # Region selection
                col5 = st.columns(1)[0]
                with col5:
                    selected_region = st.selectbox(
                        "Region Selection",
                        options=["All"] + available_regions,
                        index=0,
                        key="hourly_region"
                    )
                
                st.write(f"Selected period: {start_date} ~ {end_date}")
                st.write(f"Selected time range: {start_hour:02d}:00 ~ {end_hour:02d}:00")
        else:
            # Filter in main area
            st.subheader("🔍 Filter Settings")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                start_date = st.date_input("Start Date", value=date(2025, 1, 1))
            with col2:
                end_date = st.date_input("End Date", value=date.today())
            with col3:
                start_hour = st.selectbox("Start Time", options=list(range(24)), index=0, format_func=lambda x: f"{x:02d}:00")
            with col4:
                end_hour = st.selectbox("End Time", options=list(range(24)), index=23, format_func=lambda x: f"{x:02d}:00")
            
            col5 = st.columns(1)[0]
            with col5:
                selected_region = st.selectbox("Region Selection", options=["All"] + available_regions, index=0)
        
        # Add menu filter to sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("🍽️ Menu Filter")
        selected_product = st.sidebar.selectbox(
            "Product Selection (for time-based trends)",
            options=["All"] + available_products,
            index=0,
            key="hourly_product"
        )
        
        # 3. Data filtering and deduplication
        filtered_data = raw_data[
            (raw_data['DATE'] >= start_date) & 
            (raw_data['DATE'] <= end_date) &
            (raw_data['HOUR'] >= start_hour) &
            (raw_data['HOUR'] <= end_hour)
        ].copy()
        
        if selected_region != "All":
            filtered_data = filtered_data[filtered_data['ADDR_CODE'] == selected_region]
        
        # Remove duplicate data and verify
        original_count = len(filtered_data)
        filtered_data = filtered_data.drop_duplicates(subset=['ADDR_CODE', 'ITEM_NAME', 'ORDER_TIMESTAMP'])
        deduplicated_count = len(filtered_data)
        
        # Display deduplication results for debugging
        if original_count != deduplicated_count:
            st.warning(f"⚠️ {original_count - deduplicated_count} duplicate records removed. (Original: {original_count} → After cleanup: {deduplicated_count})")
        
        if filtered_data.empty:
            st.warning("No data matches the selected conditions.")
            return
        
        # Create tabs
        tab1, tab2 = st.tabs(["📊 Hourly TOP 5 Products", "📈 Product Time-based Trends"])
        
        # Tab 1: Hourly TOP 5 Products
        with tab1:
            st.subheader("📊 TOP 5 Popular Products by Selected Criteria")
            
            # Display selected criteria summary
            region_text = selected_region if selected_region != "All" else "All Regions"
            date_text = f"{start_date} ~ {end_date}"
            time_text = f"{start_hour:02d}:00 ~ {end_hour:02d}:00"
            
            st.info(f"📍 **Region**: {region_text} | 📅 **Period**: {date_text} | ⏰ **Time Range**: {time_text}")
            
            # TOP 5 product aggregation
            top5_data = filtered_data.groupby('ITEM_NAME')['ORDER_COUNT'].sum().reset_index()
            top5_data = top5_data.sort_values('ORDER_COUNT', ascending=False).head(5)
            
            if not top5_data.empty:
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_orders = top5_data['ORDER_COUNT'].sum()
                    st.metric("Total Orders", f"{total_orders:,} orders")
                with col2:
                    top_product = top5_data.iloc[0]
                    st.metric("1st Place Product", top_product['ITEM_NAME'])
                with col3:
                    top_share = (top_product['ORDER_COUNT'] / total_orders) * 100
                    st.metric("1st Place Share", f"{top_share:.1f}%")
                
                # Bar chart
                fig_top5 = px.bar(
                    top5_data,
                    x='ORDER_COUNT',
                    y='ITEM_NAME',
                    orientation='h',
                    title=f"{region_text} TOP 5 Popular Products ({time_text})",
                    labels={
                        'ORDER_COUNT': 'Order Count',
                        'ITEM_NAME': 'Product Name'
                    },
                    color='ORDER_COUNT',
                    color_continuous_scale='Viridis'
                )
                
                fig_top5.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_top5, use_container_width=True)
                
                # Detailed table
                st.subheader("📋 Detailed Rankings")
                
                top5_display = top5_data.copy()
                top5_display['Rank'] = range(1, len(top5_display) + 1)
                top5_display['Share(%)'] = (top5_display['ORDER_COUNT'] / total_orders * 100).round(1)
                top5_display = top5_display[['Rank', 'ITEM_NAME', 'ORDER_COUNT', 'Share(%)']]
                top5_display.columns = ['Rank', 'Product Name', 'Order Count', 'Share(%)']
                
                st.dataframe(top5_display, use_container_width=True)
            else:
                st.warning("No product data matches the selected conditions.")
        
        # Tab 2: Product Time-based Trends
        with tab2:
            if selected_product == "All":
                st.subheader("📈 All Products Time-based Sales Trends")
                
                # Aggregate all products by time period
                hourly_trend = filtered_data.groupby('HOUR')['ORDER_COUNT'].sum().reset_index()
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_orders = hourly_trend['ORDER_COUNT'].sum()
                    st.metric("Total Orders", f"{total_orders:,} orders")
                with col2:
                    peak_hour = hourly_trend.loc[hourly_trend['ORDER_COUNT'].idxmax(), 'HOUR']
                    st.metric("Peak Time", f"{peak_hour:02d}:00")
                with col3:
                    peak_orders = hourly_trend['ORDER_COUNT'].max()
                    st.metric("Peak Orders", f"{peak_orders:,} orders")
                with col4:
                    avg_orders = hourly_trend['ORDER_COUNT'].mean()
                    st.metric("Hourly Average", f"{avg_orders:.0f} orders")
                
                # Line chart - all products
                fig_trend = px.line(
                    hourly_trend,
                    x='HOUR',
                    y='ORDER_COUNT',
                    title="All Products Time-based Sales Trends",
                    labels={
                        'HOUR': 'Time',
                        'ORDER_COUNT': 'Order Count'
                    },
                    markers=True
                )
                
                fig_trend.update_layout(
                    xaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=1,
                        tickformat='%02d:00'
                    ),
                    height=400
                )
                
                # Highlight peak time
                fig_trend.add_vline(
                    x=peak_hour,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Peak: {peak_hour:02d}:00"
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # TOP 5 products time-based trend comparison
                st.subheader("📊 Popular Products Time-based Trend Comparison")
                
                # Extract TOP 5 products
                top5_products = filtered_data.groupby('ITEM_NAME')['ORDER_COUNT'].sum().sort_values(ascending=False).head(5).index
                
                # TOP 5 products time-based data
                top5_hourly = filtered_data[filtered_data['ITEM_NAME'].isin(top5_products)].groupby(['HOUR', 'ITEM_NAME'])['ORDER_COUNT'].sum().reset_index()
                
                # Multi-line chart
                fig_multi = px.line(
                    top5_hourly,
                    x='HOUR',
                    y='ORDER_COUNT',
                    color='ITEM_NAME',
                    title="TOP 5 Products Time-based Sales Trends",
                    labels={
                        'HOUR': 'Time',
                        'ORDER_COUNT': 'Order Count',
                        'ITEM_NAME': 'Product Name'
                    },
                    markers=True
                )
                
                fig_multi.update_layout(
                    xaxis=dict(
                        tickmode='linear',
                        tick0=0,
                        dtick=1,
                        tickformat='%02d:00'
                    ),
                    height=400,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig_multi, use_container_width=True)
                
                # Time-based detailed table - all
                st.subheader("📊 Time-based Detailed Data (All)")
                
                hourly_display = hourly_trend.copy()
                hourly_display['Time Period'] = hourly_display['HOUR'].apply(lambda x: f"{x:02d}:00")
                hourly_display['Ratio(%)'] = (hourly_display['ORDER_COUNT'] / total_orders * 100).round(1)
                hourly_display = hourly_display[['Time Period', 'ORDER_COUNT', 'Ratio(%)']]
                hourly_display.columns = ['Time Period', 'Order Count', 'Ratio(%)']
                
                st.dataframe(hourly_display, use_container_width=True)
                
            else:
                st.subheader(f"📈 {selected_product} Time-based Sales Trends")
                
                # Aggregate selected product time-based data
                product_data = filtered_data[filtered_data['ITEM_NAME'] == selected_product]
                
                if not product_data.empty:
                    # Time-based aggregation
                    hourly_trend = product_data.groupby('HOUR')['ORDER_COUNT'].sum().reset_index()
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        total_orders = hourly_trend['ORDER_COUNT'].sum()
                        st.metric("Total Orders", f"{total_orders:,} orders")
                    with col2:
                        peak_hour = hourly_trend.loc[hourly_trend['ORDER_COUNT'].idxmax(), 'HOUR']
                        st.metric("Peak Time", f"{peak_hour:02d}:00")
                    with col3:
                        peak_orders = hourly_trend['ORDER_COUNT'].max()
                        st.metric("Peak Orders", f"{peak_orders:,} orders")
                    with col4:
                        avg_orders = hourly_trend['ORDER_COUNT'].mean()
                        st.metric("Hourly Average", f"{avg_orders:.0f} orders")
                    
                    # Line chart
                    fig_trend = px.line(
                        hourly_trend,
                        x='HOUR',
                        y='ORDER_COUNT',
                        title=f"{selected_product} Time-based Sales Trends",
                        labels={
                            'HOUR': 'Time',
                            'ORDER_COUNT': 'Order Count'
                        },
                        markers=True
                    )
                    
                    fig_trend.update_layout(
                        xaxis=dict(
                            tickmode='linear',
                            tick0=0,
                            dtick=1,
                            tickformat='%02d:00'
                        ),
                        height=400
                    )
                    
                    # Highlight peak time
                    fig_trend.add_vline(
                        x=peak_hour,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Peak: {peak_hour:02d}:00"
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # Regional comparison (when all regions selected)
                    if selected_region == "All":
                        st.subheader("🗺️ Regional Time-based Comparison")
                        
                        regional_comparison = product_data.groupby(['ADDR_CODE', 'HOUR'])['ORDER_COUNT'].sum().reset_index()
                        
                        fig_heatmap = px.density_heatmap(
                            regional_comparison,
                            x='HOUR',
                            y='ADDR_CODE',
                            z='ORDER_COUNT',
                            title=f"{selected_product} Regional Time-based Sales Volume Heatmap",
                            labels={
                                'HOUR': 'Time',
                                'ADDR_CODE': 'Region',
                                'ORDER_COUNT': 'Order Count'
                            },
                            color_continuous_scale='Blues'
                        )
                        
                        fig_heatmap.update_layout(
                            xaxis=dict(
                                tickmode='linear',
                                tick0=0,
                                dtick=1,
                                tickformat='%02d:00'
                            ),
                            height=500
                        )
                        
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                    # Time-based detailed table
                    st.subheader("📊 Time-based Detailed Data")
                    
                    hourly_display = hourly_trend.copy()
                    hourly_display['Time Period'] = hourly_display['HOUR'].apply(lambda x: f"{x:02d}:00")
                    hourly_display['Ratio(%)'] = (hourly_display['ORDER_COUNT'] / total_orders * 100).round(1)
                    hourly_display = hourly_display[['Time Period', 'ORDER_COUNT', 'Ratio(%)']]
                    hourly_display.columns = ['Time Period', 'Order Count', 'Ratio(%)']
                    
                    st.dataframe(hourly_display, use_container_width=True)
                else:
                    st.warning(f"No data available for '{selected_product}' product under selected conditions.")
        
        st.divider()
        
        # Data download section
        st.subheader("💾 Data Download")
        
        if st.button("📊 Download Filtered Data", type="secondary"):
            if not filtered_data.empty:
                csv_buffer = io.StringIO()
                download_data = filtered_data.copy()
                download_data['Date'] = download_data['DATE']
                download_data['Time'] = download_data['HOUR']
                download_data = download_data[['ADDR_CODE', 'ITEM_NAME', 'Date', 'Time', 'ORDER_COUNT']]
                download_data.columns = ['Region', 'Product Name', 'Date', 'Time', 'Order Count']
                download_data.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                csv_data = csv_buffer.getvalue()
                
                current_datetime = datetime.now().strftime('%Y%m%d_%H%M')
                filename = f"{current_brand['short']}_HourlyProductSales_{current_datetime}.csv"
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    type="primary"
                )
            else:
                st.warning("No data available for download.")
        
        # Marketing insights
        st.divider()
        
        with st.expander("💡 Operation Optimization Insights", expanded=False):
            st.markdown(f"""
            ### 🕐 Time-based Operation Strategy
            
            **⏰ Peak Time Operations**
            - **Staffing**: Concentrate staff during major sales hours
            - **Ingredient Preparation**: Prepare sufficient ingredients focusing on popular products
            - **Equipment Check**: Check equipment status and standby before peak time
            
            **🌙 Off-Peak Operations**
            - **Limited Menu**: Simplified menu operation during low demand hours
            - **Cleaning and Maintenance**: Store cleaning and equipment maintenance during quiet hours
            - **Training Time**: Utilize staff education and training time
            
            **🗺️ Regional Customized Operations**
            - **Operation Hours**: Adjust operation hours according to regional demand patterns
            - **Product Composition**: Menu composition focusing on regionally preferred products
            - **Promotion**: Target marketing for regional major time periods
            
            **📊 Revenue Optimization**
            - **Dynamic Pricing**: Price policy based on time-based demand
            - **Bundle Products**: Set menus for faster peak time ordering
            - **Pre-orders**: Encourage pre-orders to reduce peak time congestion
            
            ### 📈 Monitoring Indicators
            - Time-based revenue change rate
            - Peak time order processing time
            - Regional time-based demand prediction accuracy
            - Staff efficiency indicators
            """) 
    except Exception as e:
        st.error(f"Error occurred while loading data: {str(e)}")
        st.info("Please check Snowflake connection or table name.")
        
        # Display debugging information
        with st.expander("🔍 Debug Information", expanded=False):
            st.code(f"""
            Schema: {schema}
            Brand: {brand}
            
            Time-based Sales Table: COMPANY_DW.{schema}.DT_{brand}_HOURLY_PRODUCT_SALES_BY_REGION
            Expected columns:
            - ADDR_CODE (region name)
            - ITEM_NAME (product name)
            - ORDER_TIMESTAMP (order timestamp, DATETIME)
            - ORDER_COUNT (product order count for that time period)
            """)
        return 