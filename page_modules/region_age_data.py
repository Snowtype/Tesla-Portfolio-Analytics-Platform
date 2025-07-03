import streamlit as st
import plotly.express as px
import pandas as pd
import calendar

def show_page(session, top_placeholder, brand=None, schema=None, role=None):
    # Brand-specific dynamic query generation settings
    brand = brand or "TPC"
    schema = schema or f"ANALYSIS_{brand}"
    table_prefix = f"DT_{brand}"
    
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
    
    st.title(f"🗺️ {current_brand['title']} Regional Age Group Data Analysis")
    
    # Description section
    with st.expander("📋 Analysis Description", expanded=False):
        st.markdown(f"""
        **This analysis provides regional age group distribution and trends:**
        
        🗺️ **Regional Analysis**
        - Age group distribution by region
        - Regional customer demographic characteristics
        - Regional age preference patterns
        
        👥 **Age Group Analysis**
        - Age group distribution trends
        - Age group-specific regional preferences
        - Age group customer behavior patterns
        
        **Data Source:**
        - `COMPANY_DW.{schema}.DT_{brand}_AGE_GROUP_USERS`
        - `COMPANY_DW.{schema}.DT_{brand}_AGE_GROUP_MEMBERS`
        
        **Usage:**
        - Regional marketing strategy development
        - Age group targeted product planning
        - Regional store operation optimization
        """)
    
    # Create tabs for different analysis types
    tab1, tab2, tab3 = st.tabs(["📊 Regional Age Distribution", "👥 Age Group Regional Analysis", "📈 Trend Analysis"])
    
    # Tab 1: Regional Age Distribution
    with tab1:
        st.subheader("📊 Regional Age Group Distribution")
        
        # Load regional age group data
        @st.cache_data(ttl=3600)  # 1 hour cache
        def load_regional_age_data(schema, brand):
            query = f"""
            SELECT 
                ADDR_CODE,
                AGE_GROUP,
                USER_COUNT,
                MEMBER_COUNT,
                TOTAL_COUNT
            FROM COMPANY_DW.{schema}.DT_{brand}_AGE_GROUP_USERS
            ORDER BY ADDR_CODE, AGE_GROUP
            """
            return session.sql(query).to_pandas()
        
        try:
            regional_data = load_regional_age_data(schema, brand)
            
            if regional_data.empty:
                st.warning("No regional age group data available.")
                return
            
            # Filter settings
            col1, col2 = st.columns(2)
            with col1:
                selected_region = st.selectbox(
                    "Region Selection",
                    options=["All"] + sorted(regional_data['ADDR_CODE'].unique().tolist()),
                    index=0,
                    key="regional_age_region"
                )
            
            with col2:
                age_group_filter = st.selectbox(
                    "Age Group Filter",
                    options=["All"] + sorted(regional_data['AGE_GROUP'].unique().tolist()),
                    index=0,
                    key="regional_age_filter"
                )
            
            # Filter data
            filtered_data = regional_data.copy()
            if selected_region != "All":
                filtered_data = filtered_data[filtered_data['ADDR_CODE'] == selected_region]
            if age_group_filter != "All":
                filtered_data = filtered_data[filtered_data['AGE_GROUP'] == age_group_filter]
            
            if filtered_data.empty:
                st.warning("No data matches the selected conditions.")
                return
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_users = filtered_data['USER_COUNT'].sum()
                st.metric("Total Users", f"{total_users:,}")
            with col2:
                total_members = filtered_data['MEMBER_COUNT'].sum()
                st.metric("Total Members", f"{total_members:,}")
            with col3:
                member_ratio = (total_members / total_users * 100) if total_users > 0 else 0
                st.metric("Member Ratio", f"{member_ratio:.1f}%")
            with col4:
                avg_age_group = len(filtered_data['AGE_GROUP'].unique())
                st.metric("Age Groups", f"{avg_age_group}")
            
            # Regional age distribution chart
            if selected_region == "All":
                # All regions - heatmap
                st.subheader("🗺️ Regional Age Group Distribution Heatmap")
                
                pivot_data = filtered_data.pivot(index='ADDR_CODE', columns='AGE_GROUP', values='TOTAL_COUNT').fillna(0)
                
                fig_heatmap = px.imshow(
                    pivot_data,
                    title="Regional Age Group Distribution Heatmap",
                    labels=dict(x="Age Group", y="Region", color="Total Count"),
                    color_continuous_scale='Blues',
                    aspect="auto"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Regional comparison bar chart
                st.subheader("📊 Regional Age Group Comparison")
                
                fig_bar = px.bar(
                    filtered_data,
                    x='ADDR_CODE',
                    y='TOTAL_COUNT',
                    color='AGE_GROUP',
                    title="Regional Age Group Distribution",
                    labels={
                        'ADDR_CODE': 'Region',
                        'TOTAL_COUNT': 'Total Count',
                        'AGE_GROUP': 'Age Group'
                    },
                    barmode='stack'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                # Single region - pie chart
                st.subheader(f"📊 {selected_region} Age Group Distribution")
                
                fig_pie = px.pie(
                    filtered_data,
                    values='TOTAL_COUNT',
                    names='AGE_GROUP',
                    title=f"{selected_region} Age Group Distribution",
                    labels={'TOTAL_COUNT': 'Total Count', 'AGE_GROUP': 'Age Group'}
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Age group bar chart
                fig_bar = px.bar(
                    filtered_data,
                    x='AGE_GROUP',
                    y=['USER_COUNT', 'MEMBER_COUNT'],
                    title=f"{selected_region} Age Group User vs Member Count",
                    labels={
                        'AGE_GROUP': 'Age Group',
                        'value': 'Count',
                        'variable': 'Type'
                    },
                    barmode='group'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Detailed data table
            st.subheader("📋 Detailed Data")
            
            display_data = filtered_data.copy()
            display_data['Member_Ratio(%)'] = (display_data['MEMBER_COUNT'] / display_data['USER_COUNT'] * 100).round(1)
            display_data = display_data[['ADDR_CODE', 'AGE_GROUP', 'USER_COUNT', 'MEMBER_COUNT', 'TOTAL_COUNT', 'Member_Ratio(%)']]
            display_data.columns = ['Region', 'Age Group', 'User Count', 'Member Count', 'Total Count', 'Member Ratio(%)']
            
            st.dataframe(display_data, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading regional age data: {str(e)}")
    
    # Tab 2: Age Group Regional Analysis
    with tab2:
        st.subheader("👥 Age Group Regional Analysis")
        
        try:
            if 'regional_data' not in locals():
                regional_data = load_regional_age_data(schema, brand)
            
            if regional_data.empty:
                st.warning("No data available for age group analysis.")
                return
            
            # Age group selection
            selected_age_group = st.selectbox(
                "Select Age Group for Analysis",
                options=sorted(regional_data['AGE_GROUP'].unique().tolist()),
                index=0,
                key="age_group_analysis"
            )
            
            # Filter data for selected age group
            age_group_data = regional_data[regional_data['AGE_GROUP'] == selected_age_group]
            
            if age_group_data.empty:
                st.warning(f"No data available for age group: {selected_age_group}")
                return
            
            # Display metrics for selected age group
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_users = age_group_data['USER_COUNT'].sum()
                st.metric(f"{selected_age_group} Total Users", f"{total_users:,}")
            with col2:
                total_members = age_group_data['MEMBER_COUNT'].sum()
                st.metric(f"{selected_age_group} Members", f"{total_members:,}")
            with col3:
                member_ratio = (total_members / total_users * 100) if total_users > 0 else 0
                st.metric(f"{selected_age_group} Member Ratio", f"{member_ratio:.1f}%")
            with col4:
                region_count = len(age_group_data)
                st.metric("Regions", f"{region_count}")
            
            # Regional distribution for selected age group
            st.subheader(f"🗺️ {selected_age_group} Regional Distribution")
            
            # Bar chart
            fig_bar = px.bar(
                age_group_data,
                x='ADDR_CODE',
                y='TOTAL_COUNT',
                title=f"{selected_age_group} Regional Distribution",
                labels={
                    'ADDR_CODE': 'Region',
                    'TOTAL_COUNT': 'Total Count'
                },
                color='TOTAL_COUNT',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Regional ranking
            st.subheader(f"📊 {selected_age_group} Regional Ranking")
            
            ranking_data = age_group_data.sort_values('TOTAL_COUNT', ascending=False).copy()
            ranking_data['Rank'] = range(1, len(ranking_data) + 1)
            ranking_data['Share(%)'] = (ranking_data['TOTAL_COUNT'] / ranking_data['TOTAL_COUNT'].sum() * 100).round(1)
            ranking_data = ranking_data[['Rank', 'ADDR_CODE', 'USER_COUNT', 'MEMBER_COUNT', 'TOTAL_COUNT', 'Share(%)']]
            ranking_data.columns = ['Rank', 'Region', 'User Count', 'Member Count', 'Total Count', 'Share(%)']
            
            st.dataframe(ranking_data, use_container_width=True)
            
            # Top 5 regions pie chart
            top5_data = ranking_data.head(5)
            
            fig_pie = px.pie(
                top5_data,
                values='Total Count',
                names='Region',
                title=f"Top 5 Regions for {selected_age_group}",
                labels={'Total Count': 'Total Count', 'Region': 'Region'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error in age group analysis: {str(e)}")
    
    # Tab 3: Trend Analysis
    with tab3:
        st.subheader("📈 Age Group Trend Analysis")
        
        # Load trend data (if available)
        @st.cache_data(ttl=3600)
        def load_trend_data(schema, brand):
            query = f"""
            SELECT 
                ORDER_DATE,
                AGE_GROUP,
                ADDR_CODE,
                ORDER_COUNT,
                USER_COUNT
            FROM COMPANY_DW.{schema}.DT_{brand}_AGE_GROUP_TRENDS
            ORDER BY ORDER_DATE, AGE_GROUP, ADDR_CODE
            """
            return session.sql(query).to_pandas()
        
        try:
            trend_data = load_trend_data(schema, brand)
            
            if trend_data.empty:
                st.info("No trend data available. This feature requires historical trend data.")
                
                # Show static analysis instead
                st.subheader("📊 Age Group Distribution Summary")
                
                if 'regional_data' in locals() and not regional_data.empty:
                    # Age group summary
                    age_summary = regional_data.groupby('AGE_GROUP').agg({
                        'USER_COUNT': 'sum',
                        'MEMBER_COUNT': 'sum',
                        'TOTAL_COUNT': 'sum'
                    }).reset_index()
                    
                    age_summary['Member_Ratio(%)'] = (age_summary['MEMBER_COUNT'] / age_summary['USER_COUNT'] * 100).round(1)
                    age_summary['Share(%)'] = (age_summary['TOTAL_COUNT'] / age_summary['TOTAL_COUNT'].sum() * 100).round(1)
                    
                    # Age group distribution chart
                    fig_age = px.bar(
                        age_summary,
                        x='AGE_GROUP',
                        y='TOTAL_COUNT',
                        title="Overall Age Group Distribution",
                        labels={
                            'AGE_GROUP': 'Age Group',
                            'TOTAL_COUNT': 'Total Count'
                        },
                        color='Member_Ratio(%)',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig_age, use_container_width=True)
                    
                    # Age group summary table
                    display_summary = age_summary.copy()
                    display_summary = display_summary[['AGE_GROUP', 'USER_COUNT', 'MEMBER_COUNT', 'TOTAL_COUNT', 'Member_Ratio(%)', 'Share(%)']]
                    display_summary.columns = ['Age Group', 'User Count', 'Member Count', 'Total Count', 'Member Ratio(%)', 'Share(%)']
                    
                    st.dataframe(display_summary, use_container_width=True)
                return
            
            # Process trend data
            trend_data['ORDER_DATE'] = pd.to_datetime(trend_data['ORDER_DATE'])
            
            # Date range selection
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=trend_data['ORDER_DATE'].min().date(),
                    key="trend_start_date"
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=trend_data['ORDER_DATE'].max().date(),
                    key="trend_end_date"
                )
            
            # Filter trend data
            filtered_trend = trend_data[
                (trend_data['ORDER_DATE'].dt.date >= start_date) &
                (trend_data['ORDER_DATE'].dt.date <= end_date)
            ]
            
            if filtered_trend.empty:
                st.warning("No trend data available for the selected period.")
                return
            
            # Age group trend over time
            st.subheader("📈 Age Group Trend Over Time")
            
            daily_trend = filtered_trend.groupby(['ORDER_DATE', 'AGE_GROUP'])['ORDER_COUNT'].sum().reset_index()
            
            fig_trend = px.line(
                daily_trend,
                x='ORDER_DATE',
                y='ORDER_COUNT',
                color='AGE_GROUP',
                title="Age Group Order Trend Over Time",
                labels={
                    'ORDER_DATE': 'Date',
                    'ORDER_COUNT': 'Order Count',
                    'AGE_GROUP': 'Age Group'
                },
                markers=True
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Regional trend comparison
            st.subheader("🗺️ Regional Age Group Trend Comparison")
            
            # Select regions for comparison
            available_regions = sorted(filtered_trend['ADDR_CODE'].unique())
            selected_regions = st.multiselect(
                "Select Regions for Comparison",
                options=available_regions,
                default=available_regions[:3] if len(available_regions) >= 3 else available_regions,
                key="trend_regions"
            )
            
            if selected_regions:
                regional_trend = filtered_trend[filtered_trend['ADDR_CODE'].isin(selected_regions)]
                regional_daily = regional_trend.groupby(['ORDER_DATE', 'ADDR_CODE'])['ORDER_COUNT'].sum().reset_index()
                
                fig_regional = px.line(
                    regional_daily,
                    x='ORDER_DATE',
                    y='ORDER_COUNT',
                    color='ADDR_CODE',
                    title="Regional Order Trend Comparison",
                    labels={
                        'ORDER_DATE': 'Date',
                        'ORDER_COUNT': 'Order Count',
                        'ADDR_CODE': 'Region'
                    },
                    markers=True
                )
                st.plotly_chart(fig_regional, use_container_width=True)
            
            # Trend summary statistics
            st.subheader("📊 Trend Summary Statistics")
            
            trend_summary = filtered_trend.groupby('AGE_GROUP').agg({
                'ORDER_COUNT': ['sum', 'mean', 'std'],
                'USER_COUNT': 'sum'
            }).reset_index()
            
            trend_summary.columns = ['Age Group', 'Total Orders', 'Avg Daily Orders', 'Std Dev', 'Total Users']
            trend_summary['Orders per User'] = (trend_summary['Total Orders'] / trend_summary['Total Users']).round(2)
            
            st.dataframe(trend_summary, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error in trend analysis: {str(e)}")
    
    # Data download section
    st.divider()
    st.subheader("💾 Data Download")
    
    try:
        if 'regional_data' in locals() and not regional_data.empty:
            csv_data = regional_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"{current_brand['title']} Regional Age Group Data Download",
                data=csv_data,
                file_name=f'{current_brand["short"]}_regional_age_data.csv',
                mime='text/csv'
            )
        else:
            st.warning("No data available for download.")
    except Exception as e:
        st.error(f"Error creating download: {str(e)}")
    
    # Marketing insights
    st.divider()
    
    with st.expander("💡 Marketing Insights and Recommendations", expanded=False):
        st.markdown(f"""
        ### 🎯 Age Group Marketing Strategy
        
        **👶 Young Age Groups (Teens, 20s)**
        - **Digital Marketing**: Social media and mobile app-focused campaigns
        - **Product Strategy**: Trendy, Instagram-worthy products
        - **Pricing**: Competitive pricing with student discounts
        - **Location**: University areas and trendy neighborhoods
        
        **👨‍💼 Middle Age Groups (30s, 40s)**
        - **Quality Focus**: Premium products and service quality
        - **Convenience**: Quick service and online ordering
        - **Family Appeal**: Family-friendly products and promotions
        - **Location**: Business districts and residential areas
        
        **👴 Senior Age Groups (50s+)**
        - **Traditional Marketing**: Traditional media and word-of-mouth
        - **Health Focus**: Healthy and low-sugar options
        - **Service**: Personalized service and loyalty programs
        - **Location**: Residential areas and community centers
        
        ### 📊 Regional Customization Strategy
        
        **🏙️ Urban Areas**
        - Fast-paced service and trendy products
        - Premium pricing and premium experience
        - Extended operating hours
        
        **🏘️ Suburban Areas**
        - Family-friendly atmosphere and products
        - Moderate pricing with family packages
        - Weekend-focused promotions
        
        **🏘️ Rural Areas**
        - Community-focused approach
        - Competitive pricing
        - Local ingredient sourcing
        
        ### 📈 Performance Monitoring
        
        **Key Metrics to Track:**
        - Age group conversion rates
        - Regional age group preferences
        - Age group-specific product performance
        - Regional age group growth trends
        - Member acquisition by age group and region
        """) 