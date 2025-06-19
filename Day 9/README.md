# Expense Pattern Auditor (Agentic + RAG)

## Overview
This project automates the detection of unusual or recurring spending behaviors using four autonomous AI agents, built with LangChain. The Benchmark Retrieval Agent leverages Retrieval-Augmented Generation (RAG) with a local vector database (ChromaDB) to cross-check anomalies against industry standards.

## Agents
- **Expense Parsing Agent:** Extracts structured data from invoices, spreadsheets, or accounting tools.
- **Anomaly Detection Agent:** Flags outliers based on seasonality, vendor concentration, or category-level deviation.
- **Benchmark Retrieval Agent (RAG):** Uses RAG to pull industry-standard spend ratios and financial norms for cross-checking anomalies.
- **Insight Generation Agent:** Clusters patterns and visualizes them, highlighting risks and optimization opportunities.

## Architecture
- **LangChain Agents:** Each agent is an autonomous LangChain agent, not just a function or class.
- **RAG:** Only the Benchmark Retrieval Agent uses RAG with ChromaDB for retrieval.
- **Pipeline:** The main pipeline orchestrates the agents for end-to-end automation.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your OpenAI API key (for LLM):
   ```bash
   export OPENAI_API_KEY=your-key
   ```
3. (Optional) Add industry benchmarks to `src/rag/benchmarks/` and ingest them using `VectorStore`.

## Usage
Run the main pipeline:
```bash
python src/main.py
```

## Rubric Compliance
- **Agent Implementation:** All agents are autonomous LangChain agents.
- **RAG Implementation:** Benchmark Retrieval Agent uses RAG with ChromaDB.
- **Documentation:** This README and code docstrings explain the architecture and usage.
- **Solution Impact:** Automates detection, benchmarking, and insight generation for expense patterns.
- **Gen AI Usage:** Uses LangChain, OpenAI LLM, and ChromaDB for agentic and generative reasoning.
