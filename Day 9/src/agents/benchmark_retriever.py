import pandas as pd
from typing import Dict, List, Union, Optional
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, Field
import json
import os
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from src.rag.vector_store import VectorStore
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import io
import base64

# Load environment variables
load_dotenv()

class Benchmark(BaseModel):
    """Schema for industry benchmark data"""
    category: str
    industry_average: float
    percentile_25: float
    percentile_75: float
    source: str
    confidence: float

class BenchmarkRetriever:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash",
            temperature=0.1,
            google_api_key="AIzaSyCi1Fr-z-A8fDB3ahs8Iduz3nsM1gIOKxk"
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key="AIzaSyCi1Fr-z-A8fDB3ahs8Iduz3nsM1gIOKxk"
        )
        
        self.analysis_template = """
        You are an expert in financial benchmarking. Analyze the following expense data against industry standards:

        EXPENSE DATA:
        {expense_data}

        INDUSTRY BENCHMARKS:
        {benchmarks}

        Please provide:
        1. Comparison with industry averages
        2. Percentile rankings
        3. Areas of concern
        4. Optimization opportunities

        Format the response as a JSON object with these fields.
        """
        
        # Initialize vector store with benchmark data
        self._initialize_benchmark_store()

    def _initialize_benchmark_store(self):
        """Initialize vector store with benchmark data"""
        try:
            # Load benchmark data
            benchmark_data = self._load_benchmark_data()
            
            # Create vector store
            texts = [json.dumps(benchmark) for benchmark in benchmark_data]
            self.vector_store = FAISS.from_texts(texts, self.embeddings)
            
        except Exception as e:
            st.error(f"Error initializing benchmark store: {str(e)}")
            self.vector_store = None

    def _load_benchmark_data(self) -> List[Dict]:
        """Load benchmark data from various sources"""
        return [
            {
                "category": "Travel",
                "industry_average": 5000,
                "percentile_25": 3000,
                "percentile_75": 8000,
                "source": "Industry Survey 2023",
                "confidence": 0.9
            },
            {
                "category": "Office Supplies",
                "industry_average": 2000,
                "percentile_25": 1000,
                "percentile_75": 3000,
                "source": "Financial Database",
                "confidence": 0.85
            },
            {
                "category": "Software",
                "industry_average": 3000,
                "percentile_25": 1500,
                "percentile_75": 5000,
                "source": "Tech Industry Report",
                "confidence": 0.88
            },
            {
                "category": "Training",
                "industry_average": 2500,
                "percentile_25": 1200,
                "percentile_75": 4000,
                "source": "HR Analytics",
                "confidence": 0.82
            },
            {
                "category": "Marketing Materials",
                "industry_average": 1800,
                "percentile_25": 900,
                "percentile_75": 2800,
                "source": "Marketing Survey",
                "confidence": 0.87
            },
            {
                "category": "Office Rent",
                "industry_average": 8000,
                "percentile_25": 5000,
                "percentile_75": 12000,
                "source": "Real Estate Index",
                "confidence": 0.95
            },
            {
                "category": "Equipment",
                "industry_average": 4000,
                "percentile_25": 2000,
                "percentile_75": 6000,
                "source": "Equipment Survey",
                "confidence": 0.86
            },
            {
                "category": "Food & Beverage",
                "industry_average": 1500,
                "percentile_25": 800,
                "percentile_75": 2500,
                "source": "Catering Industry Report",
                "confidence": 0.84
            },
            {
                "category": "Transportation",
                "industry_average": 1200,
                "percentile_25": 600,
                "percentile_75": 2000,
                "source": "Transportation Survey",
                "confidence": 0.83
            },
            {
                "category": "Entertainment",
                "industry_average": 1000,
                "percentile_25": 500,
                "percentile_75": 1800,
                "source": "Entertainment Survey",
                "confidence": 0.81
            },
            {
                "category": "Events",
                "industry_average": 3500,
                "percentile_25": 1800,
                "percentile_75": 5500,
                "source": "Event Industry Report",
                "confidence": 0.89
            },
            {
                "category": "Investment",
                "industry_average": 10000,
                "percentile_25": 5000,
                "percentile_75": 15000,
                "source": "Investment Survey",
                "confidence": 0.92
            },
            {
                "category": "Miscellaneous",
                "industry_average": 800,
                "percentile_25": 400,
                "percentile_75": 1500,
                "source": "General Survey",
                "confidence": 0.80
            },
            {
                "category": "Office Decor",
                "industry_average": 1200,
                "percentile_25": 600,
                "percentile_75": 2000,
                "source": "Interior Design Survey",
                "confidence": 0.82
            },
            {
                "category": "Shopping",
                "industry_average": 1500,
                "percentile_25": 800,
                "percentile_75": 2500,
                "source": "Retail Survey",
                "confidence": 0.85
            }
        ]

    def get_benchmarks(self, category: str) -> List[Benchmark]:
        """Retrieve relevant benchmarks for a category"""
        try:
            # Search for relevant benchmarks
            results = self.vector_store.similarity_search(category, k=3)
            
            # Parse results
            benchmarks = []
            for result in results:
                benchmark_data = json.loads(result.page_content)
                benchmark = Benchmark(**benchmark_data)
                benchmarks.append(benchmark)
            
            return benchmarks
        except Exception as e:
            st.error(f"Error retrieving benchmarks: {str(e)}")
            return []

    def analyze_against_benchmarks(self, df: pd.DataFrame) -> Dict:
        """Analyze expenses against industry benchmarks"""
        try:
            analysis_results = {}
            
            # Group by category
            for category, group in df.groupby('category'):
                # Get benchmarks for category
                benchmarks = self.get_benchmarks(category)
                
                if benchmarks:
                    # Calculate statistics
                    total_spend = float(group['amount'].sum())
                    avg_transaction = float(group['amount'].mean())
                    num_transactions = int(len(group))
                    
                    # Get benchmark data
                    benchmark = benchmarks[0]  # Use the first matching benchmark
                    
                    # Calculate comparison metrics
                    spend_vs_average = (total_spend - benchmark.industry_average) / benchmark.industry_average * 100
                    percentile = self._calculate_percentile(total_spend, benchmark)
                    
                    # Generate recommendations based on the comparison
                    recommendations = self._generate_category_recommendations(
                        total_spend,
                        benchmark,
                        spend_vs_average,
                        percentile
                    )
                    
                    analysis_results[category] = {
                        "industry_average": float(benchmark.industry_average),
                        "your_spend": total_spend,
                        "percentile_25": float(benchmark.percentile_25),
                        "percentile_75": float(benchmark.percentile_75),
                        "spend_vs_average": spend_vs_average,
                        "percentile": percentile,
                        "recommendations": recommendations,
                        "source": benchmark.source,
                        "confidence": float(benchmark.confidence)
                    }
            
            return analysis_results
        except Exception as e:
            st.error(f"Error analyzing against benchmarks: {str(e)}")
            return {}

    def _calculate_percentile(self, spend: float, benchmark: Benchmark) -> float:
        """Calculate the percentile of spending relative to benchmarks"""
        if spend <= benchmark.percentile_25:
            return 25
        elif spend <= benchmark.industry_average:
            return 50
        elif spend <= benchmark.percentile_75:
            return 75
        else:
            return 90

    def _generate_category_recommendations(self, spend: float, benchmark: Benchmark, 
                                         spend_vs_average: float, percentile: float) -> List[str]:
        """Generate recommendations based on spending comparison"""
        recommendations = []
        
        if spend_vs_average > 20:  # Spending is significantly above average
            recommendations.append(f"Consider reducing {benchmark.category} expenses by {abs(spend_vs_average):.1f}% to align with industry average.")
            if percentile >= 75:
                recommendations.append("Your spending is in the top quartile. Review for potential cost optimization opportunities.")
        elif spend_vs_average < -20:  # Spending is significantly below average
            recommendations.append(f"Your {benchmark.category} spending is {abs(spend_vs_average):.1f}% below industry average. Consider if this aligns with your business needs.")
        else:
            recommendations.append(f"Your {benchmark.category} spending is within normal range compared to industry standards.")
        
        if benchmark.confidence >= 0.9:
            recommendations.append("High confidence in benchmark data. Recommendations are based on reliable industry data.")
        
        return recommendations

    def get_optimization_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """Generate optimization recommendations based on benchmark analysis"""
        recommendations = []
        
        for category, analysis in analysis_results.items():
            if "optimization_opportunities" in analysis:
                for opportunity in analysis["optimization_opportunities"]:
                    recommendations.append({
                        "category": category,
                        "opportunity": opportunity,
                        "potential_savings": analysis.get("potential_savings", "Unknown"),
                        "implementation_difficulty": analysis.get("implementation_difficulty", "Medium")
                    })
        
        return recommendations

