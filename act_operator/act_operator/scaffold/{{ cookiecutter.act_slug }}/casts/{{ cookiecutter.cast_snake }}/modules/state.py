"""[Required] State definition for the {{ cookiecutter.cast_name }} graph.

Guidelines:
    - Create TypedDict classes for input, output, overall state, and any other state you need.
    - Use `MessagesState` from langgraph.graph or use `Annotated[list[AnyMessage], add_messages]` for messages to enable proper message merging.
    - When inheriting from MessagesState, do not override the messages field.

Official document URL:
    - State: https://docs.langchain.com/oss/python/langgraph/graph-api#state
"""

from langgraph.graph import MessagesState
from typing_extensions import TypedDict


class InputState(TypedDict):
    """Input state container.

    Attributes:
        query: User query
    """

    query: str


{% if cookiecutter.rag|string|lower in ['true', '1'] %}
class OutputState(TypedDict):
    """Output state container.

    Attributes:
        result: Generated answer
        context: Retrieved context documents
        retrieved_docs: List of retrieved document contents
    """

    result: str
    context: str
    retrieved_docs: list[str]


class State(MessagesState):
    """Graph state container for RAG.

    Attributes:
        query: User query
        result: Generated answer
        context: Retrieved context documents
        retrieved_docs: List of retrieved document contents
        messages: Additional messages (inherited from MessagesState)
    """

    result: str
    query: str
    context: str
    retrieved_docs: list[str]
{% else %}
class OutputState(TypedDict):
    """Output state container.

    Attributes:
        messages: Additional messages (inherited from MessagesState)
    """

    result: str


class State(MessagesState):
    """Graph state container.

    Attributes:
        query: User query
        messages: Additional messages (inherited from MessagesState)
    """

    # messages field is inherited from MessagesState
    # It is defined as: messages: Annotated[list[AnyMessage], add_messages]
    result: str
    query: str
{% endif %}
