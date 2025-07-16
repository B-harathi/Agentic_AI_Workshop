import pandas as pd
from typing import Dict, List, Union
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from pydantic import BaseModel, Field

class ParsedExpense(BaseModel):
    """Schema for parsed expense data"""
    date: str
    amount: float
    category: str
    vendor: str
    department: str
    description: str
    confidence_score: float

class ExpenseParser:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash",
            temperature=0.1,
            google_api_key="AIzaSyCi1Fr-z-A8fDB3ahs8Iduz3nsM1gIOKxk"
        )
        
        self.parsing_template = """
        You are an expert expense data parser. Analyze the following expense data and extract structured information:

        EXPENSE DATA:
        {expense_data}

        Please extract the following information:
        1. Date of the expense
        2. Amount
        3. Category
        4. Vendor
        5. Department
        6. Description
        7. Confidence score (0-1) for the extraction

        Format the response as a JSON object with these fields.
        """

    def parse_expense(self, expense_data: str) -> ParsedExpense:
        """Parse a single expense entry"""
        try:
            prompt = ChatPromptTemplate.from_template(self.parsing_template)
            chain = prompt | self.llm
            
            result = chain.invoke({"expense_data": expense_data})
            return ParsedExpense.parse_raw(result)
        except Exception as e:
            st.error(f"Error parsing expense: {str(e)}")
            return None

    def parse_batch(self, expenses: List[str]) -> List[ParsedExpense]:
        """Parse multiple expense entries"""
        return [self.parse_expense(expense) for expense in expenses]

    def validate_data(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Validate expense data for required fields and data types"""
        validation_results = {
            "missing_fields": [],
            "type_errors": [],
            "format_errors": []
        }
        
        required_fields = ['date', 'amount', 'category', 'vendor', 'department']
        
        # Check for missing fields
        for field in required_fields:
            if field not in df.columns:
                validation_results["missing_fields"].append(field)
        
        # Validate data types
        try:
            pd.to_datetime(df['date'])
        except:
            validation_results["type_errors"].append("date")
            
        try:
            pd.to_numeric(df['amount'])
        except:
            validation_results["type_errors"].append("amount")
        
        return validation_results

    def enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich expense data with additional information"""
        try:
            # Add month and year columns
            df['month'] = pd.to_datetime(df['date']).dt.month
            df['year'] = pd.to_datetime(df['date']).dt.year
            
            # Add expense type based on category
            df['expense_type'] = df['category'].apply(self._categorize_expense_type)
            
            # Add vendor risk score
            df['vendor_risk_score'] = df['vendor'].apply(self._calculate_vendor_risk)
            
            return df
        except Exception as e:
            st.error(f"Error enriching data: {str(e)}")
            return df

    def _categorize_expense_type(self, category: str) -> str:
        """Categorize expense type based on category"""
        category_mapping = {
            'Travel': 'Operational',
            'Office Supplies': 'Operational',
            'Software': 'Technology',
            'Hardware': 'Technology',
            'Marketing': 'Business Development',
            'Training': 'Professional Development',
            'Consulting': 'Professional Services',
            'Rent': 'Facilities',
            'Utilities': 'Facilities'
        }
        return category_mapping.get(category, 'Other')

    def _calculate_vendor_risk(self, vendor: str) -> float:
        """Calculate risk score for vendor"""
        # This is a simplified example. In a real implementation,
        # this would use more sophisticated logic and possibly external data
        high_risk_vendors = ['Unknown', 'Unregistered', 'Offshore']
        if vendor in high_risk_vendors:
            return 0.8
        return 0.2 