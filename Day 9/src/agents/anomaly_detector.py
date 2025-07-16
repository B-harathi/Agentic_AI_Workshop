import pandas as pd
import numpy as np
from typing import Dict, List, Union
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json
from .insight_generator import Insight
from langchain.agents import initialize_agent, Tool
import os
from dotenv import load_dotenv
load_dotenv()

class Anomaly(BaseModel):
    """Schema for detected anomaly"""
    transaction_id: Union[int, str]
    amount: float
    category: str
    vendor: str
    department: str
    anomaly_type: str
    severity: float
    explanation: str

class AnomalyDetector:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        self.analysis_template = """
        You are an expert in financial anomaly detection. Analyze the following anomaly data and provide insights:

        ANOMALY DATA:
        {anomaly_data}

        Please provide:
        1. Type of anomaly
        2. Severity level (0-1)
        3. Detailed explanation
        4. Recommended actions

        Format the response as a JSON object with these fields.
        """

    def detect_anomalies(self, df: pd.DataFrame) -> List[Anomaly]:
        """Detect anomalies using multiple methods"""
        anomalies = []
        
        # Statistical anomaly detection
        stat_anomalies = self._detect_statistical_anomalies(df)
        anomalies.extend(stat_anomalies)
        
        # Pattern-based anomaly detection
        pattern_anomalies = self._detect_pattern_anomalies(df)
        anomalies.extend(pattern_anomalies)
        
        # Vendor concentration anomalies
        vendor_anomalies = self._detect_vendor_anomalies(df)
        anomalies.extend(vendor_anomalies)
        
        return anomalies

    def _detect_statistical_anomalies(self, df: pd.DataFrame) -> List[Anomaly]:
        """Detect anomalies using statistical methods"""
        anomalies = []
        
        # Prepare features for anomaly detection
        features = ['amount']
        X = df[features].values
        
        # Scale the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Use Isolation Forest for anomaly detection
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        predictions = iso_forest.fit_predict(X_scaled)
        
        # Identify anomalies
        for idx, pred in enumerate(predictions):
            if pred == -1:  # Anomaly detected
                anomaly = Anomaly(
                    transaction_id=idx,
                    amount=df.iloc[idx]['amount'],
                    category=df.iloc[idx]['category'],
                    vendor=df.iloc[idx]['vendor'],
                    department=df.iloc[idx]['department'],
                    anomaly_type="Statistical",
                    severity=abs(iso_forest.score_samples(X_scaled[idx].reshape(1, -1))[0]),
                    explanation=self._generate_anomaly_explanation(df.iloc[idx], "statistical")
                )
                anomalies.append(anomaly)
        
        return anomalies

    def _detect_pattern_anomalies(self, df: pd.DataFrame) -> List[Anomaly]:
        """Detect anomalies based on spending patterns"""
        anomalies = []
        
        # Group by category and calculate statistics
        category_stats = df.groupby('category')['amount'].agg(['mean', 'std']).reset_index()
        
        # Detect category-level anomalies
        for _, row in df.iterrows():
            category_stat = category_stats[category_stats['category'] == row['category']]
            if not category_stat.empty:
                z_score = abs((row['amount'] - category_stat['mean'].iloc[0]) / category_stat['std'].iloc[0])
                if z_score > 3:  # More than 3 standard deviations
                    anomaly = Anomaly(
                        transaction_id=row.name,
                        amount=row['amount'],
                        category=row['category'],
                        vendor=row['vendor'],
                        department=row['department'],
                        anomaly_type="Pattern",
                        severity=min(z_score / 10, 1.0),  # Normalize severity
                        explanation=self._generate_anomaly_explanation(row, "pattern")
                    )
                    anomalies.append(anomaly)
        
        return anomalies

    def _detect_vendor_anomalies(self, df: pd.DataFrame) -> List[Anomaly]:
        """Detect anomalies based on vendor concentration"""
        anomalies = []
        
        # Calculate vendor concentration
        vendor_totals = df.groupby('vendor')['amount'].sum()
        total_spend = vendor_totals.sum()
        vendor_concentration = vendor_totals / total_spend
        
        # Identify high concentration vendors
        high_concentration_vendors = vendor_concentration[vendor_concentration > 0.2]  # 20% threshold
        
        # Flag transactions from high concentration vendors
        for vendor in high_concentration_vendors.index:
            vendor_transactions = df[df['vendor'] == vendor]
            for _, row in vendor_transactions.iterrows():
                anomaly = Anomaly(
                    transaction_id=row.name,
                    amount=row['amount'],
                    category=row['category'],
                    vendor=row['vendor'],
                    department=row['department'],
                    anomaly_type="Vendor Concentration",
                    severity=float(vendor_concentration[vendor]),
                    explanation=self._generate_anomaly_explanation(row, "vendor")
                )
                anomalies.append(anomaly)
        
        return anomalies

    def _generate_anomaly_explanation(self, row: pd.Series, anomaly_type: str) -> str:
        """Generate explanation for detected anomaly"""
        try:
            prompt = ChatPromptTemplate.from_template(self.analysis_template)
            chain = prompt | self.llm
            
            anomaly_data = {
                "amount": float(row['amount']),
                "category": str(row['category']),
                "vendor": str(row['vendor']),
                "department": str(row['department']),
                "type": anomaly_type
            }
            
            result = chain.invoke({"anomaly_data": str(anomaly_data)})
            
            # Extract content from AIMessage
            if hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
            
            # Clean the content
            content = content.strip()
            
            # Remove JSON formatting if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            try:
                # Try to parse as JSON and extract the explanation
                json_data = json.loads(content)
                if isinstance(json_data, dict):
                    explanation = json_data.get('detailed_explanation', '')
                    if explanation:
                        return explanation
            except json.JSONDecodeError:
                pass
            
            # If JSON parsing fails or no explanation found, return cleaned content
            return content.replace('\n', ' ').strip()
            
        except Exception as e:
            return f"Anomaly detected in {row['category']} spending of ${row['amount']:,.2f} by {row['vendor']} in {row['department']} department."

    def _analyze_anomalies(self, anomalies: List[Anomaly]) -> List[Insight]:
        """Analyze anomalies and generate insights"""
        insights = []
        
        if anomalies:
            # Group anomalies by type
            anomaly_types = {}
            for anomaly in anomalies:
                if anomaly.anomaly_type not in anomaly_types:
                    anomaly_types[anomaly.anomaly_type] = []
                anomaly_types[anomaly.anomaly_type].append(anomaly)
            
            # Generate insights for each anomaly type
            for anomaly_type, type_anomalies in anomaly_types.items():
                # Calculate statistics for this anomaly type
                total_amount = sum(a.amount for a in type_anomalies)
                avg_severity = sum(a.severity for a in type_anomalies) / len(type_anomalies)
                
                insight = Insight(
                    title=f"{anomaly_type} Anomalies Analysis",
                    description=f"Analysis of {anomaly_type.lower()} anomalies with total value of ${total_amount:,.2f}",
                    visualization_type="bar",
                    data={
                        "categories": [a.category for a in type_anomalies],
                        "values": [float(a.amount) for a in type_anomalies],
                        "severity": [float(a.severity) for a in type_anomalies]
                    },
                    recommendations=self._generate_anomaly_recommendations(type_anomalies),
                    priority="High" if avg_severity > 0.7 else "Medium"
                )
                insights.append(insight)
        
        return insights

    def _generate_anomaly_recommendations(self, anomalies: List[Anomaly]) -> List[str]:
        """Generate recommendations for anomalies"""
        try:
            # Convert anomalies to dictionaries for JSON serialization
            anomaly_dicts = [
                {
                    "amount": float(a.amount),
                    "category": str(a.category),
                    "vendor": str(a.vendor),
                    "department": str(a.department),
                    "anomaly_type": str(a.anomaly_type),
                    "severity": float(a.severity),
                    "explanation": str(a.explanation)
                }
                for a in anomalies
            ]
            
            prompt = ChatPromptTemplate.from_template(self.analysis_template)
            chain = prompt | self.llm
            
            result = chain.invoke({"data": json.dumps(anomaly_dicts)})
            
            # Extract content from AIMessage
            if hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
            
            # Clean the content
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            try:
                # Try to parse as JSON and extract recommendations
                json_data = json.loads(content)
                if isinstance(json_data, dict):
                    recommendations = json_data.get('recommendations', [])
                    if recommendations:
                        return recommendations
            except json.JSONDecodeError:
                pass
            
            # If JSON parsing fails or no recommendations found, generate basic recommendations
            return [
                f"Review {len(anomalies)} {anomalies[0].anomaly_type.lower()} anomalies in {anomalies[0].category}",
                f"Investigate transactions with {anomalies[0].vendor}",
                "Verify the legitimacy of these transactions",
                "Consider implementing additional controls if needed"
            ]
            
        except Exception as e:
            return [
                f"Review {len(anomalies)} anomalies in {anomalies[0].category if anomalies else 'various categories'}",
                "Investigate the transactions for potential issues",
                "Verify the legitimacy of these transactions"
            ]

# Tool for anomaly detection

def detect_anomalies(expense_records):
    try:
        df = pd.DataFrame(expense_records)
        if 'amount' not in df.columns:
            return 'No amount column found.'
        df['zscore'] = (df['amount'] - df['amount'].mean()) / df['amount'].std()
        anomalies = df[np.abs(df['zscore']) > 2]
        return anomalies.to_dict(orient='records')
    except Exception as e:
        return f"Anomaly detection error: {e}"

anomaly_tool = Tool(
    name="AnomalyDetector",
    func=detect_anomalies,
    description="Flags outliers in expense data based on statistical deviation."
)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

anomaly_agent = initialize_agent(
    tools=[anomaly_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

def run_anomaly_agent(expense_records):
    return anomaly_agent.run(expense_records) 