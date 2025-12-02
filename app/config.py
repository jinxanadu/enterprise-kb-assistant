from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    embedding_model_name: str = "BAAI/bge-small-zh-v1.5"
    base_url: str = os.getenv("BASE_URL", "https://api.deepseek.com/v1")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "deepseek-chat")
    chroma_dir: str = os.getenv("CHROMA_DIR", "./data/chroma")
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))
    collection_name: str = os.getenv("COLLECTION_NAME", "knowledge_base")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))

settings = Settings()