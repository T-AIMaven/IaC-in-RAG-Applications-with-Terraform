import os
from uuid import uuid4
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import Distance, PointStruct, VectorParams
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import SimpleDirectoryReader
from s3fs import S3FileSystem
import openai

# Load environment variables
load_dotenv()

# Configuration
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'documents')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('DOCUMENT_BUCKET')
S3_PREFIX = 'documents/'  # Subdirectory in S3 bucket where the documents are stored

openai.api_key = OPENAI_API_KEY

# Set OpenAI API key
if OPENAI_API_KEY is None:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

def get_documents_s3(aws_access_key_id, aws_secret_access_key, bucket_name, s3_prefix):
    s3_fs = S3FileSystem(key=aws_access_key_id, secret=aws_secret_access_key)

    bucket_path = f'{bucket_name}/{s3_prefix}'
    print("Listing files in S3 path:")
    for file in s3_fs.ls(bucket_path):
        print(file)

    try:
        reader = SimpleDirectoryReader(
            input_dir=bucket_path,
            fs=s3_fs,
            recursive=True
        )
        documents = reader.load_data()
        return documents

    except Exception as e:
        print(f"Error: {e}")
        return None

def split_documents_into_nodes(all_documents):
    try:
        splitter = SentenceSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )
        nodes = splitter.get_nodes_from_documents(all_documents)
        return nodes
    except Exception as e:
        print(f"Error splitting documents into nodes: {e}")
        return []

def create_collection_if_not_exists(client, collection_name):
    try:
        collections = client.get_collections()
        if collection_name not in [col.name for col in collections.collections]:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"Collection '{collection_name}' created.")
        else:
            print(f"Collection '{collection_name}' already exists.")
    except ResponseHandlingException as e:
        print(f"Error checking or creating collection: {e}")

def process_and_upsert_nodes(data, client, collection_name, embed_model):
    chunked_nodes = []

    for item in data:
        qdrant_id = str(uuid4())
        document_id = item.id_
        code_text = item.text
        file_path = item.metadata["file_path"]
        file_name = item.metadata["file_name"]

        content_vector = embed_model.get_text_embedding(code_text)

        payload = {
            "text": code_text,
            "document_id": document_id,
            "metadata": {
                "qdrant_id": qdrant_id,
                "file_path": file_path,
                "file_name": file_name,
            }
        }

        metadata = PointStruct(id=qdrant_id, vector=content_vector, payload=payload)
        chunked_nodes.append(metadata)

    if chunked_nodes:
        client.upsert(
            collection_name=collection_name,
            wait=True,
            points=chunked_nodes
        )

    print(f"{len(chunked_nodes)} Chunked metadata upserted.")

if __name__ == "__main__":
    # Get documents from S3
    all_documents = get_documents_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, S3_PREFIX)

    if all_documents:
        # Split documents into nodes
        nodes = split_documents_into_nodes(all_documents)

        # Initialize embedding model
        embed_model = OpenAIEmbedding(openai_api_key=OPENAI_API_KEY)

        # Initialize Qdrant client
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

        # Create collection if it does not exist
        create_collection_if_not_exists(client, COLLECTION_NAME)

        # Process and upsert documents in vector store
        process_and_upsert_nodes(nodes[:15], client, COLLECTION_NAME, embed_model)
    else:
        print("No documents were loaded from S3. Please check your S3 configuration and bucket contents.")