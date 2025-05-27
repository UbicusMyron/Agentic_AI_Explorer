"""
LangChain Qwen Agent Demo

This script demonstrates how to run a LangChain agent locally using the Qwen large language model API.

Prerequisites:
- Python 3.10+
- Install dependencies: pip install langchain langchain-community openai
- Set your Qwen API Key (sk-ac968b8245624f3eb154bda6b13c2601)
"""

import os
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import Tool

# 1. Set your Qwen API key directly (or use an environment variable)
QWEN_API_KEY = "sk-ac968b8245624f3eb154bda6b13c2601"

# 2. Specify Qwen's API base URL
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # Qwen's OpenAI-compatible endpoint

# 3. Initialize LLM with Qwen
llm = ChatOpenAI(
    openai_api_key=QWEN_API_KEY,
    model_name="qwen-plus",       # Use your actual model name, e.g., "qwen-plus", "qwen1.5-72b-chat", etc.
    temperature=0.7,
    base_url=QWEN_BASE_URL        # Set if your Qwen endpoint is not the OpenAI default
)

# 4. Define a simple math tool (add numbers)
def add_tool_func(input_text: str) -> str:
    """
    Parse the input string and sum all the numbers separated by spaces.
    """
    try:
        numbers = [float(x) for x in input_text.strip().split()]
        return f"Sum: {sum(numbers)}"
    except Exception:
        return "Error: Please provide numbers separated by spaces."

add_tool = Tool(
    name="AddNumbers",
    func=add_tool_func,
    description="Use this tool to add a list of numbers separated by spaces."
)

# 5. Initialize the agent with the LLM and tools
agent = initialize_agent(
    tools=[add_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 6. Start a command-line loop for interactive chat
print("Welcome to your LangChain Agent (Qwen model)! Type 'exit' to quit.")
while True:
    user_input = input("User: ")
    if user_input.lower().strip() == 'exit':
        print("Goodbye!")
        break
    response = agent.run(user_input)
    print(f"Agent: {response}")
