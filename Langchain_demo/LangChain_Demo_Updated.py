"""
LangChain Qwen Agent Demo (Updated Version)

This script demonstrates how to run a LangChain agent locally using the Qwen large language model API.
Updated to use the latest LangChain packages and best practices.

Prerequisites:
- Python 3.10+
- Install dependencies: pip install langchain langchain-openai langchain-community
- Set your Qwen API Key (sk-ac968b8245624f3eb154bda6b13c2601)
"""

import os
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI  # Updated import
from langchain.tools import Tool

# 1. Set your Qwen API key directly (or use an environment variable)
QWEN_API_KEY = "sk-ac968b8245624f3eb154bda6b13c2601"

# 2. Specify Qwen's API base URL
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # Qwen's OpenAI-compatible endpoint

# 3. Initialize LLM with Qwen (using updated import)
llm = ChatOpenAI(
    api_key=QWEN_API_KEY,  # Updated parameter name
    model="qwen-plus",     # Updated parameter name
    temperature=0.7,
    base_url=QWEN_BASE_URL
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

# 5. Define a multiplication tool
def multiply_tool_func(input_text: str) -> str:
    """
    Parse the input string and multiply all the numbers separated by spaces.
    """
    try:
        numbers = [float(x) for x in input_text.strip().split()]
        result = 1
        for num in numbers:
            result *= num
        return f"Product: {result}"
    except Exception:
        return "Error: Please provide numbers separated by spaces."

# Create tools
add_tool = Tool(
    name="AddNumbers",
    func=add_tool_func,
    description="Use this tool to add a list of numbers separated by spaces."
)

multiply_tool = Tool(
    name="MultiplyNumbers", 
    func=multiply_tool_func,
    description="Use this tool to multiply a list of numbers separated by spaces."
)

# 6. Initialize the agent with the LLM and tools
agent = initialize_agent(
    tools=[add_tool, multiply_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def main():
    """Main function to run the interactive chat"""
    print("🤖 Welcome to your LangChain Agent (Qwen model)!")
    print("📝 Available tools: AddNumbers, MultiplyNumbers")
    print("💡 Example: 'Add 1 2 3 4 5' or 'Multiply 2 3 4'")
    print("🚪 Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower().strip() == 'exit':
                print("👋 Goodbye!")
                break
            
            if not user_input.strip():
                print("Please enter a question or command.")
                continue
                
            response = agent.run(user_input)
            print(f"Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'exit' to quit.\n")

if __name__ == "__main__":
    main() 