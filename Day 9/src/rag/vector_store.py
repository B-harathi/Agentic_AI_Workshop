import chromadb
from chromadb.config import Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
import os
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

CHROMA_PATH = os.path.join(os.path.dirname(__file__), 'chroma_db')

class VectorStore:
    def __init__(self, persist_directory=CHROMA_PATH):
        self.persist_directory = persist_directory
        self.client = chromadb.Client(Settings(persist_directory=self.persist_directory))
        self.collection = self.client.get_or_create_collection('benchmarks')
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

    def add_documents_from_csv(self, csv_path, chunk_size=500):
        df = pd.read_csv(csv_path)
        docs = []
        for _, row in df.iterrows():
            text = ' '.join([str(x) for x in row.values])
            docs.append(text)
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
        chunks = splitter.create_documents(docs)
        texts = [chunk.page_content for chunk in chunks]
        vectors = self.embeddings.embed_documents(texts)
        self.collection.add(documents=texts, embeddings=vectors)

    def query(self, query_text, n_results=3):
        query_vector = self.embeddings.embed_query(query_text)
        results = self.collection.query(query_embeddings=[query_vector], n_results=n_results)
        # Return the actual text chunks
        return results['documents'][0] if 'documents' in results else [] 