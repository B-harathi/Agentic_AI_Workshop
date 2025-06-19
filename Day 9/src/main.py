import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os
from dotenv import load_dotenv
import json

# Import agents
from .agents.expense_parser import ExpenseParser
from .agents.anomaly_detector import AnomalyDetector
from .agents.benchmark_retriever import BenchmarkRetriever
from .agents.insight_generator import InsightGenerator

# Load environment variables
load_dotenv()

def load_expense_data(uploaded_file):
    """Load and process expense data from uploaded CSV file"""
    try:
        df = pd.read_csv(uploaded_file)
        required_columns = ['date', 'amount', 'category', 'vendor', 'department']
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return pd.DataFrame()
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def main():
    # Set page config
    st.set_page_config(
        page_title="Expense Pattern Auditor",
        page_icon="💰",
        layout="wide"
    )

    # Title and description
    st.title("Expense Pattern Auditor")
    st.markdown("""
    This tool helps analyze expense patterns, detect anomalies, and compare against industry benchmarks.
    Upload your expense data to get started.
    """)

    # Initialize agents
    expense_parser = ExpenseParser()
    anomaly_detector = AnomalyDetector()
    benchmark_retriever = BenchmarkRetriever()
    insight_generator = InsightGenerator()

    # File uploader
    uploaded_file = st.file_uploader("Upload Expense Data (CSV)", type=['csv'])

    if uploaded_file is not None:
        # Load and process data
        df = load_expense_data(uploaded_file)
        
        if df.empty:
            st.error("No valid data found in the uploaded file. Please check the file format and try again.")
        else:
            # Sidebar filters
            st.sidebar.header("Filters")
            
            # Date range filter
            date_range = st.sidebar.selectbox(
                "Select Date Range",
                ["This Week", "This Month", "Last Month", "Last 6 Months", "This Year", "Custom"]
            )
            
            if date_range == "Custom":
                start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=30))
                end_date = st.sidebar.date_input("End Date", datetime.now())
            else:
                # Calculate date range based on selection
                end_date = datetime.now()
                if date_range == "This Week":
                    start_date = end_date - timedelta(days=7)
                elif date_range == "This Month":
                    start_date = end_date.replace(day=1)
                elif date_range == "Last Month":
                    start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
                elif date_range == "Last 6 Months":
                    start_date = end_date - timedelta(days=180)
                else:  # This Year
                    start_date = end_date.replace(month=1, day=1)
            
            # Filter data based on date range
            df['date'] = pd.to_datetime(df['date'])
            mask = (df['date'] >= pd.Timestamp(start_date)) & (df['date'] <= pd.Timestamp(end_date))
            filtered_df = df.loc[mask]
            
            if filtered_df.empty:
                st.warning("No data available for the selected date range.")
            else:
                # Additional filters
                vendors = st.sidebar.multiselect("Select Vendors", df['vendor'].unique())
                departments = st.sidebar.multiselect("Select Departments", df['department'].unique())
                
                if vendors:
                    filtered_df = filtered_df[filtered_df['vendor'].isin(vendors)]
                if departments:
                    filtered_df = filtered_df[filtered_df['department'].isin(departments)]
                
                if filtered_df.empty:
                    st.warning("No data available for the selected filters.")
                else:
                    # Main content
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Expense Overview")
                        # Total expenses
                        total_expenses = filtered_df['amount'].sum()
                        st.metric("Total Expenses", f"${total_expenses:,.2f}")
                        
                        # Expenses by category
                        category_expenses = filtered_df.groupby('category')['amount'].sum().reset_index()
                        if not category_expenses.empty:
                            fig_category = px.bar(
                                category_expenses,
                                x='category',
                                y='amount',
                                title='Expenses by Category'
                            )
                            st.plotly_chart(fig_category)
                    
                    with col2:
                        st.subheader("Vendor Analysis")
                        # Expenses by vendor
                        vendor_expenses = filtered_df.groupby('vendor')['amount'].sum().reset_index()
                        if not vendor_expenses.empty:
                            fig_vendor = px.bar(
                                vendor_expenses,
                                x='vendor',
                                y='amount',
                                title='Expenses by Vendor'
                            )
                            st.plotly_chart(fig_vendor)
                    
                    # Analysis Options
                    st.header("Analysis Options")
                    analysis_type = st.selectbox(
                        "Select Analysis Type",
                        ["Comprehensive Analysis", "Anomaly Detection", "Benchmark Analysis", "Insight Generation"]
                    )

                    try:
                        if analysis_type == "Comprehensive Analysis":
                            st.subheader("Comprehensive Analysis")
                            if st.button("Run Analysis"):
                                with st.spinner("Running comprehensive analysis..."):
                                    try:
                                        # Parse and validate data
                                        validation_results = expense_parser.validate_data(filtered_df)
                                        if validation_results["missing_fields"] or validation_results["type_errors"]:
                                            st.error("Data validation failed. Please check the data format.")
                                            return
                                        
                                        # Enrich data
                                        enriched_df = expense_parser.enrich_data(filtered_df)
                                        
                                        # Detect anomalies
                                        anomalies = anomaly_detector.detect_anomalies(enriched_df)
                                        
                                        # Get benchmarks
                                        benchmarks = benchmark_retriever.analyze_against_benchmarks(enriched_df)
                                        
                                        # Generate insights
                                        insights = insight_generator.generate_insights(enriched_df, anomalies, benchmarks)
                                        
                                        # Display results
                                        st.write("### Detected Anomalies")
                                        if anomalies:
                                            for anomaly in anomalies:
                                                st.write(f"- {anomaly.explanation}")
                                        else:
                                            st.success("No anomalies detected.")
                                        
                                        st.write("### Benchmark Analysis")
                                        if benchmarks:
                                            for category, benchmark in benchmarks.items():
                                                st.write(f"#### {category}")
                                                st.write(f"Industry Average: ${benchmark.get('industry_average', 0):,.2f}")
                                                st.write(f"Your Spending: ${benchmark.get('your_spend', 0):,.2f}")
                                        else:
                                            st.info("No benchmark data available.")
                                        
                                        st.write("### Insights")
                                        if insights:
                                            for insight in insights:
                                                st.write(f"#### {insight.title}")
                                                st.write(insight.description)
                                                fig = insight_generator.create_visualization(insight)
                                                st.plotly_chart(fig)
                                                st.write("Recommendations:")
                                                for rec in insight.recommendations:
                                                    st.write(f"- {rec}")
                                        else:
                                            st.info("No insights generated.")
                                    except Exception as e:
                                        st.error(f"Error during comprehensive analysis: {str(e)}")

                        elif analysis_type == "Anomaly Detection":
                            st.subheader("Anomaly Detection")
                            if st.button("Detect Anomalies"):
                                with st.spinner("Detecting anomalies..."):
                                    try:
                                        anomalies = anomaly_detector.detect_anomalies(filtered_df)
                                        
                                        if not anomalies:
                                            st.success("No anomalies detected.")
                                        else:
                                            st.write("### Detected Anomalies")
                                            for anomaly in anomalies:
                                                st.write(f"- Transaction {anomaly.transaction_id}: ${anomaly.amount:,.2f}")
                                                st.write(f"  Category: {anomaly.category}")
                                                st.write(f"  Vendor: {anomaly.vendor}")
                                                st.write(f"  Type: {anomaly.anomaly_type}")
                                                st.write(f"  Severity: {anomaly.severity:.2f}")
                                                st.write(f"  Explanation: {anomaly.explanation}")
                                                st.write("---")
                                    except Exception as e:
                                        st.error(f"Error during anomaly detection: {str(e)}")

                        elif analysis_type == "Benchmark Analysis":
                            st.subheader("Benchmark Analysis")
                            if st.button("Analyze Benchmarks"):
                                with st.spinner("Analyzing benchmarks..."):
                                    try:
                                        benchmarks = benchmark_retriever.analyze_against_benchmarks(filtered_df)
                                        
                                        if not benchmarks:
                                            st.warning("No benchmark data available for the selected categories.")
                                        else:
                                            for category, benchmark in benchmarks.items():
                                                st.write(f"### {category}")
                                                col1, col2 = st.columns(2)
                                                
                                                with col1:
                                                    st.metric(
                                                        "Industry Average",
                                                        f"${benchmark['industry_average']:,.2f}",
                                                        f"{benchmark['spend_vs_average']:+.1f}%"
                                                    )
                                                    st.write(f"25th Percentile: ${benchmark['percentile_25']:,.2f}")
                                                    st.write(f"75th Percentile: ${benchmark['percentile_75']:,.2f}")
                                                
                                                with col2:
                                                    st.metric(
                                                        "Your Spending",
                                                        f"${benchmark['your_spend']:,.2f}",
                                                        f"Percentile: {benchmark['percentile']}th"
                                                    )
                                                    st.write(f"Data Source: {benchmark['source']}")
                                                    st.write(f"Confidence: {benchmark['confidence']*100:.0f}%")
                                                
                                                st.write("#### Recommendations")
                                                for rec in benchmark['recommendations']:
                                                    st.write(f"- {rec}")
                                                
                                                st.write("---")
                                    except Exception as e:
                                        st.error(f"Error during benchmark analysis: {str(e)}")

                        elif analysis_type == "Insight Generation":
                            st.subheader("Insight Generation")
                            if st.button("Generate Insights"):
                                with st.spinner("Generating insights..."):
                                    try:
                                        insights = insight_generator.generate_insights(filtered_df, [], {})
                                        
                                        if not insights:
                                            st.warning("No insights could be generated.")
                                        else:
                                            for insight in insights:
                                                st.write(f"### {insight.title}")
                                                st.write(insight.description)
                                                fig = insight_generator.create_visualization(insight)
                                                st.plotly_chart(fig)
                                                st.write("Recommendations:")
                                                for rec in insight.recommendations:
                                                    st.write(f"- {rec}")
                                                st.write("---")
                                    except Exception as e:
                                        st.error(f"Error during insight generation: {str(e)}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