# Tool for RAG retrieval
vector_store = VectorStore()

def retrieve_benchmark(query: str):
    """
    Uses RAG to retrieve relevant industry benchmarks and generate an answer.
    """
    retrieved_chunks = vector_store.query(query, n_results=3)
    context = '\n'.join(retrieved_chunks)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
    answer = llm.invoke(prompt)
    return answer

benchmark_tool = Tool(
    name="BenchmarkRetriever",
    func=retrieve_benchmark,
    description="Retrieves industry-standard spend ratios and financial norms for a given expense category or query using RAG."
)

benchmark_agent = initialize_agent(
    tools=[benchmark_tool],
    llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY")),
    agent="zero-shot-react-description",
    verbose=True
)

def run_benchmark_agent(query):
    return benchmark_agent.run(query)

def detect_anomalies(expense_records):
    """
    Flags outliers in expense data based on z-score of 'amount'.
    """
    try:
        df = pd.DataFrame(expense_records)
        if 'amount' not in df.columns or 'category' not in df.columns:
            return "Error: 'amount' or 'category' column not found in data."
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

def generate_insights(expense_records):
    """
    Clusters expense patterns and generates dashboard-ready insights.
    """
    try:
        df = pd.DataFrame(expense_records)
        if 'amount' not in df.columns or 'category' not in df.columns:
            return "Error: 'amount' or 'category' column not found in data."
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

insight_agent = initialize_agent(
    tools=[insight_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

def run_insight_agent(expense_records):
    return insight_agent.run(expense_records)

def main():
    # 1. Parse raw expenses (simulate with CSV string)
    with open('data/sample_expenses.csv', 'r') as f:
        raw_expenses = f.read()
    parsed_expenses = run_parsing_agent(raw_expenses)
    print('Parsed Expenses:', parsed_expenses)

    # 2. Detect anomalies
    anomalies = run_anomaly_agent(parsed_expenses)
    print('Anomalies:', anomalies)

    # 3. Retrieve benchmarks (RAG)
    benchmark_results = run_benchmark_agent('marketing spend ratio for SaaS')
    print('Benchmarks:', benchmark_results)

    # 4. Generate insights
    insights = run_insight_agent(parsed_expenses)
    print('Insights:', insights)

if __name__ == '__main__':
    main() 