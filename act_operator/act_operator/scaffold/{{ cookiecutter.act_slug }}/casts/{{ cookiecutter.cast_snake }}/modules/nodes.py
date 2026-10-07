"""[Required] Node implementations for the {{ cookiecutter.cast_name }} graph.

Guidelines:
    - Derive each node from :class:`BaseNode` or :class:`AsyncBaseNode`.
    - Implement :meth:`execute` to process state and return updates.
    - Choose your node signature based on what you need:
      * Simple: `def execute(self, state)` - Only needs state
      * With config: `def execute(self, state, config)` - Needs thread_id, tags
      * With runtime: `def execute(self, state, runtime)` - Needs store, stream
      * Full: `def execute(self, state, config, runtime)` - Needs everything
    - Use `self.log()` for debugging when `verbose=True`.

Official document URL:
    - Nodes: https://docs.langchain.com/oss/python/langgraph/graph-api#nodes
"""

from langchain_core.messages import AIMessage

from casts.base_node import AsyncBaseNode, BaseNode


{% if cookiecutter.rag|string|lower in ['true', '1'] %}
from casts.{{ cookiecutter.cast_snake }}.modules.tools import retrieve_documents


class SampleNode(BaseNode):
    """RAG-enabled sync node that retrieves relevant context and answers.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self):
        super().__init__()

    def execute(self, state):
        """Execute the RAG node.

        Args:
            state: Current graph state containing user query.

        Returns:
            dict: State updates with retrieved context, docs, result, and messages.
        """
        query = state.get("query", "")
        context = retrieve_documents.invoke(query)
        welcome = "Welcome to the Act!"
        return {
            "result": welcome,
            "context": context,
            "retrieved_docs": [context],
            "messages": [AIMessage(content=f"{welcome} (Context: {context})")],
        }
{% else %}
class SampleNode(BaseNode):
    """Simple sync node - only uses state.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self):
        super().__init__()

    def execute(self, state):
        """Execute the sample node.

        Args:
            state: Current graph state.

        Returns:
            dict: State updates (must be a dict). Writes both ``result``
            (exposed by OutputState) and ``messages`` (accumulated via
            MessagesState's ``add_messages`` reducer).
        """
        welcome = "Welcome to the Act!"
        return {
            "result": welcome,
            "messages": [AIMessage(content=f"{welcome} by Sync Node")],
        }
{% endif %}


class AsyncSampleNode(AsyncBaseNode):
    """Simple async node - only uses state.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self):
        super().__init__()

    async def execute(self, state):
        """Execute the sample node.

        Args:
            state: Current graph state.

        Returns:
            dict: State updates (must be a dict). Writes both ``result``
            (exposed by OutputState) and ``messages`` (accumulated via
            MessagesState's ``add_messages`` reducer).
        """
        welcome = "Welcome to the Act!"
        return {
            "result": welcome,
            "messages": [AIMessage(content=f"{welcome} by Async Node")],
        }
