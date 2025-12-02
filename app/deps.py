from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.config import settings
from app.rag.vectorstore import get_vectorstore
from app.embeddings import DashScopeEmbeddings


# def get_embeddings():
#     return OpenAIEmbeddings(api_key=settings.openai_api_key)
# def get_embeddings():
#     return HuggingFaceEmbeddings(
#         model_name="./models/bge-small-zh",  # ← 本地路径！
#         model_kwargs={"device": "cpu"},
#         encode_kwargs={"normalize_embeddings": True},
#
#     )

def get_llm():
    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.deepseek_api_key,
        base_url=settings.base_url,
        temperature=0.2,
        streaming=True,
    )


def get_embeddings():
    return DashScopeEmbeddings(

    model="text-embedding-v3",

    api_key=settings.dashscope_api_key

)


def get_vs():
    return get_vectorstore(get_embeddings())

if __name__ == '__main__':
    # print(settings.dashscope_api_key)
    # print(settings.deepseek_api_key)
    # print('--------------')
    # print(get_llm())
    # print('--------------')
    # print(get_vs())
    # print('--------------')



    embeddings = get_embeddings()

    vec = embeddings.embed_query("你好，阿里云")

    print(f"Embedding dimension: {len(vec)}")  # v3/v4 都是 1024

    print(f"First 5 values: {vec[:5]}")
