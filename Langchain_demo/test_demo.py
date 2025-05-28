"""
测试LangChain演示脚本
"""

import os
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import Tool

def test_langchain_demo():
    print("🚀 开始测试LangChain演示...")
    
    # 1. 测试API配置
    try:
        QWEN_API_KEY = "sk-ac968b8245624f3eb154bda6b13c2601"
        QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        llm = ChatOpenAI(
            openai_api_key=QWEN_API_KEY,
            model_name="qwen-plus",
            temperature=0.7,
            base_url=QWEN_BASE_URL
        )
        print("✅ LLM配置成功")
    except Exception as e:
        print(f"❌ LLM配置失败: {e}")
        return False
    
    # 2. 测试工具定义
    try:
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
        print("✅ 工具定义成功")
    except Exception as e:
        print(f"❌ 工具定义失败: {e}")
        return False
    
    # 3. 测试代理初始化
    try:
        agent = initialize_agent(
            tools=[add_tool],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        print("✅ 代理初始化成功")
    except Exception as e:
        print(f"❌ 代理初始化失败: {e}")
        return False
    
    # 4. 测试工具功能（不调用API）
    try:
        test_result = add_tool_func("1 2 3 4 5")
        expected = "Sum: 15.0"
        if test_result == expected:
            print(f"✅ 工具测试成功: {test_result}")
        else:
            print(f"❌ 工具测试失败: 期望 {expected}, 得到 {test_result}")
            return False
    except Exception as e:
        print(f"❌ 工具测试失败: {e}")
        return False
    
    print("🎉 所有测试通过！LangChain演示配置正确。")
    print("\n📝 要运行完整演示，请执行:")
    print("   python LangChain_Demo.py")
    print("\n⚠️  注意: 完整演示需要网络连接和有效的API密钥")
    
    return True

if __name__ == "__main__":
    test_langchain_demo() 