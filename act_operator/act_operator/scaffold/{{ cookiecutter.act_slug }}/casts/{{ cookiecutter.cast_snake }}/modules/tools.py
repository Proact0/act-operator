"""[Optional] LLM tools or Model Context Protocol (MCP) adapters for the agents.

Guidelines:
    - Wrap side-effecting operations (API calls, filesystem access, etc.).
    - Register your tools or MCP adapters with agents for LLM integration.
    - If you use MCP adapters, you need langchain-mcp-adapters package installed. (`uv add langchain-mcp-adapters --package {{ cookiecutter.cast_slug }}`)

Official document URL:
    - Tools: https://docs.langchain.com/oss/python/langchain/tools
    - MCP Adapters: https://docs.langchain.com/oss/python/langchain/mcp
"""

{% if cookiecutter.rag|string|lower in ['true', '1'] %}
from langchain_core.documents import Document
from langchain_core.tools import tool

# Sample knowledge base documents for out-of-the-box demonstration
SAMPLE_KNOWLEDGE_BASE = [
    Document(
        page_content="Act Operator is a CLI scaffolding tool for modular LangGraph projects.",
        metadata={"source": "overview"},
    ),
    Document(
        page_content="A Cast represents an independent StateGraph package within an Act monorepo.",
        metadata={"source": "architecture"},
    ),
]


@tool
def retrieve_documents(query: str) -> str:
    """Retrieve relevant documents matching the search query.

    Args:
        query: Search keywords or question.

    Returns:
        Formatted context string of matching documents.
    """
    query_lower = query.lower()
    matches = [
        f"[{doc.metadata.get('source', 'doc')}]: {doc.page_content}"
        for doc in SAMPLE_KNOWLEDGE_BASE
        if any(term in doc.page_content.lower() for term in query_lower.split())
    ]
    if not matches:
        # Fallback to returning sample documents as demonstration
        return "\n\n".join(
            f"[{doc.metadata.get('source', 'doc')}]: {doc.page_content}"
            for doc in SAMPLE_KNOWLEDGE_BASE
        )
    return "\n\n".join(matches)
{% endif %}
