import streamlit as st
import plotly.express as px
import pandas as pd

def show_page(session, top_placeholder, month_options, brand=None, schema=None, role=None):
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
    
    st.title(f"{current_brand['title']} Heavy User Analysis")

    # # Header for the page
    # st.header(f"{current_brand['title']} Heavy User Order Analysis")

    # Cache menu list to avoid querying every time
    @st.cache_data(ttl=3600)  # 1 hour cache
    def get_menu_list(schema, table_prefix):
        menu_query = f"""
        SELECT DISTINCT ITEM_NAME 
        FROM COMPANY_DW.{schema}.{table_prefix}_HEAVY_USER_ANALYSIS_SUMMARY
        ORDER BY ITEM_NAME
        """
        menu_data = session.sql(menu_query).to_pandas()
        return menu_data['ITEM_NAME'].tolist()
    
    menu_list = get_menu_list(schema, table_prefix)

    # Initialize session state (execute only once)
    if 'heavy_user_filters' not in st.session_state:
        st.session_state.heavy_user_filters = {
            'year_from': 2024,
            'month_from': list(month_options.values())[0],
            'year_to': 2024,
            'month_to': list(month_options.values())[-1],
            'age_group': 'All',
            'gender': 'All',
            'menu': []  # Initialize as empty list
        }

    with top_placeholder.container():
        # Allow the user to choose a date range on the same page
        # Top 2 columns: start year/month
        col1, col2 = st.columns(2)
        
        with col1:
            year_from = st.selectbox(
                "Start Year", 
                [2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030], 
                key="heavy_user_year_from",
                index=0 if st.session_state.heavy_user_filters['year_from'] == 2024 else 0
            )
        
        with col2:
            month_from = st.selectbox(
                "Start Month", 
                list(month_options.values()), 
                key="heavy_user_month_from",
                index=list(month_options.values()).index(st.session_state.heavy_user_filters['month_from'])
            )
        
        # Bottom 2 columns: end year/month
        col3, col4 = st.columns(2)
        
        with col3:
            year_to = st.selectbox(
                "End Year", 
                [2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030], 
                key="heavy_user_year_to",
                index=0 if st.session_state.heavy_user_filters['year_to'] == 2024 else 0
            )
        
        with col4:
            month_to = st.selectbox(
                "End Month", 
                list(month_options.values()), 
                key="heavy_user_month_to",
                index=list(month_options.values()).index(st.session_state.heavy_user_filters['month_to'])
            )
        
        # Additional filters: age group, gender
        col5, col6 = st.columns(2)
        
        with col5:
            age_group = st.selectbox(
                'Age Group Selection', 
                ['All', 'Teens', '20s', '30s', '40s', '50s'], 
                key="heavy_user_age_group",
                index=['All', 'Teens', '20s', '30s', '40s', '50s'].index(st.session_state.heavy_user_filters['age_group'])
            )
        
        with col6:
            gender = st.selectbox(
                'Gender Selection', 
                ['All', 'Male', 'Female'], 
                key="heavy_user_gender",
                index=['All', 'Male', 'Female'].index(st.session_state.heavy_user_filters['gender'])
            )
        
        # Menu selection
        selected_menus = st.multiselect(
            'Menu Selection (Multiple selections possible)', 
            menu_list, 
            default=[],
            key="heavy_user_menu"
        )
        
        # Save filter values to session state
        st.session_state.heavy_user_filters.update({
            'year_from': year_from,
            'month_from': month_from,
            'year_to': year_to,
            'month_to': month_to,
            'age_group': age_group,
            'gender': gender,
            'menu': selected_menus  # Save selected menu list
        })
        
        st.write(f"Selected period: {year_from} {month_from} ~ {year_to} {month_to}")
        if age_group != 'All':
            st.write(f"Age group: {age_group}")
        if gender != 'All':
            st.write(f"Gender: {gender}")
        if selected_menus:
            st.write(f"Selected menus: {', '.join(selected_menus)}")
        else:
            st.write("Selected menus: All")

    # Extract the selected month key (e.g., '01', '10') from the dictionary
    month_from_key = [key for key, value in month_options.items() if value == month_from][0]
    month_to_key = [key for key, value in month_options.items() if value == month_to][0]
    
    # Weekday order setting
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # 1. Heavy user order data (include filter conditions in query)
    # Basic query conditions
    where_conditions = []
    
    # Date conditions
    date_from = f"{year_from}{month_from_key}01"
    date_to = f"{year_to}{month_to_key}31"
    where_conditions.append(f"ORDER_YMD BETWEEN '{date_from}' AND '{date_to}'")
    
    # Age group conditions
    if age_group != 'All':
        where_conditions.append(f"AGE_GROUP = '{age_group}'")
    
    # Gender conditions
    if gender != 'All':
        where_conditions.append(f"GENDER = '{gender}'")
    
    # Menu conditions
    if selected_menus:
        menu_list_str = "', '".join(selected_menus)
        where_conditions.append(f"ITEM_NAME IN ('{menu_list_str}')")
    
    # WHERE clause composition
    where_clause = " AND ".join(where_conditions)
    
    # Cache data query to improve performance
    @st.cache_data(ttl=1800)  # 30 minute cache
    def get_heavy_users_data(schema, table_prefix, where_clause):
        heavy_users_query = f"""
        SELECT * FROM COMPANY_DW.{schema}.{table_prefix}_HEAVY_USER_ANALYSIS_SUMMARY
        WHERE {where_clause}
        """
        return session.sql(heavy_users_query).to_pandas()
    
    heavy_users_data = get_heavy_users_data(schema, table_prefix, where_clause)
    
    # Convert ORDER_YMD to 'YYYY-MM' format and create new column for sorting
    heavy_users_data['ORDER_YMD'] = pd.to_datetime(heavy_users_data['ORDER_YMD'], format='%Y%m%d')
    heavy_users_data['ORDER_MONTH_STR'] = heavy_users_data['ORDER_YMD'].dt.strftime('%Y-%m')
    
    # Extract weekday in English and map to English
    weekday_mapping = {
        "Monday": "Monday", "Tuesday": "Tuesday", "Wednesday": "Wednesday", 
        "Thursday": "Thursday", "Friday": "Friday", "Saturday": "Saturday", "Sunday": "Sunday"
    }
    heavy_users_data['ORDER_WEEKDAY'] = heavy_users_data['ORDER_YMD'].dt.day_name().map(weekday_mapping)
    
    # Streamlit Header
    st.header(f"{current_brand['title']} Heavy User Order Count (Monthly/Daily/Daily)")
    
    # Create placeholders for chart and dataframe
    chart_placeholder1 = st.empty()
    df_placeholder1 = st.empty()
    
    # Create daily/weekday heavy user order count graph
    heavy_users_data['ORDER_WEEKDAY'] = pd.Categorical(heavy_users_data['ORDER_WEEKDAY'], categories=weekday_order, ordered=True)
    
    weekday_color_map = {
        "Monday": "tomato",
        "Tuesday": "orange",
        "Wednesday": "gold",
        "Thursday": "limegreen",
        "Friday": "dodgerblue",
        "Saturday": "purple",
        "Sunday": "pink"
    }
    heavy_users_chart = px.bar(
        heavy_users_data, 
        x='ORDER_YMD',                  # Show daily order count on x-axis
        y='TOTAL_ORDER_COUNT', 
        color='ORDER_WEEKDAY', 
        title=f"{current_brand['title']} Daily/Weekday Heavy User Order Count",
        labels={"ORDER_WEEKDAY": "Weekday", "TOTAL_ORDER_COUNT": "Order Count", "ORDER_YMD": "Order Date"},
        category_orders={"ORDER_WEEKDAY": weekday_order},  # Fixed weekday order
        color_discrete_map=weekday_color_map  # Apply rainbow color mapping
    )
    
    chart_placeholder1.plotly_chart(heavy_users_chart, use_container_width=True)
    df_placeholder1.dataframe(heavy_users_data, use_container_width=True)

    # (1) First, group heavy_users_data by month+weekday and sum
    monthly_weekday_df = (
        heavy_users_data
        .groupby(['ORDER_MONTH_STR', 'ORDER_WEEKDAY'], as_index=False)['TOTAL_ORDER_COUNT']
        .sum()
    )

    monthly_chart = px.bar(
        monthly_weekday_df, 
        x='ORDER_MONTH_STR', 
        y='TOTAL_ORDER_COUNT', 
        color='ORDER_WEEKDAY', 
        title=f"{current_brand['title']} Monthly/Weekday Heavy User Order Count",
        labels={"ORDER_WEEKDAY": "Weekday", "TOTAL_ORDER_COUNT": "Order Count", "ORDER_MONTH_STR": "Month"},
        color_discrete_map=weekday_color_map,  # (A) Hardcoded weekday color
        category_orders={
            "ORDER_WEEKDAY": weekday_order, 
            "ORDER_MONTH_STR": sorted(monthly_weekday_df['ORDER_MONTH_STR'].unique())
        },
        text='TOTAL_ORDER_COUNT'  # Data column to display above bars
    )
    
    # (3) Monthly total (= sum of all weekdays) -> Annotation at top of graph
    monthly_sums = monthly_weekday_df.groupby('ORDER_MONTH_STR')['TOTAL_ORDER_COUNT'].sum()
    
    for month_str, total_value in monthly_sums.items():
        monthly_chart.add_annotation(
            x=month_str,
            y=total_value,
            text=f"{int(total_value):,}",   # Example: Thousands comma
            showarrow=False,               # Show arrow X
            xanchor='center',
            yanchor='bottom',
            yshift=5                       # Slightly above bar top
        )
    # (4) Set data count to be inside graph
    monthly_chart.update_traces(textposition='inside')
    monthly_chart.update_layout(
        yaxis=dict(tickformat=",") # Use comma for thousands
    )
    
    # Create placeholders for monthly chart and dataframe
    chart_placeholder2 = st.empty()
    df_placeholder2 = st.empty()
    
    chart_placeholder2.plotly_chart(monthly_chart, use_container_width=True)
    df_placeholder2.dataframe(monthly_weekday_df, use_container_width=True)
    
    # Hardcoded weekday totals
    weekday_totals = {
        "Monday": heavy_users_data[heavy_users_data['ORDER_WEEKDAY'] == "Monday"]['TOTAL_ORDER_COUNT'].sum(),
        "Tuesday": heavy_users_data[heavy_users_data['ORDER_WEEKDAY'] == "Tuesday"]['TOTAL_ORDER_COUNT'].sum(),
        "Wednesday": heavy_users_data[heavy_users_data['ORDER_WEEKDAY'] == "Wednesday"]['TOTAL_ORDER_COUNT'].sum(),
        "Thursday": heavy_users_data[heavy_users_data['ORDER_WEEKDAY'] == "Thursday"]['TOTAL_ORDER_COUNT'].sum(),
        "Friday": heavy_users_data[heavy_users_data['ORDER_WEEKDAY'] == "Friday"]['TOTAL_ORDER_COUNT'].sum(),
        "Saturday": heavy_users_data[heavy_users_data['ORDER_WEEKDAY'] == "Saturday"]['TOTAL_ORDER_COUNT'].sum(),
        "Sunday": heavy_users_data[heavy_users_data['ORDER_WEEKDAY'] == "Sunday"]['TOTAL_ORDER_COUNT'].sum()
    }
    
    weekday_summary_df = pd.DataFrame(list(weekday_totals.items()), columns=['ORDER_WEEKDAY', 'TOTAL_ORDER_COUNT'])

    # (1) Sum "weekday" over entire period
    total_weekday_df = (
        heavy_users_data
        .groupby('ORDER_WEEKDAY', as_index=False)['TOTAL_ORDER_COUNT']
        .sum()
    )

    # (2) Create graph
    weekday_chart = px.bar(
        total_weekday_df,
        x='ORDER_WEEKDAY',
        y='TOTAL_ORDER_COUNT',
        color='ORDER_WEEKDAY',
        text='TOTAL_ORDER_COUNT',
        title=f"{current_brand['title']} Total Period Weekday Heavy User Order Count Sum",
        labels={"ORDER_WEEKDAY": "Weekday", "TOTAL_ORDER_COUNT": "Order Count"},
        color_discrete_map=weekday_color_map,
        category_orders={"ORDER_WEEKDAY": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]}
    )
    weekday_chart.update_traces(textposition='outside')
    weekday_chart.update_layout(
        yaxis=dict(tickformat=",")
    )
    
    # Create placeholders for weekday chart and dataframe
    chart_placeholder3 = st.empty()
    df_placeholder3 = st.empty()
    
    chart_placeholder3.plotly_chart(weekday_chart, use_container_width=True)
    df_placeholder3.dataframe(total_weekday_df, use_container_width=True)

    # Age group heavy user order count
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # Format the selected dates into YYYYMM format
    date_from = f"{year_from}{month_from_key}"
    date_to = f"{year_to}{month_to_key}"
    
    st.write(f"Selected period: {date_from} ~ {date_to}")
    
    # Query to fetch data dynamically based on selected date range
    age_group_where_conditions = []
    age_group_where_conditions.append(f"ORDER_YMD BETWEEN '{date_from}01' AND '{date_to}31'")
    
    if age_group != 'All':
        age_group_where_conditions.append(f"AGE_GROUP = '{age_group}'")
    if gender != 'All':
        age_group_where_conditions.append(f"GENDER = '{gender}'")
    if selected_menus:
        menu_list_str = "', '".join(selected_menus)
        age_group_where_conditions.append(f"ITEM_NAME IN ('{menu_list_str}')")
    
    age_group_where_clause = " AND ".join(age_group_where_conditions)
    
    # Cache age group data query to improve performance
    @st.cache_data(ttl=1800)  # 30 minute cache
    def get_age_group_heavy_users_data(schema, table_prefix, age_group_where_clause):
        age_group_heavy_users_query = f"""
        SELECT * FROM COMPANY_DW.{schema}.{table_prefix}_HEAVY_USER_ANALYSIS_SUMMARY
        WHERE {age_group_where_clause}
        """
        return session.sql(age_group_heavy_users_query).to_pandas()
    
    age_group_heavy_users_data = get_age_group_heavy_users_data(schema, table_prefix, age_group_where_clause)
    
    aggregated_age_group_heavy_users_data = age_group_heavy_users_data.groupby('AGE_GROUP', as_index=False)['TOTAL_ORDER_COUNT'].sum()
    # Plotly Bar Chart creation (age group)
    age_group_chart = px.bar(
        aggregated_age_group_heavy_users_data,
        x='AGE_GROUP',
        y='TOTAL_ORDER_COUNT',
        color='AGE_GROUP',
        text='TOTAL_ORDER_COUNT',  # Show number above bar
        title=f"{current_brand['title']} Age Group Heavy User Order Count",
        labels={"AGE_GROUP": "Age Group", "TOTAL_ORDER_COUNT": "Order Count"},
        category_orders={"AGE_GROUP": ["Teens","20s","30s","40s","50s"]}
    )
    
    # Set number to be shown above bar
    age_group_chart.update_traces(textposition='outside')
    age_group_chart.update_layout(
        yaxis=dict(tickformat=",")  # Thousands comma
    )
    
    # Create placeholders for age group chart and dataframe
    chart_placeholder4 = st.empty()
    df_placeholder4 = st.empty()
    
    # Display the chart on the page
    chart_placeholder4.plotly_chart(age_group_chart, use_container_width=True)
    df_placeholder4.dataframe(age_group_heavy_users_data, use_container_width=True)

    # space = st.empty()
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    # Add empty space (increase spacing)
    space1 = st.empty()
    space1.write("\n")  # Alternatively, you can add multiple lines to increase spacing

    # Header for the page
    st.header(f"{current_brand['title']} Gender Heavy User Order Count")

    # Format the selected dates into YYYYMM format
    date_from = f"{year_from}{month_from_key}"
    date_to = f"{year_to}{month_to_key}"
    
    st.write(f"Selected period: {date_from} ~ {date_to}")
    
    # Query to fetch data dynamically based on selected date range
    gender_where_conditions = []
    gender_where_conditions.append(f"ORDER_YMD BETWEEN '{date_from}01' AND '{date_to}31'")
    
    if age_group != 'All':
        gender_where_conditions.append(f"AGE_GROUP = '{age_group}'")
    if gender != 'All':
        gender_where_conditions.append(f"GENDER = '{gender}'")
    if selected_menus:
        menu_list_str = "', '".join(selected_menus)
        gender_where_conditions.append(f"ITEM_NAME IN ('{menu_list_str}')")
    
    gender_where_clause = " AND ".join(gender_where_conditions)
    
    # Cache gender data query to improve performance
    @st.cache_data(ttl=1800)  # 30 minute cache
    def get_gender_heavy_users_data(schema, table_prefix, gender_where_clause):
        gender_heavy_users_query = f"""
        SELECT * FROM COMPANY_DW.{schema}.{table_prefix}_HEAVY_USER_ANALYSIS_SUMMARY
        WHERE {gender_where_clause}
        ORDER BY GENDER
        """
        return session.sql(gender_heavy_users_query).to_pandas()
    
    gender_heavy_users_data = get_gender_heavy_users_data(schema, table_prefix, gender_where_clause)
    
    # 1) Sum data split by month by GENDER
    gender_agg_data = (
    gender_heavy_users_data
        .groupby('GENDER', as_index=False)['TOTAL_ORDER_COUNT']
        .sum()
    )

    # Plotly Bar Chart creation (gender)
    gender_chart = px.bar(
        gender_agg_data,
        x='GENDER',
        y='TOTAL_ORDER_COUNT',
        color='GENDER',
        title=f"{current_brand['title']} Gender Heavy User Order Count",
        labels={"GENDER": "Gender", "TOTAL_ORDER_COUNT": "Order Count"},
        color_discrete_map={
            'Male': 'blue',
            'Female': 'pink',
        },
        barmode='group',
        category_orders={
        "GENDER": ["Male", "Female"]
        }
    )

    # Axis(Label) Format change
    gender_chart.update_layout(
        yaxis=dict(
            tickformat=",",    # Thousands comma (e.g., 1,000 / 10,000)
        )
    )

    # Create placeholders for gender chart and dataframe
    chart_placeholder5 = st.empty()
    df_placeholder5 = st.empty()

    # Display the chart on the page
    chart_placeholder5.plotly_chart(gender_chart, use_container_width=True)
    df_placeholder5.dataframe(gender_heavy_users_data, use_container_width=True) 