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

# Sample data generation function
def get_sample_sales_data():
    """Generate sample sales data by category for portfolio demonstration"""
    categories = [
        "Coffee & Espresso", "Cold Brew & Iced", "Tea & Beverages", 
        "Pastries & Bakery", "Sandwiches & Meals", "Desserts & Sweets"
    ]
    
    months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
              '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12']
    
    data = []
    for month in months:
        for category in categories:
            # Generate realistic sales data with seasonal patterns
            base_sales = np.random.randint(50000, 150000)
            
            # Category-specific multipliers
            if "Coffee" in category:
                category_multiplier = 1.5  # Coffee is most popular
            elif "Cold Brew" in category:
                # Summer boost for cold drinks
                month_num = int(month.split('-')[1])
                category_multiplier = 1.8 if month_num in [6, 7, 8] else 1.0
            elif "Tea" in category:
                category_multiplier = 0.8
            elif "Pastries" in category:
                category_multiplier = 1.2
            elif "Sandwiches" in category:
                category_multiplier = 1.1
            else:  # Desserts
                category_multiplier = 0.9
            
            # Seasonal effects
            month_num = int(month.split('-')[1])
            if month_num in [1, 12]:  # Holiday season
                seasonal_multiplier = 1.3
            elif month_num in [6, 7, 8]:  # Summer
                seasonal_multiplier = 1.2
            else:
                seasonal_multiplier = 1.0
            
            sales = int(base_sales * category_multiplier * seasonal_multiplier * np.random.uniform(0.8, 1.2))
            
            data.append({
                'MONTH': month,
                'CATEGORY': category,
                'SALES_AMOUNT': sales,
                'ORDER_COUNT': int(sales / np.random.randint(8, 15))  # Average order value calculation
            })
    
    return pd.DataFrame(data)

