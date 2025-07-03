# Brand configuration for Tesla Portfolio Analytics Platform
# Portfolio demonstration version with masked brand information

# Brand schema mapping for multi-tenant architecture
BRAND_SCHEMA = {
    "BRAND_A": "ANALYSIS_BRAND_A",  # Coffee Brand A (formerly TPC)
    "BRAND_B": "ANALYSIS_BRAND_B",  # Coffee Brand B (formerly MMC)
}

# Brand-specific text and display information
BRAND_TEXTS = {
    "BRAND_A": {
        "title": "Coffee Brand A",
        "short": "Brand A", 
        "app_name": "Order App A",
        "description": "Premium coffee chain with focus on quality and customer experience",
        "color_primary": "#B8865B",
        "color_secondary": "#D9B48C"
    },
    "BRAND_B": {
        "title": "Coffee Brand B",
        "short": "Brand B",
        "app_name": "Order App B", 
        "description": "Trendy coffee brand targeting young professionals",
        "color_primary": "#8B4513",
        "color_secondary": "#CD853F"
    }
}

# Portfolio user credentials for demonstration
# Note: In production, these would be securely hashed and stored in database
PORTFOLIO_USERS = {
    "brand_a_user": {
        "password": "portfolio_demo",  # Demo password for portfolio
        "brand": "BRAND_A",
        "role": "user",
        "description": "Brand A analyst user"
    },
    "brand_b_user": {
        "password": "portfolio_demo",  # Demo password for portfolio
        "brand": "BRAND_B", 
        "role": "user",
        "description": "Brand B analyst user"
    },
    "admin": {
        "password": "admin_demo",  # Demo admin password
        "brand": "BRAND_A",  # Admin has access to all brands
        "role": "admin",
        "description": "System administrator with full access"
    }
}

def get_brand_texts(brand_key):
    """
    Get brand-specific text configuration
    
    Args:
        brand_key (str): Brand identifier (BRAND_A, BRAND_B)
        
    Returns:
        dict: Brand text configuration
    """
    return BRAND_TEXTS.get(brand_key, BRAND_TEXTS["BRAND_A"])

def get_brand_schema(brand_key):
    """
    Get database schema name for specific brand
    
    Args:
        brand_key (str): Brand identifier (BRAND_A, BRAND_B)
        
    Returns:
        str: Database schema name
    """
    return BRAND_SCHEMA.get(brand_key, BRAND_SCHEMA["BRAND_A"])

def get_available_brands():
    """
    Get list of all available brands
    
    Returns:
        list: List of brand keys
    """
    return list(BRAND_SCHEMA.keys())

def validate_brand_access(user_brand, requested_brand):
    """
    Validate if user has access to requested brand data
    
    Args:
        user_brand (str): User's assigned brand
        requested_brand (str): Brand data being requested
        
    Returns:
        bool: True if access is allowed
    """
    # Admin users have access to all brands
    if user_brand == "admin":
        return True
    
    # Regular users can only access their assigned brand
    return user_brand == requested_brand

# Data table prefixes for each brand
BRAND_TABLE_PREFIXES = {
    "BRAND_A": "DT_BRAND_A",
    "BRAND_B": "DT_BRAND_B"
}

def get_table_prefix(brand_key):
    """
    Get table prefix for specific brand
    
    Args:
        brand_key (str): Brand identifier
        
    Returns:
        str: Table prefix for the brand
    """
    return BRAND_TABLE_PREFIXES.get(brand_key, BRAND_TABLE_PREFIXES["BRAND_A"])

# Portfolio configuration flags
PORTFOLIO_CONFIG = {
    "is_demo": True,
    "use_sample_data": True,
    "mask_sensitive_info": True,
    "tesla_portfolio_mode": True,
    "demo_data_only": True
} 