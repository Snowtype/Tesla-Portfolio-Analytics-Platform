# Tesla Coffee & RoboBrew Analytics Dashboard

This project is a Streamlit-based dashboard for analyzing customer data from Tesla Coffee and RoboBrew Coffee chains.

## Key Features

### 1. User Segments and MAU

- Tesla Coffee and RoboBrew member/non-member user analysis
- Monthly MAU (Monthly Active Users) trends
- User segment status (SHADOW, BLACK, BLUE, GREEN, RED, OTHER)
- RFM segment distribution
- Cohort retention trends

### 2. Daily New Member Registration

- Daily/weekly/monthly new member trends
- Age group distribution of new members
- Registration type analysis (Apple, Kakao, Phone number, etc.)

### 3. Regional/Age Data

- Regional sales analysis
- Period filtering functionality

### 4. Repurchase Customer Ratio

- Weekly/monthly repurchase analysis
- Kiosk order data separation
- Store-specific menu repurchase ratios
- TOP 5 location analysis

## Installation and Setup

### 1. Environment Setup

```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Snowflake Connection Setup

#### Method 1: Using Streamlit Secrets (Recommended)

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Enter actual connection information in `.streamlit/secrets.toml`

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Example `.streamlit/secrets.toml` file:

```toml
[snowflake]
account = "your_account.region"
user = "your_username"
password = "your_password"
warehouse = "your_warehouse"
database = "your_database"
schema = "your_schema"
role = "ACCOUNTADMIN"
```

#### Method 2: Private Key Authentication (More Secure)

```toml
[snowflake]
account = "your_account.region"
user = "your_username"
private_key_path = "/path/to/your/private_key.p8"
warehouse = "your_warehouse"
database = "your_database"
schema = "your_schema"
role = "ACCOUNTADMIN"
```

#### Method 3: Using Environment Variables

```bash
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_username"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_WAREHOUSE="your_warehouse"
export SNOWFLAKE_DATABASE="your_database"
export SNOWFLAKE_SCHEMA="your_schema"
```

### 3. Application Execution

```bash
streamlit run app.py
```

### 4. Connection Test

```bash
python snowflake_connection.py
```

## Database Schema

This application uses dynamic table naming with the following Snowflake table patterns:

- `COMPANY_DW.{schema}.DT_{brand}_USER_COUNTS`
- `COMPANY_DW.{schema}.DT_{brand}_MAU_USERS`
- `COMPANY_DW.{schema}.DT_{brand}_USER_SEGMENTS`
- `COMPANY_DW.{schema}.DT_{brand}_USER_RFM_SEGMENTS`
- `COMPANY_DW.{schema}.DT_{brand}_USER_COHORT_RETENTION`
- `COMPANY_DW.{schema}.DT_{brand}_NEW_MEMBERS`
- `COMPANY_DW.{schema}.DT_{brand}_AGE_GROUP_MEMBERS`
- `COMPANY_DW.{schema}.DT_{brand}_AGE_GROUP_USERS`
- `COMPANY_DW.{schema}.DT_{brand}_REGION_SALES_DYN`
- `COMPANY_DW.{schema}.DT_{brand}_USER_WEEKLY_ORDER_DIST`
- `COMPANY_DW.{schema}.DT_{brand}_USER_MONTHLY_ORDER_DIST`
- `COMPANY_DW.{schema}.DT_{brand}_REPURCHASE_METRICS`

Where:

- `{schema}` = ANALYSIS_TPC (Tesla Coffee) or ANALYSIS_MMC (RoboBrew Coffee)
- `{brand}` = TPC (Tesla Coffee) or MMC (RoboBrew Coffee)

## Project Structure

```
TESLA_TPC_STREAMLIT/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python package dependencies
├── README.md                # Project documentation
├── snowflake_connection.py  # Snowflake connection module
├── .streamlit/              # Streamlit configuration directory
│   ├── config.toml         # Streamlit app configuration
│   ├── secrets.toml        # Snowflake connection info (user created)
│   └── secrets.toml.example # Connection info example
└── .gitignore              # Git exclude file list
```

## Streamlit Configuration

You can customize the app's theme and server settings in the `.streamlit/config.toml` file:

```toml
[theme]
primaryColor = "#B8865B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F0F0"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
address = "localhost"
```

## Usage

1. When you run the application, the "User Segments and MAU" page is displayed by default.
2. You can select the desired analysis page from the sidebar.
3. Each page provides interactive features such as period selection and filtering.
4. Charts and data are queried in real-time from the Snowflake database.

## Security Considerations

- The `.streamlit/secrets.toml` file contains sensitive information and is added to `.gitignore`.
- Use Private Key authentication when possible.
- Environment variables are recommended for production environments.
- When using Streamlit Cloud, you can set secrets directly in the web dashboard.

## Important Notes

- Snowflake connection is required.
- Database access permissions are necessary.
- Large data queries may affect performance.

## Technical Stack

- **Frontend**: Streamlit
- **Data Visualization**: Plotly, Matplotlib, Seaborn
- **Data Processing**: Pandas, NumPy
- **Database**: Snowflake (Snowpark)
- **Date Handling**: python-dateutil
- **Configuration**: TOML
