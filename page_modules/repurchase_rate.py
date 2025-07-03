import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date, timedelta

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
    
    st.title(f"{current_brand['title']} Repurchase Customer Ratio and Order Distribution Analysis (Weekly/Monthly)")

    flg_year_or_not = False

    with top_placeholder.container():
        # Analysis type selection: weekly or monthly
        analysis_type = st.sidebar.selectbox("Analysis Type Selection", ["Weekly", "Monthly"])
    
        if analysis_type == "Weekly":
            # Weekly analysis: calculate ISO year and week after date input
            selected_date = st.sidebar.date_input("Select order date for analysis", date.today())
            selected_date_dt = pd.to_datetime(selected_date)
            year, week, _ = selected_date_dt.isocalendar()
            st.write(f"Selected date: {selected_date_dt.strftime('%Y-%m-%d')}, Year: {year}, Week: {week}")
    
            # Weekly analysis period selection options
            window_option = st.sidebar.radio(
                "Analysis Period Selection",
                ["This Week Only", "2 Weeks (This Week + Previous 1 Week)", "3 Weeks (This Week + Previous 2 Weeks)"]
            )
    
            # Use dynamic tables to query actual aggregated results for 2 or 3 week periods
            if window_option == "This Week Only":
                query = f"""
                SELECT YEAR, WEEK, ORDER_COUNT, USER_COUNT
                FROM COMPANY_DW.{schema}.{table_prefix}_USER_WEEKLY_ORDER_DIST
                WHERE YEAR = {year} AND WEEK = {week}
                ORDER BY ORDER_COUNT
                """
            elif window_option == "2 Weeks (This Week + Previous 1 Week)":
                # Calculate same as dynamic table aggregation (base date: 2000-01-01, 14-day units)
                diff_days = (selected_date_dt - pd.to_datetime('2000-01-01')).days
                mod_val = diff_days % 14
                two_week_start = (selected_date_dt - pd.Timedelta(days=mod_val)).strftime('%Y-%m-%d')
                query = f"""
                SELECT YEAR, PERIOD_START, ORDER_COUNT, USER_COUNT
                FROM COMPANY_DW.{schema}.{table_prefix}_USER_2WEEK_ORDER_DIST
                WHERE PERIOD_START = TO_DATE('{two_week_start}', 'YYYY-MM-DD')
                ORDER BY ORDER_COUNT
                """
            elif window_option == "3 Weeks (This Week + Previous 2 Weeks)":
                # Calculate same as dynamic table aggregation (base date: 2000-01-01, 21-day units)
                diff_days = (selected_date_dt - pd.to_datetime('2000-01-01')).days
                mod_val = diff_days % 21
                three_week_start = (selected_date_dt - pd.Timedelta(days=mod_val)).strftime('%Y-%m-%d')
                query = f"""
                SELECT YEAR, PERIOD_START, ORDER_COUNT, USER_COUNT
                FROM COMPANY_DW.{schema}.{table_prefix}_USER_3WEEK_ORDER_DIST
                WHERE PERIOD_START = TO_DATE('{three_week_start}', 'YYYY-MM-DD')
                ORDER BY ORDER_COUNT
                """
        else:
            flg_year_or_not = True
            
            # Monthly analysis: year and month selection
            sel_year = st.sidebar.number_input("Select year for analysis", min_value=2000, max_value=date.today().year, value=date.today().year)
            month = st.sidebar.selectbox("Select month for analysis", list(range(1, 13)))
            st.write(f"Selected year: {sel_year}, Month: {month}")
    
            query = f"""
            SELECT YEAR, MON, ORDER_COUNT, USER_COUNT
            FROM COMPANY_DW.{schema}.{table_prefix}_USER_MONTHLY_ORDER_DIST
            WHERE YEAR = {sel_year} AND MON = {month}
            ORDER BY ORDER_COUNT
            """

            query_year = f"""
                SELECT MON, ORDER_COUNT, SUM(USER_COUNT) AS TOTAL_USER_COUNT
                FROM COMPANY_DW.{schema}.{table_prefix}_USER_MONTHLY_ORDER_DIST
                WHERE YEAR = {sel_year}
                GROUP BY MON, ORDER_COUNT
                ORDER BY MON, ORDER_COUNT
            """
            data_year = session.sql(query_year).to_pandas()
        
        # Create Snowflake session and query data
        data = session.sql(query).to_pandas()

    if flg_year_or_not is True:
        # Monthly repurchase ratio graph (1, 2, 3 times)
        st.subheader(f"{current_brand['title']} {sel_year} Monthly Repurchase Ratio (1, 2, 3 times)")
        
        # Filter data for order counts 1, 2, 3
        filtered_data_year = data_year[data_year['ORDER_COUNT'].isin([1, 2, 3])]
        
        if not filtered_data_year.empty:
            # Calculate total users per month
            total_users_per_month = data_year.groupby('MON')['TOTAL_USER_COUNT'].sum().reset_index()
            total_users_per_month.rename(columns={'TOTAL_USER_COUNT': 'MONTHLY_TOTAL_USERS'}, inplace=True)
        
            # Combine monthly, order count data and calculate ratios
            filtered_data_year = filtered_data_year.merge(total_users_per_month, on='MON')
            filtered_data_year['RATIO'] = (filtered_data_year['TOTAL_USER_COUNT'] / filtered_data_year['MONTHLY_TOTAL_USERS']) * 100
        
            # Create graph
            fig = px.bar(
                filtered_data_year,
                x='MON',
                y='RATIO',
                color='ORDER_COUNT',
                barmode='group',
                title=f"{current_brand['title']} {sel_year} Monthly Repurchase Ratio (1, 2, 3 times)",
                labels={'MON': 'Month', 'RATIO': 'Ratio (%)', 'ORDER_COUNT': 'Order Count'}
            )
            fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
            fig.update_layout(yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for order counts 1, 2, 3 times.")

    # ---------- Kiosk (Outlier) Data Separation ----------
    # Rows with maximum order count are considered kiosk orders (outliers)
    max_order_count = data['ORDER_COUNT'].max()
    kiosk_data = data[data['ORDER_COUNT'] == max_order_count]
    normal_data = data[data['ORDER_COUNT'] < max_order_count]

    st.subheader(f"{current_brand['title']} Kiosk Order Data (Outliers)")
    if not kiosk_data.empty:
        if analysis_type == "Weekly":
            # For weekly, use WEEK or aggregated period start date (PERIOD_START) based on window_option
            if window_option == "This Week Only":
                kiosk_data = kiosk_data.rename(columns={
                    "YEAR": "Year",
                    "WEEK": "Week",
                    "ORDER_COUNT": "Order Count",
                    "USER_COUNT": "User Count"
                })
            else:
                kiosk_data = kiosk_data.rename(columns={
                    "YEAR": "Year",
                    "PERIOD_START": "Aggregation Period Start",
                    "ORDER_COUNT": "Order Count",
                    "USER_COUNT": "User Count"
                })
        else:
            kiosk_data = kiosk_data.rename(columns={
                "YEAR": "Year",
                "MON": "Month",
                "ORDER_COUNT": "Order Count",
                "USER_COUNT": "User Count"
            })
        st.dataframe(kiosk_data, use_container_width=True)
    else:
        st.info("No kiosk order data available.")

    if normal_data.empty:
        st.warning("No normal order data available after excluding kiosk data.")
    

    # ---------- Repurchase Customer Ratio Calculation ----------
    total_normal_users = normal_data['USER_COUNT'].sum()
    repurchase_normal_users = normal_data.loc[normal_data['ORDER_COUNT'] >= 2, 'USER_COUNT'].sum()
    repurchase_ratio = (repurchase_normal_users / total_normal_users * 100) if total_normal_users > 0 else 0

    st.header(f"{current_brand['title']} Repurchase Customer Ratio")
    st.metric(label="Repurchase Customer Ratio", value=f"{repurchase_ratio:.2f}%")
    st.write(f"Total normal users: {total_normal_users:,}")
    st.write(f"Repurchase (2+ orders) normal users: {repurchase_normal_users:,}")

    # ---------- User Distribution Chart by Order Count ----------
    fig = px.bar(
        normal_data,
        x='ORDER_COUNT',
        y='USER_COUNT',
        text='USER_COUNT',
        title=f"{current_brand['title']} {analysis_type} Order Count Distribution (Excluding Kiosk)",
        labels={'ORDER_COUNT': 'Order Count', 'USER_COUNT': 'User Count'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis=dict(tickformat=","))
    max_order = normal_data['ORDER_COUNT'].max()
    x_range_max = int(max_order * 1.1) if max_order > 0 else 10
    fig.update_layout(xaxis=dict(range=[0, x_range_max]))
    st.plotly_chart(fig, use_container_width=True)

    if analysis_type == "Weekly":
        if window_option == "This Week Only":
            normal_data = normal_data.rename(columns={
                "YEAR": "Year",
                "WEEK": "Week",
                "ORDER_COUNT": "Order Count",
                "USER_COUNT": "User Count"
            })
        else:
            normal_data = normal_data.rename(columns={
                "YEAR": "Year",
                "PERIOD_START": "Aggregation Period Start",
                "ORDER_COUNT": "Order Count",
                "USER_COUNT": "User Count"
            })
    else:
        normal_data = normal_data.rename(columns={
            "YEAR": "Year",
            "MON": "Month",
            "ORDER_COUNT": "Order Count",
            "USER_COUNT": "User Count"
        })
    st.subheader(f"{current_brand['title']} {analysis_type} Order Distribution Data (Excluding Kiosk)")
    st.dataframe(normal_data, use_container_width=True)

    # ---------- Full Data Download Button (Including Date Information) ----------
    st.markdown("---")
    st.subheader(f"{current_brand['title']} Full Data Download and Description")
    if analysis_type == "Weekly":
        st.write(f"""
        **Full Data Structure (for Weekly Analysis)**  
        - **Year**: The year  
        - **Week**: ISO week number or aggregation period start date (for 2-week, 3-week periods)  
        - **Order Count**: Number of orders by user in the period  
        - **User Count**: Number of users with that order count  
        **Note**: Data with maximum order count (kiosk orders) can be viewed separately above.
        """)
        download_query = f"""
        SELECT YEAR, WEEK, ORDER_COUNT, USER_COUNT
        FROM COMPANY_DW.{schema}.{table_prefix}_USER_WEEKLY_ORDER_DIST
        ORDER BY YEAR, WEEK, ORDER_COUNT
        """
    else:
        st.write(f"""
        **Full Data Structure (for Monthly Analysis)**  
        - **Year**: The year  
        - **Month**: The month  
        - **Order Count**: Number of orders by user in the month  
        - **User Count**: Number of users with that order count
        """)
        download_query = f"""
        SELECT YEAR, MON, ORDER_COUNT, USER_COUNT
        FROM COMPANY_DW.{schema}.{table_prefix}_USER_MONTHLY_ORDER_DIST
        ORDER BY YEAR, MON, ORDER_COUNT
        """
    download_data = session.sql(download_query).to_pandas()
    if analysis_type == "Weekly":
        download_data = download_data.rename(columns={
            "YEAR": "Year",
            "WEEK": "Week",
            "ORDER_COUNT": "Order Count",
            "USER_COUNT": "User Count"
        })
    else:
        download_data = download_data.rename(columns={
            "YEAR": "Year",
            "MON": "Month",
            "ORDER_COUNT": "Order Count",
            "USER_COUNT": "User Count"
        })
    csv_data = download_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"{current_brand['title']} Full Data CSV Download",
        data=csv_data,
        file_name=f"{current_brand['short']}_FullData.csv",
        mime="text/csv"
    )

    # ------------------------------------------------------------
    # ---------- Repurchase Metrics Visualization (Same Store/Same Menu) - Store and Order Date Filter Added ----------
    # ---------- Additional: Store and Order Date Repurchase Ratio and TOP 5 Locations Visualization ----------
    # ------------------------------------------------------------

    st.markdown("---")
    st.header(f"{current_brand['title']} Store Menu Repurchase Ratio and TOP 5 Locations")

    # Query repurchase metrics data from dynamic table
    repurchase_query = f"""
    SELECT *
    FROM COMPANY_DW.{schema}.{table_prefix}_REPURCHASE_METRICS
    ORDER BY ORDER_DATE, STORE_NAME, ITEM_ID
    """
    repurchase_df = session.sql(repurchase_query).to_pandas()

    if repurchase_df.empty:
        st.warning("No repurchase metrics data available.")
    else:
        # Convert ORDER_DATE column to datetime format
        repurchase_df['ORDER_DATE'] = pd.to_datetime(repurchase_df['ORDER_DATE'])

        # 1. Place two select boxes in one row (left: date, right: store)
        cols = st.columns(2)
        with cols[0]:
            # Date selection: use maximum order date from data as default
            default_date = repurchase_df['ORDER_DATE'].max().date() - timedelta(days=30) if not repurchase_df.empty else pd.to_datetime(
                "today").date()
            selected_date = st.date_input("Select **Order Date** for analysis", value=default_date)
        with cols[1]:
            # Store selection: use unique store name list
            unique_stores = sorted(repurchase_df['STORE_NAME'].unique())
            selected_store = st.selectbox("Select **Store** for repurchase analysis", unique_stores, key="store_select")

        # Filter data for selected store
        repurchase_store_df = repurchase_df[repurchase_df['STORE_NAME'] == selected_store]

        # 3. TOP 5 locations (stores) from all data for selected order date - based on total order customer count
        date_filtered = repurchase_df[repurchase_df['ORDER_DATE'].dt.date == selected_date]
        top5_stores = date_filtered.groupby("STORE_NAME")["TOTAL_CUSTOMERS"].sum().reset_index()
        top5_stores = top5_stores.sort_values(by="TOTAL_CUSTOMERS", ascending=False).head(5)

        st.subheader(f"{current_brand['title']} TOP 5 Locations with Highest Order Count on {selected_date}")
        st.dataframe(top5_stores, use_container_width=True)

        fig_top5 = px.bar(
            top5_stores,
            x="STORE_NAME",
            y="TOTAL_CUSTOMERS",
            labels={"STORE_NAME": "Store Name", "TOTAL_CUSTOMERS": "Total Order Customer Count"}
        )
        fig_top5.update_layout(
            xaxis_title="Store Name",
            yaxis_title="Total Order Customer Count",
            yaxis_tickformat=","
        )
        st.plotly_chart(fig_top5, use_container_width=True)

        # Filter data for selected store and order date (use .date() for date comparison)
        filtered_repurchase = repurchase_store_df[repurchase_store_df['ORDER_DATE'].dt.date == selected_date]

        st.write(f"### {current_brand['title']} {selected_store} {selected_date} Repurchase Metrics Detailed Data", filtered_repurchase.head())

        # 4. Repurchase ratio line chart by selected order date (Plotly)
        # Group all data by order date and calculate average repurchase ratio
        avg_rates = repurchase_df.groupby("ORDER_DATE").agg({
            "REPURCHASE_RATE_7": "mean",
            "REPURCHASE_RATE_14": "mean",
            "REPURCHASE_RATE_30": "mean"
        }).reset_index()

        # Filter by user-selected calendar date (use .dt.date for comparison since ORDER_DATE is datetime)
        daily_avg_rates = avg_rates[avg_rates["ORDER_DATE"].dt.date == selected_date]

        if daily_avg_rates.empty:
            st.info(f"No repurchase ratio data available for {selected_date}.")
        else:
            # Convert data to long format (melt)
            daily_avg_rates_melt = daily_avg_rates.melt(
                id_vars=["ORDER_DATE"],
                value_vars=["REPURCHASE_RATE_7", "REPURCHASE_RATE_14", "REPURCHASE_RATE_30"],
                var_name="Repurchase Period",
                value_name="Average Repurchase Ratio"
            )
            # Korean labels for repurchase period
            mapping = {
                "REPURCHASE_RATE_7": "Within 7 Days",
                "REPURCHASE_RATE_14": "Within 14 Days",
                "REPURCHASE_RATE_30": "Within 30 Days"
            }
            daily_avg_rates_melt["Repurchase Period"] = daily_avg_rates_melt["Repurchase Period"].map(mapping)

            # Create Plotly line chart (show markers even for single day data)
            fig_bar_daily = px.bar(
                daily_avg_rates_melt,
                x="Repurchase Period",  # x-axis shows repurchase period categories (Within 7 Days, Within 14 Days, Within 30 Days)
                y="Average Repurchase Ratio",
                color="Repurchase Period",
                text="Average Repurchase Ratio",
                title=f"{current_brand['title']} {selected_date} Repurchase Ratio",
                range_y = [0,1]
            )
            fig_bar_daily.update_traces(texttemplate='%{text:.2f}')
            fig_bar_daily.update_layout(
                xaxis_title="Repurchase Period",
                yaxis_title="Average Repurchase Ratio",
                yaxis_tickformat=",.2f"
            )
            st.plotly_chart(fig_bar_daily, use_container_width=True)

        # 4. Bar chart for each menu repurchase ratio by selected store & order date (Plotly)
        # Convert to long format
        filtered_melt = filtered_repurchase.melt(
            id_vars=["ITEM_NAME"],
            value_vars=["REPURCHASE_RATE_7", "REPURCHASE_RATE_14", "REPURCHASE_RATE_30"],
            var_name="Repurchase Period",
            value_name="Repurchase Ratio"
        )
        filtered_melt["Repurchase Period"] = filtered_melt["Repurchase Period"].map(mapping)

        fig_bar = px.bar(
            filtered_melt,
            x="ITEM_NAME",
            y="Repurchase Ratio",
            color="Repurchase Period",
            barmode="group",
            text="Repurchase Ratio",
            title=f"{current_brand['title']} {selected_store} - {selected_date} Menu Repurchase Ratio",
            range_y = [0,1]
        )
        fig_bar.update_layout(
            xaxis_title="Menu Name",
            yaxis_title="Repurchase Ratio",
            yaxis_tickformat=",.2f"
        )
        st.plotly_chart(fig_bar, use_container_width=True) 