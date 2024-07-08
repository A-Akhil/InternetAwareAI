# server.py
from langchain_community.llms import Ollama
from typing import TypedDict
import langchain
from langgraph.graph import StateGraph
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END

def inputprocess(query: str):
    llm = Ollama(
        model="llama3"
    )
    search_engine = DuckDuckGoSearchRun()

    system_prompt = """You are given a user's query. If the query pertains to information that you do not have access to 
    or asking something which is a realtime data which you dont have access to, respond with string 'search_query' only nothing else. 
    even if you dont have access to realtime data just return the string 'search_query' and never say i don't know if you don't know reply as 'search_query'
    Otherwise, provide an answer based on your existing knowledge only if you are sure that you know about it."""

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "{input}")]
    )

    chain = prompt | llm

    class GraphState(TypedDict):
        question: str
        response: str

    def call_llm(state):
        question = state.get('question')
        print(f"call_llm: question = {question}")

        response = chain.invoke({"input": question})
        print(f"call_llm: response = {response}")

        return {"response": response}

    def search_tool(state):
        query = state.get("question")
        print(f"search_tool: query = {query}")

        result = {"User": query, "Search Results": search_engine.invoke(query)}
        print(f"search_tool: result = {result}")

        return {"question": str(result)}

    def should_search(state):
        response = state.get('response')
        print(f"should_search: response = {response}")

        if 'search_query' in response:
            return response
        else:
            return "end"

    workflow = StateGraph(GraphState)
    workflow.add_node("search_query", search_tool)
    workflow.add_node("call_llm", call_llm)
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
    result = graph.invoke({"question": query})

    print(f"Final result: {result['response']}")
    return result['response']

# Example usage
# query = "who won men's t20 2024"
# response = inputprocess(query)
# print(response)
