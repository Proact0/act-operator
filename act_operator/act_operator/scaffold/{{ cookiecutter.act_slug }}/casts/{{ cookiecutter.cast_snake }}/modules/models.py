"""[Optional] Model configuration helpers for the {{ cookiecutter.cast_name }} graph.

Guidelines:
    - Provide factory functions for LLMs or embeddings.
    - Accept environment variables or configuration values when necessary.

Official document URL:
    - Models: https://docs.langchain.com/oss/python/langchain/models
    - Chat Models: https://docs.langchain.com/oss/python/integrations/chat
    - Embedding Models: https://docs.langchain.com/oss/python/integrations/text_embedding
"""

{% if cookiecutter.rag|string|lower in ['true', '1'] %}
import os
from typing import Any


def get_embedding_model() -> Any:
    """Embedding model factory function for RAG retrieval.

    Returns:
        Configured embeddings instance (e.g., OpenAIEmbeddings, HuggingFaceEmbeddings).
    """
    try:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    except ImportError:
        return None


def get_chat_model() -> Any:
    """Chat model factory function."""
    try:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    except ImportError:
        return None
{% else %}
# from langchain.chat_models import init_chat_model
# from langchain_openai import ChatOpenAI


def get_sample_model():
    # return init_chat_model(
    #     model="",
    #     model_provider="openai",
    # )
    pass
{% endif %}
