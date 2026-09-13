from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.services.llm import get_chat_model
from app.services.tools import get_tools

BASE_SYSTEM_PROMPT = (
    "You are a helpful, precise assistant powered by Google Gemini. "
    "Answer clearly and concisely. If context from the user's documents is provided below, "
    "prioritize it and cite it naturally; if it doesn't answer the question, say so and use "
    "your own knowledge or tools instead."
)


def _build_system_message(rag_context: list[str]) -> SystemMessage:
    if not rag_context:
        return SystemMessage(content=BASE_SYSTEM_PROMPT)

    context_block = "\n\n".join(f"[Doc {i + 1}] {chunk}" for i, chunk in enumerate(rag_context))
    return SystemMessage(
        content=f"{BASE_SYSTEM_PROMPT}\n\nRelevant context from the user's documents:\n{context_block}"
    )


async def run_agent(
    user_message: str,
    history: list[BaseMessage],
    rag_context: list[str],
    use_tools: bool = True,
) -> str:
    """Runs one turn: injects RAG context + short-term memory, optionally lets Gemini
    call tools (web search / calculator / custom), and returns the final text reply."""
    system_message = _build_system_message(rag_context)

    if use_tools:
        llm = get_chat_model()
        tools = get_tools()
        prompt = ChatPromptTemplate.from_messages(
            [
                system_message,
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)
        result = await executor.ainvoke({"input": user_message, "chat_history": history})
        return result["output"]

    # Simple RAG/chat path without tool-calling
    llm = get_chat_model()
    messages = [system_message, *history, ("human", user_message)]
    response = await llm.ainvoke(messages)
    return response.content
