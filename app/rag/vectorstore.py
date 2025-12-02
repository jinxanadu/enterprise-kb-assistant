import os
import chromadb
from langchain_chroma import Chroma
from app.config import settings

def get_vectorstore(embeddings):
    client = chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port
    )
    return Chroma(
        client=client,
        collection_name=settings.collection_name,
        embedding_function=embeddings,
    )

# def get_vectorstore(embeddings):
#     persist_dir = "./chroma_db"
#     os.makedirs(persist_dir, exist_ok=True)
#     return Chroma(
#             persist_directory=persist_dir,
#             collection_name=settings.collection_name,
#             embedding_function=embeddings,
#         )