import chainlit as cl

# Comment out the OpenAI client setup
# client = AsyncOpenAI(base_url="http://localhost:8080/v1", api_key="fake-key")
# cl.instrument_openai()

settings = {
    "model": "llama3-8b",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )

@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    query = input("Please enter your query: ")
    print(f"Query received: {query}")
# Call the main function directly for testing purposes
if __name__ == "__main__":
    start_chat()
    while True:
        main(cl.Message(content=input("Enter your message: ")))
