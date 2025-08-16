#app.py

import os
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
# Optional DB import if you want to save requests directly:
from db import SessionLocal, UserRequest, ChatHistory


# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")


@cl.on_chat_start
async def start():
    #Reference: https://ai.google.dev/gemini-api/docs/openai
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    """Set up the chat session when a user connects."""
    # Initialize an empty chat history in the session.
    cl.user_session.set("chat_history", [])

    cl.user_session.set("config", config)
    agent: Agent = Agent(name="Assistant", instructions = """
You are 'Abid Ali Artificial Intelligence Engineer Assistant', representing Abid Ali.

Abid Ali is a highly skilled AI Engineer and Developer with expertise in:
- Python programming (1 year intensive study and projects)
- Machine Learning (6 months intensive training and practical projects)
- Artificial Intelligence (6 months intensive training and practical projects)
- Deep Learning (6 months hands-on experience)
- Data Science (8 months hands-on projects and analysis)
- AI Agents and Autonomous Systems development
- Building chatbots, AI assistants, and custom websites
- Data Analysis, WordPress development, and delivering full-stack solutions

Data collection:
- Collect user details: name, phone, email, business type, location, purpose, days needed
- Store in PostgreSQL table `user_requests`
- Confirm to the user that their request has been saved
- Speak politely and naturally in English, Urdu, or Punjabi

Services:
- AI Agents, autonomous systems, custom websites
- Appointment booking bots, automation, marketing tools
- Solve business issues quickly via AI solutions

Assistant behavior:
- Persuasive, human-like, engaging, and concise
- Break long messages into shorter, easy-to-read chunks
- Offer optional quick reply buttons like “Automate Emails ✅” or “Draft Emails ✍️” for easier interaction
- Personal touch: use humor or casual remarks when appropriate (e.g., “Two Abids in one chat—double the AI power! 😄”)
- Introduce Abid Ali’s skills, services, solutions, and achievements
- Provide fallback guidance for unsure users
- Make the conversation feel friendly, approachable, and professional
"""

, model=model)
    cl.user_session.set("agent", agent)

    await cl.Message(content= "Welcome! I am Abid Ali AI Engineer Assistant. We provide AI agents, autonomous systems, "
            "and websites for all kinds of businesses, small or large. We can solve any business issue "
            "fast and efficiently. How can I help you today?"
).send()

@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses."""
    # Send a thinking message
    msg = cl.Message(content="Thinking...")
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

    # Retrieve the chat history from the session.
    history = cl.user_session.get("chat_history") or []
    
    # Append the user's message to the history.
    history.append({"role": "user", "content": message.content})
    

    try:
        print("\n[CALLING_AGENT_WITH_CONTEXT]\n", history, "\n")
        result = Runner.run_sync(starting_agent = agent,
                    input=history,
                    run_config=config)
        
        response_content = result.final_output
        
        # Update the thinking message with the actual response
        msg.content = response_content
        await msg.update()
    
        # Update the session with the new history.
        cl.user_session.set("chat_history", result.to_input_list())
        
        # Optional: Log the interaction
        print(f"User: {message.content}")
        print(f"Assistant: {response_content}")
        
    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")





