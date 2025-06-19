import pandas as pd
import streamlit as st

def load_expense_data(uploaded_file):
    """
    Load and preprocess expense data from uploaded CSV file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        pandas.DataFrame: Processed expense data
    """
    try:
        # Read CSV file
        df = pd.read_csv(uploaded_file)
        
        # Validate required columns
        required_columns = ['date', 'amount', 'vendor', 'department', 'category', 'description', 'employee_id']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return pd.DataFrame()
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Convert amount to numeric, removing any currency symbols
        df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
        
        # Fill missing values
        df['description'] = df['description'].fillna('No description')
        df['category'] = df['category'].fillna('Uncategorized')
        
        # Sort by date
        df = df.sort_values('date')
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

