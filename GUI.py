# GUI.py
import os
from langchain.chains import LLMChain
import chainlit as cl
from server import inputprocess

# Define the factory function to create the LLMChain
def factory(query):
    llm_chain = inputprocess(query)
    return llm_chain

# Define the on_message callback
@cl.on_message
async def on_message(message):
    llm_chain = factory(message)  # Pass 'message' as the query
    response = llm_chain({"input": message})
    await cl.send_message(response)
