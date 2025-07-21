# Math-Q&A Agent

This project is an agentic AI assistant that can answer general knowledge questions and perform math calculations using custom tools and LLMs.

## Project Structure

```
Create_an_Agent_Using_LLM_and_Custom_Mathematical_Functions/
  ├── agent/                # Core logic (agent, tools, workflow)
  │     └── core.py
  ├── ui/                   # UI code (Streamlit app)
  │     └── app.py
  ├── requirements.txt
  ├── README.md
```

## Setup & Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your `GOOGLE_API_KEY` in a `.env` file:
   ```env
   GOOGLE_API_KEY=your_key_here
   ```
3. Run the Streamlit UI:
   ```bash
   streamlit run ui/app.py
   ```

Enjoy chatting with your Math-Q&A Agent! 