def show_page(session, brand=None, schema=None, role=None):
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
    
    st.title(f"💰 Sales Analytics by Category")
    st.markdown(f"## {current_brand['title']} - Revenue Performance Analysis")
    
    # Get sample data for portfolio
    df_sales = get_sample_sales_data()
    
    # Log data access
    SecurityUtils.log_data_access(
        user=current_user,
        data_type=f"{brand}_SALES_BY_CATEGORY",
        record_count=len(df_sales),
        ip_address=client_ip
    )
    
    # Convert month column to datetime for proper sorting
    df_sales['MONTH_DATE'] = pd.to_datetime(df_sales['MONTH'])
    df_sales['MONTH_DISPLAY'] = df_sales['MONTH_DATE'].dt.strftime('%Y-%m')
    
    # Overall category performance
    st.header("📊 Category Performance Overview")
    
    # Total sales by category
    category_totals = df_sales.groupby('CATEGORY').agg({
        'SALES_AMOUNT': 'sum',
        'ORDER_COUNT': 'sum'
    }).reset_index()
    
    category_totals['AVERAGE_ORDER_VALUE'] = category_totals['SALES_AMOUNT'] / category_totals['ORDER_COUNT']
    category_totals = category_totals.sort_values('SALES_AMOUNT', ascending=False)
    
    # Sales by category bar chart
    fig_category = px.bar(
        category_totals,
        x='CATEGORY',
        y='SALES_AMOUNT',
        title=f"{current_brand['title']} Total Sales by Category",
        labels={'SALES_AMOUNT': 'Total Sales ($)', 'CATEGORY': 'Product Category'},
        color='SALES_AMOUNT',
        color_continuous_scale='Blues'
    )
    fig_category.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_category, use_container_width=True)
    
    # Category distribution pie chart
    fig_pie = px.pie(
        category_totals,
        values='SALES_AMOUNT',
        names='CATEGORY',
        title=f"{current_brand['title']} Sales Distribution by Category",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Monthly trends analysis
    st.header("📈 Monthly Sales Trends")
    
    # Monthly sales trend by category
    monthly_sales = df_sales.groupby(['MONTH_DISPLAY', 'CATEGORY'])['SALES_AMOUNT'].sum().reset_index()
    
    fig_trend = px.line(
        monthly_sales,
        x='MONTH_DISPLAY',
        y='SALES_AMOUNT',
        color='CATEGORY',
        title=f"{current_brand['title']} Monthly Sales Trends by Category",
        labels={'SALES_AMOUNT': 'Sales Amount ($)', 'MONTH_DISPLAY': 'Month'},
        markers=True
    )
    fig_trend.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Performance metrics
    st.header("📋 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = df_sales['SALES_AMOUNT'].sum()
    total_orders = df_sales['ORDER_COUNT'].sum()
    avg_order_value = total_sales / total_orders
    top_category = category_totals.iloc[0]['CATEGORY']
    
    with col1:
        st.metric("Total Sales", f"${total_sales:,.0f}")
    
    with col2:
        st.metric("Total Orders", f"{total_orders:,}")
    
    with col3:
        st.metric("Average Order Value", f"${avg_order_value:.2f}")
    
    with col4:
        st.metric("Top Category", top_category)
    
    # Category performance comparison
    st.header("🔍 Category Performance Comparison")
    
    # Create comparison metrics
    comparison_data = category_totals.copy()
    comparison_data['SALES_PERCENTAGE'] = (comparison_data['SALES_AMOUNT'] / total_sales * 100).round(2)
    comparison_data['ORDER_PERCENTAGE'] = (comparison_data['ORDER_COUNT'] / total_orders * 100).round(2)
    
    # Format for display
    comparison_data['SALES_AMOUNT_FORMATTED'] = comparison_data['SALES_AMOUNT'].apply(lambda x: f"${x:,.0f}")
    comparison_data['AVERAGE_ORDER_VALUE_FORMATTED'] = comparison_data['AVERAGE_ORDER_VALUE'].apply(lambda x: f"${x:.2f}")
    
    # Display comparison table
    display_columns = ['CATEGORY', 'SALES_AMOUNT_FORMATTED', 'SALES_PERCENTAGE', 
                      'ORDER_COUNT', 'ORDER_PERCENTAGE', 'AVERAGE_ORDER_VALUE_FORMATTED']
    
    comparison_display = comparison_data[display_columns].copy()
    comparison_display.columns = ['Category', 'Total Sales', 'Sales %', 'Orders', 'Order %', 'Avg Order Value']
    
    st.dataframe(comparison_display, use_container_width=True)
    
    # Growth analysis
    st.header("📊 Growth Analysis")
    
    # Calculate month-over-month growth
    monthly_totals = df_sales.groupby('MONTH_DISPLAY')['SALES_AMOUNT'].sum().reset_index()
    monthly_totals['MONTH_DATE'] = pd.to_datetime(monthly_totals['MONTH_DISPLAY'])
    monthly_totals = monthly_totals.sort_values('MONTH_DATE')
    monthly_totals['GROWTH_RATE'] = monthly_totals['SALES_AMOUNT'].pct_change() * 100
    
    # Growth rate chart
    fig_growth = px.bar(
        monthly_totals.dropna(),
        x='MONTH_DISPLAY',
        y='GROWTH_RATE',
        title=f"{current_brand['title']} Month-over-Month Growth Rate",
        labels={'GROWTH_RATE': 'Growth Rate (%)', 'MONTH_DISPLAY': 'Month'},
        color='GROWTH_RATE',
        color_continuous_scale='RdYlGn'
    )
    fig_growth.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Business insights
    st.markdown("""
    <div style="background-color: #E8F4FD; padding: 15px; border-radius: 5px;">
    <h4>🎯 Business Insights</h4>
    <ul>
        <li><strong>Top Performer</strong>: Coffee & Espresso drives the highest revenue</li>
        <li><strong>Seasonal Trends</strong>: Cold beverages peak during summer months</li>
        <li><strong>Growth Opportunities</strong>: Food categories show potential for expansion</li>
        <li><strong>Customer Preferences</strong>: High-margin items can be promoted more effectively</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Advanced analytics section
    st.header("🔬 Advanced Analytics")
    
    # Category selection for detailed analysis
    selected_category = st.selectbox(
        "Select Category for Detailed Analysis",
        options=category_totals['CATEGORY'].tolist()
    )
    
    if selected_category:
        category_data = df_sales[df_sales['CATEGORY'] == selected_category]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly performance for selected category
            monthly_category = category_data.groupby('MONTH_DISPLAY')['SALES_AMOUNT'].sum().reset_index()
            
            fig_category_trend = px.line(
                monthly_category,
                x='MONTH_DISPLAY',
                y='SALES_AMOUNT',
                title=f"{selected_category} - Monthly Sales Trend",
                markers=True
            )
            fig_category_trend.update_traces(line_color='#ff7f0e', line_width=3)
            st.plotly_chart(fig_category_trend, use_container_width=True)
        
        with col2:
            # Category metrics
            category_total = category_data['SALES_AMOUNT'].sum()
            category_orders = category_data['ORDER_COUNT'].sum()
            category_aov = category_total / category_orders
            
            st.markdown(f"### {selected_category} Metrics")
            st.metric("Category Sales", f"${category_total:,.0f}")
            st.metric("Category Orders", f"{category_orders:,}")
            st.metric("Category AOV", f"${category_aov:.2f}")
            
            # Calculate category performance vs average
            avg_sales = df_sales.groupby('CATEGORY')['SALES_AMOUNT'].sum().mean()
            performance_vs_avg = ((category_total - avg_sales) / avg_sales * 100)
            
            if performance_vs_avg > 0:
                st.success(f"📈 {performance_vs_avg:.1f}% above average")
            else:
                st.info(f"📉 {abs(performance_vs_avg):.1f}% below average")
    
    # Data export section
    st.markdown("---")
    st.subheader("📥 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Category Summary"):
            csv = comparison_display.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{brand}_category_summary.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Monthly Data"):
            csv = monthly_sales.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{brand}_monthly_sales.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Download Full Dataset"):
            csv = df_sales.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{brand}_sales_full_data.csv",
                mime="text/csv"
            )
    
    # Portfolio note
    st.markdown("""
    ---
    **📝 Portfolio Note**: This sales analysis uses sample data demonstrating category performance tracking. 
    In production, this would connect to real POS systems and provide actionable insights for revenue optimization.
    """) 