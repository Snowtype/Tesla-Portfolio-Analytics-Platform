import streamlit as st
import plotly.express as px
import pandas as pd

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
    
    st.title(f"{current_brand['title']} Heavy User Segmentation by Menu")

    # Execute data query (brand-specific dynamic table usage)
    @st.cache_data(ttl=3600)  # 1 hour cache
    def load_heavy_user_data(schema, table_prefix):
        query = f"""
            SELECT
                ITEM_NAME,
                AGE_GROUP,
                GENDER,
                ORDER_YMD,
                TOTAL_ORDER_COUNT,
                PERCENTAGE_ORDER_COUNT
            FROM COMPANY_DW.{schema}.{table_prefix}_HEAVY_USER_ANALYSIS_SUMMARY
        """
        return session.sql(query).to_pandas()
    
    try:
        data = load_heavy_user_data(schema, table_prefix)
        
        if data.empty:
            st.warning(f"{current_brand['title']} heavy user analysis data is not available.")
            return
            
    except Exception as e:
        st.error(f"Error occurred while loading {current_brand['title']} heavy user analysis data: {e}")
        return
    
    # Step 1: Convert 'ORDER_YMD' to pandas datetime format, then Korean format -> back to date format
    data['ORDER_YMD'] = pd.to_datetime(data['ORDER_YMD'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
    data['ORDER_YMD'] = pd.to_datetime(data['ORDER_YMD'], format='%Y-%m-%d')
    
    # Date slider/calendar settings
    min_date = data['ORDER_YMD'].min().date()
    max_date = data['ORDER_YMD'].max().date()
    
    # Extract menu list from actual data once (static usage)
    static_menu_list = sorted(data["ITEM_NAME"].unique().tolist())
    
    # Place filters in sidebar (static method like other pages)
    with top_placeholder.container():
        st.subheader(f"{current_brand['title']} Filter Settings")
        
        # Simple date selection method (new_subscribers.py style)
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="heavy_user_start_date"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="heavy_user_end_date"
            )
        
        # Additional filtering (UI) - use static options
        col3, col4 = st.columns(2)
        
        with col3:
            age_group = st.selectbox('Age Group Selection', ['All', 'Teens', '20s', '30s', '40s', '50s'], key="heavy_user_age_group")
        
        with col4:
            gender = st.selectbox('Gender Selection', ['All', 'Male', 'Female'], key="heavy_user_gender")
        
        # Menu selection - use static menu list (like other pages)
        st.subheader(f"{current_brand['title']} Menu Selection")
        
        selected_items = st.multiselect(
            f"Select {current_brand['title']} menu",
            static_menu_list,
            key="heavy_user_menu_selection"
        )

    # Use selected dates directly (no session state modification)
    selected_dates = (start_date, end_date)
    
    # Apply date filter
    filtered_data = data[
        (data['ORDER_YMD'] >= pd.Timestamp(selected_dates[0])) &
        (data['ORDER_YMD'] <= pd.Timestamp(selected_dates[1]))
    ]
    
    # Apply additional filtering - improved more stable method
    if age_group != 'All':
        filtered_data = filtered_data[filtered_data['AGE_GROUP'] == age_group]
    if gender != 'All':
        filtered_data = filtered_data[filtered_data['GENDER'] == gender]

    # Menu list matching current filter
    available_items = filtered_data["ITEM_NAME"].unique()
    
    # Check if selected menus are not in current filter
    invalid_selections = [item for item in selected_items if item not in available_items]
    if invalid_selections:
        st.warning(f"The following selected menus do not match current filter conditions: {', '.join(invalid_selections)}")
    
    # Handle when no data matches filter
    if len(available_items) == 0:
        st.warning(f"{current_brand['title']} No menus match the selected conditions.")
        return
    
    # Display current filtered data dataframe
    st.subheader(f"{current_brand['title']} Heavy User Analysis Data")
    
    # Display filter status (new_subscribers.py style)
    st.write(f"Selected period: {selected_dates[0].strftime('%Y-%m-%d')} ~ {selected_dates[1].strftime('%Y-%m-%d')}")
    if age_group != 'All':
        st.write(f"Age group: {age_group}")
    if gender != 'All':
        st.write(f"Gender: {gender}")
    if selected_items:
        st.write(f"Selected menus: {', '.join(selected_items)}")
    
    st.dataframe(filtered_data, use_container_width=True)
    
    # CSV download
    csv_data_heavy_user = data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{current_brand['title']} Heavy User Full Data Download",
        data=csv_data_heavy_user,
        file_name=f'{current_brand["short"]}_heavy_user_data.csv',
        mime='text/csv'
    )
    
    # Filter data for selected menus
    if selected_items:
        item_data = filtered_data[filtered_data["ITEM_NAME"].isin(selected_items)]
    else:
        item_data = filtered_data.copy()  # Use all data if no menu selected
    
    # Check if data exists
    if item_data.empty:
        st.warning(f"{current_brand['title']} No data matches the selected conditions.")
        return
    
    # Aggregate order quantities by age group and gender
    gender_data = item_data.groupby(['ITEM_NAME', 'GENDER'])['TOTAL_ORDER_COUNT'].sum().reset_index()
    if not gender_data.empty:
        gender_data['PERCENTAGE'] = (gender_data['TOTAL_ORDER_COUNT'] / gender_data.groupby('ITEM_NAME')['TOTAL_ORDER_COUNT'].transform('sum')) * 100
    
    age_data = item_data.groupby(['ITEM_NAME', 'AGE_GROUP'])['TOTAL_ORDER_COUNT'].sum().reset_index()
    if not age_data.empty:
        age_data['PERCENTAGE'] = (age_data['TOTAL_ORDER_COUNT'] / age_data.groupby('ITEM_NAME')['TOTAL_ORDER_COUNT'].transform('sum')) * 100
    
    # Gender graph
    st.subheader(f"{current_brand['title']} Order Quantity by Gender")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not gender_data.empty:
            fig_gender = px.bar(
                gender_data,
                x="ITEM_NAME",
                y="TOTAL_ORDER_COUNT",
                color="GENDER",
                barmode='stack',
                text=gender_data['PERCENTAGE'].round(2).astype(str) + '%',
                title=f"{current_brand['title']} Menu Order Quantity by Gender",
                labels={"TOTAL_ORDER_COUNT": "Order Quantity", "ITEM_NAME": "Menu"}
            )
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.info("No gender data available.")
    
    # Age group graph
    with col2:
        if not age_data.empty:
            fig_age = px.bar(
                age_data,
                x="ITEM_NAME",
                y="TOTAL_ORDER_COUNT",
                color="AGE_GROUP",
                barmode='stack',
                text=age_data['PERCENTAGE'].round(2).astype(str) + '%',
                title=f"{current_brand['title']} Menu Order Quantity by Age Group",
                labels={"TOTAL_ORDER_COUNT": "Order Quantity", "ITEM_NAME": "Menu"}
            )
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("No age group data available.")
    
    # Display selected period
    st.write(f"**{current_brand['title']} Selected period: {selected_dates[0].strftime('%Y-%m-%d')} - {selected_dates[1].strftime('%Y-%m-%d')}**")

    # ========================================
    # 🚀 New Analysis Section: Revenue Correlation Analysis
    # ========================================
    
    st.markdown("---")
    st.subheader(f"🎯 {current_brand['title']} Heavy User Revenue Correlation Analysis")
    
    # 1. Menu average order frequency analysis
    st.markdown("#### 📊 Menu Average Order Frequency")
    order_frequency = item_data.groupby('ITEM_NAME')['TOTAL_ORDER_COUNT'].agg(['mean', 'sum', 'count']).reset_index()
    order_frequency.columns = ['Menu Name', 'Average Order Quantity', 'Total Order Quantity', 'Customer Count']
    order_frequency['Average Orders per Customer'] = order_frequency['Total Order Quantity'] / order_frequency['Customer Count']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average order frequency chart
        fig_frequency = px.bar(
            order_frequency,
            x='Menu Name',
            y='Average Orders per Customer',
            title=f"{current_brand['title']} Menu Average Order Frequency per Customer",
            labels={'Average Orders per Customer': 'Average Order Quantity', 'Menu Name': 'Menu'},
            color='Average Orders per Customer',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_frequency, use_container_width=True)
        st.dataframe(order_frequency, use_container_width=True)
    
    # 2. Age group menu preference analysis
    with col2:
        st.markdown("#### 👥 Age Group Menu Preference Heatmap")
        age_menu_pivot = item_data.groupby(['AGE_GROUP', 'ITEM_NAME'])['TOTAL_ORDER_COUNT'].sum().reset_index()
        age_menu_matrix = age_menu_pivot.pivot(index='AGE_GROUP', columns='ITEM_NAME', values='TOTAL_ORDER_COUNT').fillna(0)
        
        fig_heatmap = px.imshow(
            age_menu_matrix,
            title=f"{current_brand['title']} Age Group Menu Preference Heatmap",
            labels=dict(x="Menu", y="Age Group", color="Order Quantity"),
            aspect="auto",
            color_continuous_scale='YlOrRd'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 3. Gender menu preference analysis
    st.markdown("#### 👫 Gender Menu Preference")
    gender_menu_pivot = item_data.groupby(['GENDER', 'ITEM_NAME'])['TOTAL_ORDER_COUNT'].sum().reset_index()
    gender_menu_matrix = gender_menu_pivot.pivot(index='GENDER', columns='ITEM_NAME', values='TOTAL_ORDER_COUNT').fillna(0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_gender_heatmap = px.imshow(
            gender_menu_matrix,
            title=f"{current_brand['title']} Gender Menu Preference Heatmap",
            labels=dict(x="Menu", y="Gender", color="Order Quantity"),
            aspect="auto",
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_gender_heatmap, use_container_width=True)
    
    # 4. Menu customer segmentation analysis
    with col2:
        st.markdown("#### 🎯 Menu Customer Segmentation")
        
        # Customer segmentation criteria definition
        def categorize_customers(row):
            if row['TOTAL_ORDER_COUNT'] >= 10:
                return 'VIP Customer'
            elif row['TOTAL_ORDER_COUNT'] >= 5:
                return 'Heavy User'
            elif row['TOTAL_ORDER_COUNT'] >= 2:
                return 'Regular Customer'
            else:
                return 'New Customer'
        
        # Customer segmentation application
        item_data_with_category = item_data.copy()
        item_data_with_category['Customer_Segment'] = item_data_with_category.apply(categorize_customers, axis=1)
        
        # Segment distribution
        customer_segments = item_data_with_category.groupby(['ITEM_NAME', 'Customer_Segment']).size().reset_index(name='CustomerCount')
        
        fig_segments = px.bar(
            customer_segments,
            x='ITEM_NAME',
            y='CustomerCount',
            color='Customer_Segment',
            title=f"{current_brand['title']} Menu Customer Segmentation Distribution",
            labels={'CustomerCount': 'Customer Count', 'ITEM_NAME': 'Menu'},
            barmode='stack'
        )
        st.plotly_chart(fig_segments, use_container_width=True)
    
    # 5. Time-based order pattern analysis (date data utilization)
    st.markdown("#### 📅 Time-based Order Pattern")
    
    # Daily order pattern
    daily_orders = item_data.groupby('ORDER_YMD')['TOTAL_ORDER_COUNT'].sum().reset_index()
    daily_orders['DayOfWeek'] = pd.to_datetime(daily_orders['ORDER_YMD']).dt.day_name()
    daily_orders['Month'] = pd.to_datetime(daily_orders['ORDER_YMD']).dt.month
    
    # Daily average order quantity
    weekday_avg = daily_orders.groupby('DayOfWeek')['TOTAL_ORDER_COUNT'].mean().reset_index()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_avg['DayOfWeek'] = pd.Categorical(weekday_avg['DayOfWeek'], categories=weekday_order, ordered=True)
    weekday_avg = weekday_avg.sort_values('DayOfWeek')
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_weekday = px.line(
            weekday_avg,
            x='DayOfWeek',
            y='TOTAL_ORDER_COUNT',
            title=f"{current_brand['title']} Average Order Quantity by Day of Week",
            labels={'TOTAL_ORDER_COUNT': 'Average Order Quantity', 'DayOfWeek': 'Day of Week'},
            markers=True
        )
        st.plotly_chart(fig_weekday, use_container_width=True)
    
    # 6. Menu revenue contribution analysis
    with col2:
        st.markdown("#### 💰 Menu Revenue Contribution Analysis")
        
        # Create virtual revenue data (actual revenue column must exist)
        item_data_with_revenue = item_data.copy()
        # Set virtual price (actual DB must be used)
        menu_prices = {
            'Americano': 4500, 'Cafe Latte': 5000, 'Cappuccino': 5500, 'Espresso': 3500,
            'Vanilla Latte': 6000, 'Caramel Macchiato': 6000, 'Mocha': 6500, 'Affogato': 7000
        }
        
        # Menu price mapping (must be modified to match actual data)
        item_data_with_revenue['Estimated_Unit_Price'] = item_data_with_revenue['ITEM_NAME'].map(
            lambda x: menu_prices.get(x, 5000)  # Default value 5000 won
        )
        item_data_with_revenue['Estimated_Revenue'] = item_data_with_revenue['TOTAL_ORDER_COUNT'] * item_data_with_revenue['Estimated_Unit_Price']
        
        # Menu total revenue
        menu_revenue = item_data_with_revenue.groupby('ITEM_NAME')['Estimated_Revenue'].sum().reset_index()
        menu_revenue['Revenue_Ratio'] = (menu_revenue['Estimated_Revenue'] / menu_revenue['Estimated_Revenue'].sum()) * 100
        
        # Revenue pie chart
        fig_revenue = px.pie(
            menu_revenue,
            values='Estimated_Revenue',
            names='ITEM_NAME',
            title=f"{current_brand['title']} Menu Revenue Contribution",
            labels={'Estimated_Revenue': 'Estimated Revenue (Won)', 'ITEM_NAME': 'Menu'}
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Revenue ranking table
    menu_revenue_sorted = menu_revenue.sort_values('Estimated_Revenue', ascending=False)
    st.markdown("**Menu Revenue Ranking**")
    st.dataframe(menu_revenue_sorted, use_container_width=True)
    
    # 7. Insight and Recommendation
    st.markdown("#### 💡 Insights and Recommendations")
    
    # Top revenue menu
    top_revenue_menu = menu_revenue_sorted.iloc[0]['ITEM_NAME']
    top_frequency_menu = order_frequency.loc[order_frequency['Average Orders per Customer'].idxmax(), 'Menu Name']
    
    # Insight creation
    insights = f"""
    **🔍 Key Insights:**
    
    **1. Top Revenue Menu**: {top_revenue_menu} (contributes {menu_revenue_sorted.iloc[0]['Revenue_Ratio']:.1f}% of total revenue)
    
    **2. High Customer Loyalty Menu**: {top_frequency_menu} (average {order_frequency.loc[order_frequency['Average Orders per Customer'].idxmax(), 'Average Orders per Customer']:.1f} orders per customer)
    
    **3. Customer Segmentation**: VIP customers and heavy users account for {((customer_segments[customer_segments['Customer_Segment'].isin(['VIP Customer', 'Heavy User'])]['CustomerCount'].sum() / customer_segments['CustomerCount'].sum()) * 100):.1f}% of total customers
    
    **📈 Recommended Marketing Strategy:**
    
    • **{top_revenue_menu}** menu promotion enhancement for revenue growth
    • **{top_frequency_menu}** menu customer loyalty program development
    • VIP customer targeted customized service
    • Differentiated marketing strategy by age group/gender
    """
    
    st.markdown(insights)
    
    # 8. Additional analysis data download
    st.markdown("#### 📥 Detailed Analysis Data Download")
    
    # Create comprehensive analysis data
    comprehensive_data = item_data_with_revenue.merge(
        order_frequency, left_on='ITEM_NAME', right_on='Menu Name', how='left'
    )
    
    csv_comprehensive = comprehensive_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{current_brand['title']} Heavy User Detailed Analysis Data Download",
        data=csv_comprehensive,
        file_name=f'{current_brand["short"]}_comprehensive_analysis_{selected_dates[0].strftime("%Y-%m-%d")}_{selected_dates[1].strftime("%Y-%m-%d")}.csv',
        mime='text/csv'
    )

    # ITEM_NAME related logic here, then column name change
    # Current filtered_data contains ITEM_NAME column.
    available_items = filtered_data['ITEM_NAME'].unique().tolist()
    selected_items_after = st.multiselect(
        f'{current_brand["title"]} Item Selection', 
        available_items, 
        default=available_items[:1] if available_items else [], 
        key='menu_selection_2'
    )

    # Column name change
    filtered_data.columns = [
        'Item Name', 
        'Age Group', 
        'Gender', 
        'Order Date', 
        'Total Order Quantity', 
        'Percentage of Orders in the Same Age Group, Gender, and Date'
    ]

    # After column name change, use 'Item Name' column
    if not filtered_data.empty:
        available_items_kor = filtered_data['Item Name'].unique().tolist()
        selected_items_kor = st.multiselect(
            f'{current_brand["title"]} Item Selection(Column Name Changed)', 
            available_items_kor, 
            default=available_items_kor[:1] if available_items_kor else [], 
            key='unique_key_for_this_multiselect'
        )
    else:
        st.warning(f'{current_brand["title"]} No data matches the selected conditions.')

    # CSV download
    csv_data = filtered_data.to_csv(index=False).encode('utf-8')
    
    # CSS for customizing the button's size and color
    st.markdown(f"""
        <style>
        .download-button {{
            background-color: #FF6347;
            color: white;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 10px;
            border: none;
            text-align: center;
            cursor: pointer;
        }}
        .download-button:hover {{
            background-color: #FF4500;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Centering the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.download_button(
            label=f"{current_brand['title']} Selected Data Download",
            data=csv_data,
            file_name=f'{current_brand["short"]}_data_{selected_dates[0].strftime("%Y-%m-%d")}_{selected_dates[1].strftime("%Y-%m-%d")}.csv',
            mime='text/csv',
            key='download-button',
        )

    # Slider style CSS
    slider_css = f"""
    <style>
    div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"] {{
        background-color: #FF6060;  
        box-shadow: #FF6060 0px 0px 0px 0.2rem;  
    }}
    div.stSlider > div[data-baseweb="slider"] > div > div > div > div {{
        color: #FF6060; 
    }}
    div.stSlider > div[data-baseweb="slider"] > div > div {{
        background: 
            linear-gradient(to right, 
            #e0e0e0 0%, 
            #e0e0e0 {{left_percent}}%, 
            #FF6060 {{left_percent}}%, 
            #FF6060 {{right_percent}}%, 
            #e0e0e0 {{right_percent}}%, 
            #e0e0e0 100%);
    }}
    </style>
    """
    st.markdown(slider_css, unsafe_allow_html=True)

    slider_html = f"""
    <div style="width: 100%; margin: 20px 0;">
      <input type="range" min="1" max="100" value="50" class="slider" id="customSlider" style="width: 100%; background: linear-gradient(to right, #FF6060 0%, #FF6060 50%, #e0e0e0 50%, #e0e0e0 100%);">
    </div>
    <script>
      var slider = document.getElementById("customSlider");
      slider.oninput = function() {{
        var value = this.value;
        var gradient = `linear-gradient(to right, #FF6060 0%, #FF6060 ${{value}}%, #e0e0e0 ${{value}}%, #e0e0e0 100%)`;
        this.style.background = gradient;
      }}
    </script>
    """
    st.markdown(slider_html, unsafe_allow_html=True)

    # Below part, selected_dates should be fetched from st.session_state
    # If needed, additional filtering logic should be performed here
    # Below is just an example, if no need to filter again, remove it
    filtered_data_again = data[
        (data['ORDER_YMD'] >= pd.Timestamp(selected_dates[0])) &
        (data['ORDER_YMD'] <= pd.Timestamp(selected_dates[1]))
    ]
    st.write(f"{current_brand['title']} Re-filtered Data (Example):", filtered_data_again)

    # ========================================
    # 🎯 New Analysis Feature: Customer Segmentation + Revenue Simulation
    # ========================================
    st.markdown("---")
    st.subheader(f"🎯 {current_brand['title']} Customer Segment Revenue Contribution Analysis")
    
    # Calculate customer order frequency
    customer_order_freq = filtered_data.groupby(['Age Group', 'Gender'])['Total Order Quantity'].sum().reset_index()
    customer_order_freq['AVG_ORDER_FREQ'] = customer_order_freq['Total Order Quantity'] / len(filtered_data)
    
    # Customer segmentation criteria setting
    freq_75 = customer_order_freq['AVG_ORDER_FREQ'].quantile(0.75)
    freq_50 = customer_order_freq['AVG_ORDER_FREQ'].quantile(0.50)
    
    # Customer segment classification
    def classify_customer_segment(freq):
        if freq >= freq_75:
            return 'VIP Customer'
        elif freq >= freq_50:
            return 'Heavy User'
        else:
            return 'Regular Customer'
    
    customer_order_freq['Customer_Segment'] = customer_order_freq['AVG_ORDER_FREQ'].apply(classify_customer_segment)
    
    # Menu average price information
    menu_prices = {
        'Americano': 4500, 'Cafe Latte': 5000, 'Cappuccino': 5000, 'Espresso': 3500,
        'Vanilla Latte': 5500, 'Caramel Macchiato': 5500, 'Mocha': 5500, 'Affogato': 5500,
        'Iced Americano': 4500, 'Iced Latte': 5000, 'Cold Brew': 5000, 'Iced Latte': 5500,
        'Iced Mocha': 5500, 'Iced Green Tea': 5500, 'Iced Earl Grey': 4500, 'Iced Matcha': 4500,
        'Lemonade': 5500, 'Orangeade': 5500, 'Grapefruitade': 5500, 'Strawberry Smoothie': 6500,
        'Mango Smoothie': 6500, 'Vanilla Ice Cream': 3500, 'Chocolate Ice Cream': 3500, 'Strawberry Ice Cream': 3500
    }
    
    default_price = 5000
    
    # Customer segment revenue simulation
    segment_revenue_data = []
    
    for _, row in customer_order_freq.iterrows():
        segment = row['Customer_Segment']
        age_group = row['Age Group']
        gender = row['Gender']
        order_count = row['Total Order Quantity']
        
        # Calculate average price of menus ordered by the segment
        segment_menus = filtered_data[
            (filtered_data['Age Group'] == age_group) & 
            (filtered_data['Gender'] == gender)
        ]['Item Name'].unique()
        
        if len(segment_menus) > 0:
            avg_price = sum([menu_prices.get(menu, default_price) for menu in segment_menus]) / len(segment_menus)
        else:
            avg_price = default_price
        
        # Calculate estimated revenue
        estimated_revenue = order_count * avg_price
        
        segment_revenue_data.append({
            'Customer_Segment': segment,
            'Age Group': age_group,
            'Gender': gender,
            'Order_Quantity': order_count,
            'Average_Menu_Price': avg_price,
            'Estimated_Revenue': estimated_revenue,
            'Customer_Count': 1
        })
    
    segment_revenue_df = pd.DataFrame(segment_revenue_data)
    
    # Aggregate total revenue by segment
    segment_summary = segment_revenue_df.groupby('Customer_Segment').agg({
        'Order_Quantity': 'sum',
        'Estimated_Revenue': 'sum',
        'Customer_Count': 'sum'
    }).reset_index()
    
    segment_summary['Average_Order_Amount'] = segment_summary['Estimated_Revenue'] / segment_summary['Order_Quantity']
    segment_summary['Revenue_Ratio'] = (segment_summary['Estimated_Revenue'] / segment_summary['Estimated_Revenue'].sum()) * 100
    
    # 1. Customer segment revenue contribution chart
    st.markdown("#### 📊 Customer Segment Revenue Contribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_segment_revenue = px.pie(
            segment_summary,
            values='Estimated_Revenue',
            names='Customer_Segment',
            title=f"{current_brand['title']} Customer Segment Revenue Contribution",
            color_discrete_map={
                'VIP Customer': '#FF6B6B',
                'Heavy User': '#4ECDC4', 
                'Regular Customer': '#45B7D1'
            }
        )
        fig_segment_revenue.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_segment_revenue, use_container_width=True)
    
    # 2. Segment detailed indicators table
    with col2:
        st.markdown("#### 📈 Customer Segment Detailed Indicators")
        
        display_summary = segment_summary.copy()
        display_summary['Estimated_Revenue'] = display_summary['Estimated_Revenue'].apply(lambda x: f"{x:,.0f} Won")
        display_summary['Average_Order_Amount'] = display_summary['Average_Order_Amount'].apply(lambda x: f"{x:,.0f} Won")
        display_summary['Revenue_Ratio'] = display_summary['Revenue_Ratio'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(display_summary, use_container_width=True)
    
    # 3. Age group customer segment distribution heatmap
    st.markdown("#### 🔥 Age Group Customer Segment Distribution Heatmap")
    
    age_segment_pivot = segment_revenue_df.groupby(['Age Group', 'Customer_Segment'])['Estimated_Revenue'].sum().reset_index()
    age_segment_matrix = age_segment_pivot.pivot(index='Age Group', columns='Customer_Segment', values='Estimated_Revenue').fillna(0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_heatmap = px.imshow(
            age_segment_matrix,
            title=f"{current_brand['title']} Age Group Customer Segment Revenue Heatmap",
            color_continuous_scale='Reds',
            aspect='auto'
        )
        fig_heatmap.update_layout(
            xaxis_title="Customer Segment",
            yaxis_title="Age Group"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 4. Segment average order amount comparison
    with col2:
        st.markdown("#### 💰 Customer Segment Average Order Amount Comparison")
        
        fig_avg_order = px.bar(
            segment_summary,
            x='Customer_Segment',
            y='Average_Order_Amount',
            title=f"{current_brand['title']} Customer Segment Average Order Amount",
            color='Customer_Segment',
            color_discrete_map={
                'VIP Customer': '#FF6B6B',
                'Heavy User': '#4ECDC4', 
                'Regular Customer': '#45B7D1'
            }
        )
        fig_avg_order.update_layout(showlegend=False)
        st.plotly_chart(fig_avg_order, use_container_width=True)
    
    # 5. Profitability analysis and marketing insights
    st.markdown("#### 💡 Profitability Analysis and Marketing Insights")
    
    col1, col2, col3 = st.columns(3)
    
    # VIP customer analysis
    with col1:
        vip_data = segment_summary[segment_summary['Customer_Segment'] == 'VIP Customer']
        if not vip_data.empty:
            vip_revenue_ratio = vip_data.iloc[0]['Revenue_Ratio']
            vip_avg_order = vip_data.iloc[0]['Average_Order_Amount']
            
            st.markdown(f"""
            **🎯 VIP Customer Analysis:**
            - Contributes **{vip_revenue_ratio:.1f}%** of total revenue
            - Average Order Amount: **{vip_avg_order:,.0f} Won**
            - **Recommended Strategy**: VIP-specific membership, premium service, personalized marketing
            """)
    
    # Heavy user analysis
    with col2:
        heavy_data = segment_summary[segment_summary['Customer_Segment'] == 'Heavy User']
        if not heavy_data.empty:
            heavy_revenue_ratio = heavy_data.iloc[0]['Revenue_Ratio']
            heavy_avg_order = heavy_data.iloc[0]['Average_Order_Amount']
            
            st.markdown(f"""
            **🔥 Heavy User Analysis:**
            - Contributes **{heavy_revenue_ratio:.1f}%** of total revenue
            - Average Order Amount: **{heavy_avg_order:,.0f} Won**
            - **Recommended Strategy**: Reward program, regular promotion, community building
            """)
    
    # Regular customer analysis
    with col3:
        regular_data = segment_summary[segment_summary['Customer_Segment'] == 'Regular Customer']
        if not regular_data.empty:
            regular_revenue_ratio = regular_data.iloc[0]['Revenue_Ratio']
            regular_avg_order = regular_data.iloc[0]['Average_Order_Amount']
            
            st.markdown(f"""
            **👥 Regular Customer Analysis:**
            - Contributes **{regular_revenue_ratio:.1f}%** of total revenue
            - Average Order Amount: **{regular_avg_order:,.0f} Won**
            - **Recommended Strategy**: New customer acquisition, basic reward, brand awareness enhancement
            """)
    
    # 6. Segment detailed data download
    st.markdown("#### 📥 Customer Segment Detailed Data Download")
    
    csv_segment = segment_revenue_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{current_brand['title']} Customer Segment Detailed Data Download",
        data=csv_segment,
        file_name=f'{current_brand["short"]}_customer_segment_analysis_{selected_dates[0].strftime("%Y-%m-%d")}_{selected_dates[1].strftime("%Y-%m-%d")}.csv',
        mime='text/csv'
    ) 