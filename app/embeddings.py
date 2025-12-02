# app/embeddings.py
import os
from typing import List, Any
import requests


class DashScopeEmbeddings:
    def __init__(self, model: str = "text-embedding-v3", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DashScope API key is required.")

    def embed_query(self, text: str) -> List[float]:
        return self._call_api([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._call_api(texts)

    # def _call_api(self, texts: List[str]) -> List[List[float]]:
    #     url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    #     headers = {
    #         "Authorization": f"Bearer {self.api_key}",
    #         "Content-Type": "application/json",
    #     }
    #     payload = {
    #         "model": self.model,
    #         "input": texts,  # 注意：兼容模式 input 是数组，不是 {"texts": [...]}
    #     }
    #
    #     response = requests.post(url, headers=headers, json=payload)
    #     if response.status_code != 200:
    #         raise RuntimeError(f"DashScope API error: {response.status_code} - {response.text}")
    #
    #     data = response.json()
    #     return [item["embedding"] for item in data["data"]]

    def _call_api(self, texts: List[str]) -> List[List[float]]:

        # 过滤掉 None 和空字符串

        valid_texts = [text for text in texts if text and isinstance(text, str) and text.strip()]

        if not valid_texts:
            raise ValueError("No valid texts to embed. All inputs are empty or None.")

        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"

        headers = {

            "Authorization": f"Bearer {self.api_key}",

            "Content-Type": "application/json",

        }

        payload = {

            "model": self.model,

            "input": valid_texts,  # ✅ 确保是非空列表

        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"DashScope API error: {response.status_code} - {response.text}")

        data = response.json()

        embeddings = [item["embedding"] for item in data["data"]]

        # 如果需要保持原始长度（比如 LangChain 要求返回 len(texts) 个 embedding），

        # 可以为无效文本填充零向量（不推荐），或抛出错误。

        # 这里建议直接拒绝无效输入：

        if len(embeddings) != len(texts):
            raise ValueError(

                f"Mismatch: requested {len(texts)} embeddings, got {len(embeddings)}. "

                "Some input texts were empty."

            )

        return embeddings