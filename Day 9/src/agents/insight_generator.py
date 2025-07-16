import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Union
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from pydantic import BaseModel, Field
import json
from langchain.agents import initialize_agent, Tool
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import io
import base64
import os
from dotenv import load_dotenv

load_dotenv()

class Insight(BaseModel):
    """Schema for generated insight"""
    title: str
    description: str
    visualization_type: str
    data: Dict
    recommendations: List[str]
    priority: str

class InsightGenerator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        self.analysis_template = """
        You are an expert in financial data analysis and visualization. Analyze the following data and generate insights:

        DATA:
        {data}

        Please provide your analysis in the following JSON format:
        {{
            "insights": ["insight1", "insight2", ...],
            "recommendations": ["recommendation1", "recommendation2", ...],
            "priority": "High/Medium/Low"
        }}

        Ensure the response is a valid JSON object with these exact fields.
        """

    def generate_insights(self, df: pd.DataFrame, anomalies: List[Dict], benchmarks: Dict) -> List[Insight]:
        """Generate insights from expense data"""
        insights = []
        
        # Generate spending pattern insights
        pattern_insights = self._analyze_spending_patterns(df)
        insights.extend(pattern_insights)
        
        # Generate anomaly insights
        anomaly_insights = self._analyze_anomalies(anomalies)
        insights.extend(anomaly_insights)
        
        # Generate benchmark insights
        benchmark_insights = self._analyze_benchmarks(benchmarks)
        insights.extend(benchmark_insights)
        
        return insights

    def _analyze_spending_patterns(self, df: pd.DataFrame) -> List[Insight]:
        """Analyze spending patterns and generate insights"""
        insights = []
        
        # Monthly trend analysis
        monthly_data = df.groupby(pd.to_datetime(df['date']).dt.strftime('%Y-%m'))['amount'].sum()
        if not monthly_data.empty:
            insight = Insight(
                title="Monthly Spending Trends",
                description="Analysis of spending patterns over time",
                visualization_type="line",
                data={
                    "x": monthly_data.index.tolist(),
                    "y": monthly_data.values.tolist()
                },
                recommendations=self._generate_recommendations(monthly_data),
                priority="Medium"
            )
            insights.append(insight)
        
        # Category analysis
        category_data = df.groupby('category')['amount'].sum()
        if not category_data.empty:
            insight = Insight(
                title="Spending by Category",
                description="Distribution of expenses across categories",
                visualization_type="pie",
                data={
                    "labels": category_data.index.tolist(),
                    "values": category_data.values.tolist()
                },
                recommendations=self._generate_recommendations(category_data),
                priority="High"
            )
            insights.append(insight)
        
        return insights

    def _analyze_anomalies(self, anomalies: List[Dict]) -> List[Insight]:
        """Analyze anomalies and generate insights"""
        insights = []
        
        if anomalies:
            # Group anomalies by type
            anomaly_types = {}
            for anomaly in anomalies:
                anomaly_type = anomaly.anomaly_type if hasattr(anomaly, 'anomaly_type') else anomaly.get('anomaly_type', 'Unknown')
                if anomaly_type not in anomaly_types:
                    anomaly_types[anomaly_type] = []
                anomaly_types[anomaly_type].append(anomaly)
            
            # Generate insights for each anomaly type
            for anomaly_type, type_anomalies in anomaly_types.items():
                # Calculate statistics for this anomaly type
                total_amount = sum(a.amount if hasattr(a, 'amount') else a.get('amount', 0) for a in type_anomalies)
                avg_severity = sum(a.severity if hasattr(a, 'severity') else a.get('severity', 0) for a in type_anomalies) / len(type_anomalies)
                
                insight = Insight(
                    title=f"{anomaly_type} Anomalies Analysis",
                    description=f"Analysis of {anomaly_type.lower()} anomalies with total value of ${total_amount:,.2f}",
                    visualization_type="bar",
                    data={
                        "categories": [a.category if hasattr(a, 'category') else a.get('category', 'Unknown') for a in type_anomalies],
                        "values": [float(a.amount if hasattr(a, 'amount') else a.get('amount', 0)) for a in type_anomalies],
                        "severity": [float(a.severity if hasattr(a, 'severity') else a.get('severity', 0)) for a in type_anomalies]
                    },
                    recommendations=self._generate_anomaly_recommendations(type_anomalies),
                    priority="High" if avg_severity > 0.7 else "Medium"
                )
                insights.append(insight)
        
        return insights

    def _analyze_benchmarks(self, benchmarks: Dict) -> List[Insight]:
        """Analyze benchmark comparisons and generate insights"""
        insights = []
        
        for category, benchmark_data in benchmarks.items():
            insight = Insight(
                title=f"{category} Benchmark Analysis",
                description=f"Comparison of {category} spending against industry benchmarks",
                visualization_type="comparison",
                data=benchmark_data,
                recommendations=self._generate_benchmark_recommendations(benchmark_data),
                priority="Medium"
            )
            insights.append(insight)
        
        return insights

    def _generate_recommendations(self, data: pd.Series) -> List[str]:
        """Generate recommendations based on data analysis"""
        try:
            prompt = ChatPromptTemplate.from_template(self.analysis_template)
            chain = prompt | self.llm
            
            result = chain.invoke({"data": data.to_json()})
            # Extract content from AIMessage and parse JSON
            if hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
            
            # Clean the content to ensure it's valid JSON
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            analysis = json.loads(content)
            return analysis.get("recommendations", ["No specific recommendations available."])
        except Exception as e:
            return [f"Unable to generate recommendations at this time. Please try again."]

    def _generate_anomaly_recommendations(self, anomalies: List[Dict]) -> List[str]:
        """Generate recommendations for anomalies"""
        try:
            # Convert anomalies to dictionaries for JSON serialization
            anomaly_dicts = [
                {
                    "amount": float(a.amount if hasattr(a, 'amount') else a.get('amount', 0)),
                    "category": str(a.category if hasattr(a, 'category') else a.get('category', 'Unknown')),
                    "vendor": str(a.vendor if hasattr(a, 'vendor') else a.get('vendor', 'Unknown')),
                    "department": str(a.department if hasattr(a, 'department') else a.get('department', 'Unknown')),
                    "anomaly_type": str(a.anomaly_type if hasattr(a, 'anomaly_type') else a.get('anomaly_type', 'Unknown')),
                    "severity": float(a.severity if hasattr(a, 'severity') else a.get('severity', 0)),
                    "explanation": str(a.explanation if hasattr(a, 'explanation') else a.get('explanation', 'No explanation provided'))
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
            first_anomaly = anomalies[0] if anomalies else None
            anomaly_type = first_anomaly.anomaly_type if first_anomaly and hasattr(first_anomaly, 'anomaly_type') else first_anomaly.get('anomaly_type', 'various') if first_anomaly else 'various'
            category = first_anomaly.category if first_anomaly and hasattr(first_anomaly, 'category') else first_anomaly.get('category', 'various categories') if first_anomaly else 'various categories'
            
            return [
                f"Review {len(anomalies)} {anomaly_type.lower()} anomalies in {category}",
                "Investigate the transactions for potential issues",
                "Verify the legitimacy of these transactions",
                "Consider implementing additional controls if needed"
            ]
            
        except Exception as e:
            return [
                f"Review {len(anomalies)} anomalies in various categories",
                "Investigate the transactions for potential issues",
                "Verify the legitimacy of these transactions"
            ]

    def _generate_benchmark_recommendations(self, benchmark_data: Dict) -> List[str]:
        """Generate recommendations based on benchmark analysis"""
        try:
            prompt = ChatPromptTemplate.from_template(self.analysis_template)
            chain = prompt | self.llm
            
            result = chain.invoke({"data": json.dumps(benchmark_data)})
            # Extract content from AIMessage and parse JSON
            if hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)
            
            # Clean the content to ensure it's valid JSON
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            analysis = json.loads(content)
            return analysis.get("recommendations", ["No specific recommendations available."])
        except Exception as e:
            return [f"Unable to generate recommendations at this time. Please try again."]

    def create_visualization(self, insight: Insight) -> go.Figure:
        """Create visualization for an insight"""
        if insight.visualization_type == "line":
            fig = px.line(
                x=insight.data["x"],
                y=insight.data["y"],
                title=insight.title
            )
        elif insight.visualization_type == "pie":
            fig = px.pie(
                values=insight.data["values"],
                names=insight.data["labels"],
                title=insight.title
            )
        elif insight.visualization_type == "bar":
            fig = px.bar(
                x=insight.data["categories"],
                y=insight.data["values"],
                title=insight.title
            )
        elif insight.visualization_type == "comparison":
            # Create comparison visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Your Spending",
                x=[insight.data["category"]],
                y=[insight.data["your_spend"]]
            ))
            fig.add_trace(go.Bar(
                name="Industry Average",
                x=[insight.data["category"]],
                y=[insight.data["industry_average"]]
            ))
            fig.update_layout(title=insight.title)
        else:
            fig = go.Figure()
            fig.add_annotation(
                text="No visualization available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
        
        return fig 

# Tool for insight generation

def generate_insights(expense_records):
    try:
        df = pd.DataFrame(expense_records)
        if 'amount' not in df.columns:
            return 'No amount column found.'
        kmeans = KMeans(n_clusters=2, random_state=0).fit(df[['amount']])
        df['cluster'] = kmeans.labels_
        plt.figure()
        for cluster in df['cluster'].unique():
            cluster_df = df[df['cluster'] == cluster]
            plt.scatter(cluster_df.index, cluster_df['amount'], label=f'Cluster {cluster}')
        plt.xlabel('Index')
        plt.ylabel('Amount')
        plt.title('Expense Clusters')
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return {'clusters': df.to_dict(orient='records'), 'plot_base64': img_base64}
    except Exception as e:
        return f"Insight generation error: {e}"

insight_tool = Tool(
    name="InsightGenerator",
    func=generate_insights,
    description="Clusters expense patterns and generates dashboard-ready insights."
)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

insight_agent = initialize_agent(
    tools=[insight_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

def run_insight_agent(expense_records):
    return insight_agent.run(expense_records) 