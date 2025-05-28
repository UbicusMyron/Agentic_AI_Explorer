"""
测试更新版本的LangChain演示脚本
"""

import os
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI  # Updated import
from langchain.tools import Tool

def test_updated_demo():
    print("🚀 开始测试更新版本的LangChain演示...")
    
    # 1. 测试API配置
    try:
        QWEN_API_KEY = "sk-ac968b8245624f3eb154bda6b13c2601"
        QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        llm = ChatOpenAI(
            api_key=QWEN_API_KEY,
            model="qwen-plus",
            temperature=0.7,
            base_url=QWEN_BASE_URL
        )
        print("✅ 更新版LLM配置成功")
    except Exception as e:
        print(f"❌ LLM配置失败: {e}")
        return False
    
    # 2. 测试工具定义
    try:
        def add_tool_func(input_text: str) -> str:
            try:
                numbers = [float(x) for x in input_text.strip().split()]
                return f"Sum: {sum(numbers)}"
            except Exception:
                return "Error: Please provide numbers separated by spaces."

        def multiply_tool_func(input_text: str) -> str:
            try:
                numbers = [float(x) for x in input_text.strip().split()]
                result = 1
                for num in numbers:
                    result *= num
                return f"Product: {result}"
            except Exception:
                return "Error: Please provide numbers separated by spaces."

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
        print("✅ 工具定义成功（加法和乘法）")
    except Exception as e:
        print(f"❌ 工具定义失败: {e}")
        return False
    
    # 3. 测试代理初始化
    try:
        agent = initialize_agent(
            tools=[add_tool, multiply_tool],
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        print("✅ 代理初始化成功")
    except Exception as e:
        print(f"❌ 代理初始化失败: {e}")
        return False
    
    # 4. 测试工具功能
    try:
        # 测试加法工具
        add_result = add_tool_func("1 2 3 4 5")
        expected_add = "Sum: 15.0"
        if add_result == expected_add:
            print(f"✅ 加法工具测试成功: {add_result}")
        else:
            print(f"❌ 加法工具测试失败: 期望 {expected_add}, 得到 {add_result}")
            return False
            
        # 测试乘法工具
        multiply_result = multiply_tool_func("2 3 4")
        expected_multiply = "Product: 24.0"
        if multiply_result == expected_multiply:
            print(f"✅ 乘法工具测试成功: {multiply_result}")
        else:
            print(f"❌ 乘法工具测试失败: 期望 {expected_multiply}, 得到 {multiply_result}")
            return False
            
    except Exception as e:
        print(f"❌ 工具测试失败: {e}")
        return False
    
    print("🎉 所有测试通过！更新版本LangChain演示配置正确。")
    print("\n📝 要运行完整演示，请执行:")
    print("   python LangChain_Demo_Updated.py")
    print("\n✨ 新功能:")
    print("   - 使用最新的langchain-openai包")
    print("   - 添加了乘法工具")
    print("   - 改进的错误处理")
    print("   - 更好的用户界面")
    print("\n⚠️  注意: 完整演示需要网络连接和有效的API密钥")
    
    return True

if __name__ == "__main__":
    test_updated_demo() 