import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
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
    
    st.title(f"🗺️ {current_brand['title']} Regional Purchase Cycle and Popular Products")
    
    # Description section
    with st.expander("📋 Analysis Description", expanded=False):
        st.markdown(f"""
        **This analysis provides the following insights by region:**
        
        🔍 **Purchase Cycle Analysis**
        - Regional average purchase cycle (in days)
        - Purchase cycle comparison across regions
        - Identification of high/low purchase frequency regions
        
        🛍️ **Popular Products Analysis**
        - Regional TOP 5 popular products
        - Regional customized menu recommendations
        - Regional product preference difference analysis
        
        **Data Source:**
        - `COMPANY_DW.{schema}.DT_{brand}_PURCHASE_INTERVAL_BY_REGION` (purchase cycle)
        - `COMPANY_DW.{schema}.DT_{brand}_TOP_PRODUCTS_BY_REGION` (popular products)
        
        **Usage:**
        - Regional marketing strategy development
        - Revisit cycle prediction and retention campaigns
        - Regional customized menu development and inventory management
        """)
    
    try:
        # 1. Purchase cycle data query
        @st.cache_data(ttl=1800)  # 30 minute cache
        def get_purchase_interval_data(schema, brand):
            interval_query = f"""
            SELECT 
                ADDR_CODE,
                USER_COUNT,
                AVG_PURCHASE_INTERVAL
            FROM COMPANY_DW.{schema}.DT_{brand}_PURCHASE_INTERVAL_BY_REGION
            ORDER BY ADDR_CODE
            """
            return session.sql(interval_query).to_pandas()
        
        # 2. Popular products data query
        @st.cache_data(ttl=1800)  # 30 minute cache
        def get_top_products_data(schema, brand):
            products_query = f"""
            SELECT 
                ADDR_CODE,
                ITEM_NAME,
                ORDER_COUNT
            FROM COMPANY_DW.{schema}.DT_{brand}_TOP_PRODUCTS_BY_REGION
            ORDER BY ADDR_CODE, ORDER_COUNT DESC
            """
            return session.sql(products_query).to_pandas()
        
        # Load data
        interval_data = get_purchase_interval_data(schema, brand)
        products_data = get_top_products_data(schema, brand)
        
        if interval_data.empty and products_data.empty:
            st.warning("No data available. Please check the table.")
            return
        
        # Extract region list (union of both tables)
        regions_from_interval = set(interval_data['ADDR_CODE'].tolist()) if not interval_data.empty else set()
        regions_from_products = set(products_data['ADDR_CODE'].tolist()) if not products_data.empty else set()
        all_regions = sorted(list(regions_from_interval.union(regions_from_products)))
        
        if not all_regions:
            st.warning("No regional data available.")
            return
        
        # Region selection in sidebar
        if top_placeholder:
            with top_placeholder.container():
                st.subheader("🗺️ Region Selection")
                selected_region = st.selectbox(
                    "Select region for analysis:",
                    options=["All"] + all_regions,
                    index=0,
                    key="regional_analysis_region"
                )
                
                if selected_region != "All":
                    st.info(f"Selected region: **{selected_region}**")
        else:
            selected_region = st.selectbox(
                "🗺️ Select region for analysis:",
                options=["All"] + all_regions,
                index=0
            )
        
        # Create tabs
        tab1, tab2 = st.tabs(["📊 Average Purchase Cycle", "🛍️ Popular Products"])
        
        # Tab 1: Average Purchase Cycle
        with tab1:
            if not interval_data.empty:
                st.subheader("📊 Average Purchase Cycle Analysis")
                
                # Data for selected region
                if selected_region != "All":
                    selected_data = interval_data[interval_data['ADDR_CODE'] == selected_region]
                    
                    if not selected_data.empty:
                        # Metrics for selected region
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            avg_interval = selected_data['AVG_PURCHASE_INTERVAL'].iloc[0]
                            st.metric(
                                label="📅 Average Purchase Cycle",
                                value=f"{avg_interval:.1f} days"
                            )
                        
                        with col2:
                            user_count = selected_data['USER_COUNT'].iloc[0]
                            st.metric(
                                label="👥 User Count",
                                value=f"{user_count:,} users"
                            )
                        
                        with col3:
                            # Compare with overall average
                            overall_avg = interval_data['AVG_PURCHASE_INTERVAL'].mean()
                            difference = avg_interval - overall_avg
                            st.metric(
                                label="🔄 vs National Average",
                                value=f"{difference:+.1f} days",
                                delta=f"{'More frequent' if difference < 0 else 'Less frequent'} visits"
                            )
                    else:
                        st.warning(f"No purchase cycle data available for {selected_region} region.")
                
                st.divider()
                
                # Overall regional comparison chart
                st.subheader("🗺️ Overall Regional Average Purchase Cycle Comparison")
                
                # Sort data (purchase cycle ascending)
                sorted_data = interval_data.sort_values('AVG_PURCHASE_INTERVAL')
                
                # Generate colors for selected region highlight
                colors = ['#FF6B6B' if region == selected_region else '#4ECDC4' 
                         for region in sorted_data['ADDR_CODE']]
                
                fig_interval = px.bar(
                    sorted_data,
                    x='ADDR_CODE',
                    y='AVG_PURCHASE_INTERVAL',
                    title=f"{current_brand['title']} Regional Average Purchase Cycle",
                    labels={
                        'ADDR_CODE': 'Region',
                        'AVG_PURCHASE_INTERVAL': 'Average Purchase Cycle (days)'
                    },
                    color_discrete_sequence=colors
                )
                
                fig_interval.update_layout(
                    xaxis_title="Region",
                    yaxis_title="Average Purchase Cycle (days)",
                    xaxis_tickangle=-45,
                    showlegend=False,
                    height=500
                )
                
                # Add average line
                overall_avg = interval_data['AVG_PURCHASE_INTERVAL'].mean()
                fig_interval.add_hline(
                    y=overall_avg, 
                    line_dash="dash", 
                    line_color="red",
                    annotation_text=f"National Average: {overall_avg:.1f} days"
                )
                
                st.plotly_chart(fig_interval, use_container_width=True)
                
                # Regional ranking table
                st.subheader("📊 Regional Purchase Cycle Ranking")
                
                ranking_data = interval_data.sort_values('AVG_PURCHASE_INTERVAL').copy()
                ranking_data['Rank'] = range(1, len(ranking_data) + 1)
                ranking_data['vs_Average'] = ranking_data['AVG_PURCHASE_INTERVAL'] - overall_avg
                ranking_data = ranking_data[['Rank', 'ADDR_CODE', 'AVG_PURCHASE_INTERVAL', 'USER_COUNT', 'vs_Average']]
                ranking_data.columns = ['Rank', 'Region', 'Avg Cycle (days)', 'User Count', 'vs Average']
                ranking_data['vs Average'] = ranking_data['vs Average'].apply(lambda x: f"{x:+.1f} days")
                
                st.dataframe(ranking_data, use_container_width=True)
                
                # Purchase cycle distribution
                st.subheader("📈 Purchase Cycle Distribution")
                
                fig_dist = px.histogram(
                    interval_data,
                    x='AVG_PURCHASE_INTERVAL',
                    nbins=10,
                    title="Purchase Cycle Distribution",
                    labels={
                        'AVG_PURCHASE_INTERVAL': 'Purchase Cycle (days)',
                        'count': 'Number of Regions'
                    }
                )
                
                fig_dist.add_vline(
                    x=overall_avg,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Average: {overall_avg:.1f} days"
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.warning("No purchase cycle data available.")
        
        # Tab 2: Popular Products
        with tab2:
            if not products_data.empty:
                st.subheader("🛍️ Regional Popular Products Analysis")
                
                # Filter data for selected region
                if selected_region != "All":
                    region_products = products_data[products_data['ADDR_CODE'] == selected_region]
                    
                    if not region_products.empty:
                        # TOP 5 products for selected region
                        top5_products = region_products.head(5)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader(f"🏆 {selected_region} TOP 5 Products")
                            
                            # Bar chart
                            fig_top5 = px.bar(
                                top5_products,
                                x='ORDER_COUNT',
                                y='ITEM_NAME',
                                orientation='h',
                                title=f"{selected_region} TOP 5 Popular Products",
                                labels={
                                    'ORDER_COUNT': 'Order Count',
                                    'ITEM_NAME': 'Product Name'
                                },
                                color='ORDER_COUNT',
                                color_continuous_scale='Viridis'
                            )
                            
                            fig_top5.update_layout(
                                yaxis={'categoryorder': 'total ascending'},
                                height=400
                            )
                            
                            st.plotly_chart(fig_top5, use_container_width=True)
                        
                        with col2:
                            # Product details table
                            st.subheader("📋 Product Details")
                            
                            display_data = top5_products.copy()
                            display_data['Rank'] = range(1, len(display_data) + 1)
                            total_orders = display_data['ORDER_COUNT'].sum()
                            display_data['Share(%)'] = (display_data['ORDER_COUNT'] / total_orders * 100).round(1)
                            display_data = display_data[['Rank', 'ITEM_NAME', 'ORDER_COUNT', 'Share(%)']]
                            display_data.columns = ['Rank', 'Product Name', 'Order Count', 'Share(%)']
                            
                            st.dataframe(display_data, use_container_width=True)
                            
                            # Summary metrics
                            st.subheader("📊 Summary")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Orders", f"{total_orders:,}")
                            with col2:
                                top_product = top5_products.iloc[0]
                                st.metric("Top Product", top_product['ITEM_NAME'])
                            with col3:
                                top_share = (top_product['ORDER_COUNT'] / total_orders) * 100
                                st.metric("Top Product Share", f"{top_share:.1f}%")
                    else:
                        st.warning(f"No product data available for {selected_region} region.")
                
                st.divider()
                
                # Regional product comparison
                st.subheader("🗺️ Regional Product Comparison")
                
                # Get TOP 5 products for all regions
                all_top5 = products_data.groupby('ADDR_CODE').head(5)
                
                # Create heatmap for TOP 5 products across regions
                pivot_data = all_top5.pivot(index='ADDR_CODE', columns='ITEM_NAME', values='ORDER_COUNT').fillna(0)
                
                # Select only TOP 10 products across all regions for better visualization
                top_products_all = products_data.groupby('ITEM_NAME')['ORDER_COUNT'].sum().sort_values(ascending=False).head(10).index
                pivot_data_filtered = pivot_data[top_products_all]
                
                fig_heatmap = px.imshow(
                    pivot_data_filtered,
                    title="Regional Product Popularity Heatmap (TOP 10 Products)",
                    labels=dict(x="Product", y="Region", color="Order Count"),
                    color_continuous_scale='Blues',
                    aspect="auto"
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Regional product diversity analysis
                st.subheader("📊 Regional Product Diversity Analysis")
                
                diversity_data = products_data.groupby('ADDR_CODE').agg({
                    'ITEM_NAME': 'nunique',
                    'ORDER_COUNT': 'sum'
                }).reset_index()
                
                diversity_data.columns = ['Region', 'Unique Products', 'Total Orders']
                diversity_data['Avg Orders per Product'] = (diversity_data['Total Orders'] / diversity_data['Unique Products']).round(1)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_diversity = px.bar(
                        diversity_data,
                        x='Region',
                        y='Unique Products',
                        title="Number of Unique Products by Region",
                        labels={
                            'Region': 'Region',
                            'Unique Products': 'Number of Products'
                        }
                    )
                    st.plotly_chart(fig_diversity, use_container_width=True)
                
                with col2:
                    fig_avg = px.bar(
                        diversity_data,
                        x='Region',
                        y='Avg Orders per Product',
                        title="Average Orders per Product by Region",
                        labels={
                            'Region': 'Region',
                            'Avg Orders per Product': 'Average Orders'
                        }
                    )
                    st.plotly_chart(fig_avg, use_container_width=True)
                
                # Diversity table
                st.subheader("📋 Regional Diversity Summary")
                st.dataframe(diversity_data, use_container_width=True)
                
            else:
                st.warning("No product data available.")
        
        # Data download section
        st.divider()
        st.subheader("💾 Data Download")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not interval_data.empty:
                csv_interval = interval_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Purchase Cycle Data",
                    data=csv_interval,
                    file_name=f'{current_brand["short"]}_purchase_cycle_data.csv',
                    mime='text/csv'
                )
        
        with col2:
            if not products_data.empty:
                csv_products = products_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Product Data",
                    data=csv_products,
                    file_name=f'{current_brand["short"]}_product_data.csv',
                    mime='text/csv'
                )
        
        # Marketing insights
        st.divider()
        
        with st.expander("💡 Marketing Insights and Recommendations", expanded=False):
            st.markdown(f"""
            ### 🎯 Regional Marketing Strategy
            
            **📅 Purchase Cycle Optimization**
            - **Short Cycle Regions**: Focus on retention and loyalty programs
            - **Long Cycle Regions**: Implement re-engagement campaigns
            - **Seasonal Patterns**: Adjust marketing timing based on regional cycles
            
            **🛍️ Product Strategy**
            - **Regional Favorites**: Highlight locally popular products
            - **Product Mix**: Optimize inventory based on regional preferences
            - **New Product Launch**: Test in high-diversity regions first
            
            **🗺️ Regional Customization**
            - **Store Layout**: Arrange products based on regional preferences
            - **Promotions**: Customize offers based on purchase cycles
            - **Staff Training**: Focus on popular products in each region
            
            ### 📊 Performance Monitoring
            
            **Key Metrics to Track:**
            - Regional purchase cycle trends
            - Product popularity changes by region
            - Regional customer retention rates
            - Product diversity impact on sales
            - Regional marketing campaign effectiveness
            """)
        
    except Exception as e:
        st.error(f"Error occurred while loading data: {str(e)}")
        st.info("Please check Snowflake connection or table names.")
        
        # Display debugging information
        with st.expander("🔍 Debug Information", expanded=False):
            st.code(f"""
            Schema: {schema}
            Brand: {brand}
            
            Expected Tables:
            - COMPANY_DW.{schema}.DT_{brand}_PURCHASE_INTERVAL_BY_REGION
            - COMPANY_DW.{schema}.DT_{brand}_TOP_PRODUCTS_BY_REGION
            
            Expected Columns:
            Purchase Interval Table:
            - ADDR_CODE (region name)
            - USER_COUNT (number of users)
            - AVG_PURCHASE_INTERVAL (average purchase cycle in days)
            
            Top Products Table:
            - ADDR_CODE (region name)
            - ITEM_NAME (product name)
            - ORDER_COUNT (order count)
            """) 