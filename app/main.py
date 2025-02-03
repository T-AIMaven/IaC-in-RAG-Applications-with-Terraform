import os
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient
from contextlib import asynccontextmanager

print("Starting script...")

# Load environmental variables from .env file
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'documents')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Set OpenAI API key
if OPENAI_API_KEY is None:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Initialize Qdrant client
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


# Initialize embedding model
embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)

# Initialize index
index = None

class Query(BaseModel):
    question: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    await initialize_index()
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

async def initialize_index():
    global index
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=COLLECTION_NAME)
    
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

    print("Index initialized successfully.")

@app.post("/query")
async def query(query: Query):
    if not index:
        raise HTTPException(status_code=500, detail="Index not initialized")
    
    query_engine = index.as_query_engine()
    response = query_engine.query(query.question)
    return {"answer": str(response)}

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
def read_root():
    """Root endpoint returning API information."""
    return {
        "message": "Welcome to the CDK RAG API",
        "version": "V0",
        "documentation": "/docs",  # FastAPI automatic docs
        "health_check": "/health",
        "usage": "Send a POST request to /query with a JSON body containing a 'question' field."
    }

if __name__ == "__main__":
    import uvicorn
    print("About to start the server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

print("Script finished.")