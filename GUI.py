# # GUI.py
import chainlit as cl
from server import inputprocess

@cl.on_message
async def on_message(message: cl.Message):
    # Extract the content of the message
    query = message.content
    
    # Process the query
    response = inputprocess(query)
    
    # Send the response back
    await cl.Message(content=response).send()