from langchain_community.llms import Ollama
from typing import TypedDict
import langchain
from langgraph.graph import StateGraph
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END


def inputprocess(query):
    llm = Ollama(
        model="llama3"
    )
    search_engine = DuckDuckGoSearchRun()

    system_prompt = f"""You are given a user's query. If the query pertains to information that you do not have access to, respond with string 'search_query' only nothing else. Otherwise, provide an answer based on your existing knowledge."""

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "{input}")]
    )

    chain = prompt | llm


    class GraphState(TypedDict):
        question: str = None
        response: str = None

    workflow = StateGraph(GraphState)

    def call_llm(state):
        question = state.get('question')
        print(f"call_llm: question = {question}")

        response = chain.invoke({"input": question}) 
        print(f"call_llm: response = {response}")

        return {"response": response}

    def search_tool(state):
        query = state.get("question")
        print(f"search_tool: query = {query}")

        result = {"User": query,
                "Search Results": search_engine.invoke(query)}
        print(f"search_tool: result = {result}")

        return {"question": str(result)}

    workflow.add_node("search_query", search_tool)
    workflow.add_node("call_llm", call_llm)

    def should_search(state):
        response = state.get('response')
        print(f"should_search: response = {response}")

        if 'search_query' in response:
            return response
        else:
            return "end"

    workflow.set_entry_point("call_llm")

    workflow.add_conditional_edges(
        "call_llm",
        should_search,
        {
            "end": END,
            "search_query": "search_query"
        }
    )

    workflow.add_edge('search_query', "call_llm")

    graph = workflow.compile()

    # Test it Out

    langchain.debug = True
    query = "who won 2024 loksabha elections in India?"
    result = graph.invoke({"question": query})

    print(f"Final result: {result['response']}")
    return(result['response'])
