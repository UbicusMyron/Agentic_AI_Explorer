#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购物助手Agent - 基于LangChain和MCP的智能购物助手
"""

import asyncio
import os
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

# LangChain imports
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_core.tools import StructuredTool

# 本地模块
from SupportFunction import (
    MCPProductSearch, ImageProcessor, QueryParser, 
    ProductInfo, format_product_results, validate_api_key,
    filter_products_by_budget, get_api_error_message
)


class ShoppingAssistantAgent:
    """购物助手智能代理"""
    
    def __init__(self):
        self.api_keys = {}
        self.current_llm = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        self.mcp_search = MCPProductSearch()
        self.image_processor = ImageProcessor()
        self.query_parser = QueryParser()
        self.conversation_history = []
        
        # 初始化工具
        self.tools = self._create_tools()
        
        # 创建图片保存目录
        os.makedirs("images", exist_ok=True)
    
    def setup_api_keys(self):
        """设置API密钥"""
        print("🔧 购物助手初始化设置")
        print("\n⚠️  重要提示：")
        print("   真实商品搜索需要配置各平台的API密钥")
        print("   当前版本提供API调用框架，需要您补充真实密钥")
        print("   详情请查看 SupportFunction.py 中的API配置")
        
        print("\n请选择您要使用的AI服务商：")
        print("1. Qwen (默认)")
        print("2. OpenAI") 
        print("3. 跳过设置（使用模拟模式）")
        
        choice = input("\n请输入选择 (1-3，直接回车使用Qwen): ").strip()
        
        # 默认使用Qwen
        if choice == "" or choice == "1":
            # 使用提供的Qwen API Key
            default_qwen_key = "sk-ac968b8245624f3eb154bda6b13c2601"
            self.api_keys["qwen"] = default_qwen_key
            self._setup_qwen_llm(default_qwen_key)
            print("✅ 使用默认Qwen API，设置成功！")
                
        elif choice == "2":
            # 使用提供的OpenAI API Key
            default_openai_key = "sk-icrnsxtreopiwjmgtdwbcxxpumemnbqdinnfagjraaxvtzfo"
            self.api_keys["openai"] = default_openai_key
            self._setup_openai_llm(default_openai_key)
            print("✅ 使用默认OpenAI API，设置成功！")
                
        elif choice == "3":
            print("⚠️ 使用模拟模式，AI功能将受限")
            self._setup_default_llm()
        else:
            print("❌ 无效选择，使用默认Qwen设置")
            default_qwen_key = "sk-ac968b8245624f3eb154bda6b13c2601"
            self.api_keys["qwen"] = default_qwen_key
            self._setup_qwen_llm(default_qwen_key)
            print("✅ 使用默认Qwen API，设置成功！")
        
        # 检查商品搜索API配置
        print("\n🛍️ 商品搜索API状态检查：")
        self._check_ecommerce_api_status()
    
    def _setup_qwen_llm(self, api_key: str):
        """设置Qwen LLM"""
        try:
            # 注意：这里使用OpenAI兼容接口，实际项目中需要配置Qwen的具体API
            self.current_llm = ChatOpenAI(
                model="qwen-plus",  # 或其他Qwen模型
                openai_api_key=api_key,
                openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",  # Qwen API端点
                temperature=0.7,
                max_tokens=2000
            )
        except Exception as e:
            print(f"❌ Qwen LLM 设置失败: {e}")
            self._setup_default_llm()
    
    def _setup_openai_llm(self, api_key: str):
        """设置OpenAI LLM"""
        try:
            self.current_llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=api_key,
                temperature=0.7,
                max_tokens=2000
            )
        except Exception as e:
            print(f"❌ OpenAI LLM 设置失败: {e}")
            self._setup_default_llm()
    
    def _setup_default_llm(self):
        """设置默认LLM（模拟）"""
        print("🤖 使用默认AI模拟器")
        self.current_llm = None  # 将使用模拟响应
    
    def _check_ecommerce_api_status(self):
        """检查电商API配置状态"""
        try:
            # 检查淘宝API配置
            taobao_status = "❌ 需要配置" if self.mcp_search.taobao_api_config['app_key'] == '12345678' else "✅ 已配置"
            print(f"   淘宝API: {taobao_status}")
            
            # 检查京东API配置
            jd_status = "❌ 需要配置" if self.mcp_search.jd_api_config['app_key'] == 'your_jd_app_key' else "✅ 已配置"
            print(f"   京东API: {jd_status}")
            
            # 检查亚马逊API配置
            amazon_status = "❌ 需要配置" if self.mcp_search.amazon_api_config['access_key'] == 'your_access_key' else "✅ 已配置"
            print(f"   亚马逊API: {amazon_status}")
            
            if "❌" in [taobao_status, jd_status, amazon_status]:
                print("\n💡 配置真实API密钥步骤：")
                print("   1. 打开 SupportFunction.py 文件")
                print("   2. 找到对应平台的API配置部分")
                print("   3. 替换为您的真实API密钥")
                print("   4. 重新运行程序")
            
        except Exception as e:
            print(f"   ⚠️ API状态检查失败: {e}")
    
    def _create_tools(self) -> List[Tool]:
        """创建LangChain工具"""
        
        async def search_products_tool(query: str, location: str = "中国", 
                                     platform: str = "taobao") -> str:
            """搜索商品工具"""
            try:
                products = await self.mcp_search.search_products(query, location, platform)
                return format_product_results(products)
            except Exception as e:
                return f"搜索失败: {str(e)}"
        
        def parse_query_tool(query: str) -> str:
            """解析查询工具"""
            try:
                parsed = self.query_parser.parse_query(query)
                return json.dumps(parsed, ensure_ascii=False, indent=2)
            except Exception as e:
                return f"查询解析失败: {str(e)}"
        
        def download_image_tool(url: str, filename: str = None) -> str:
            """下载图片工具"""
            try:
                if not filename:
                    filename = f"product_{len(os.listdir('images')) + 1}.jpg"
                
                save_path = os.path.join("images", filename)
                
                if self.image_processor.download_image(url, save_path):
                    return f"图片已保存到: {save_path}"
                else:
                    # 创建占位图片
                    if self.image_processor.create_placeholder_image("商品图片", save_path):
                        return f"已创建占位图片: {save_path}"
                    return "图片处理失败"
            except Exception as e:
                return f"图片下载失败: {str(e)}"
        
        return [
            Tool(
                name="search_products",
                description="搜索商品信息，参数：query(商品关键词), location(地点，默认中国), platform(平台，默认taobao)",
                func=lambda q, l="中国", p="taobao": asyncio.run(search_products_tool(q, l, p))
            ),
            Tool(
                name="parse_query", 
                description="解析用户自然语言查询，提取商品、地点、预算等信息",
                func=parse_query_tool
            ),
            Tool(
                name="download_image",
                description="下载商品图片到本地，参数：url(图片链接), filename(可选，文件名)",
                func=download_image_tool
            )
        ]
    
    async def process_query(self, user_input: str) -> str:
        """处理用户查询"""
        print(f"\n🔍 正在处理查询: {user_input}")
        
        # 解析查询
        parsed_query = self.query_parser.parse_query(user_input)
        print(f"📝 查询解析结果: {json.dumps(parsed_query, ensure_ascii=False)}")
        
        # 如果有LLM，使用智能代理
        if self.current_llm:
            return await self._process_with_llm(user_input, parsed_query)
        else:
            return await self._process_with_simulation(user_input, parsed_query)
    
    async def _process_with_llm(self, user_input: str, parsed_query: Dict) -> str:
        """使用LLM处理查询"""
        try:
            # 创建ChatBot Agent
            chatbot_prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个专业的购物助手。你的任务是：
1. 理解用户的购买需求
2. 使用工具搜索相关商品  
3. 为用户提供购买建议
4. 下载商品图片供用户查看

请用友好、专业的语气回应用户。"""),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad")
            ])
            
            # 创建代理
            agent = create_openai_functions_agent(
                self.current_llm,
                self.tools,
                chatbot_prompt
            )
            
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True
            )
            
            # 执行查询
            result = await agent_executor.ainvoke({
                "input": user_input,
                "chat_history": self.conversation_history
            })
            
            # 更新对话历史
            self.conversation_history.extend([
                HumanMessage(content=user_input),
                AIMessage(content=result["output"])
            ])
            
            return result["output"]
            
        except Exception as e:
            print(f"❌ LLM处理失败: {e}")
            return await self._process_with_simulation(user_input, parsed_query)
    
    async def _process_with_simulation(self, user_input: str, parsed_query: Dict) -> str:
        """模拟处理（当没有LLM时）"""
        try:
            # 搜索商品
            products = await self.mcp_search.search_products(
                parsed_query['product'],
                parsed_query['location'],
                'taobao'
            )
            
            # 如果没有找到商品，尝试其他平台
            if not products:
                print("🔄 淘宝搜索无结果，尝试京东...")
                products = await self.mcp_search.search_products(
                    parsed_query['product'],
                    parsed_query['location'],
                    'jd'
                )
            
            # 如果仍然没有结果，给出提示
            if not products:
                return (f"🤖 购物助手为您服务！\n\n"
                       f"📊 查询分析：\n"
                       f"   商品: {parsed_query['product']}\n"
                       f"   地点: {parsed_query['location']}\n"
                       f"   预算: {parsed_query['budget'] or '未指定'}元\n\n"
                       f"❌ 很抱歉，暂时无法获取真实商品数据。\n"
                       f"💡 可能的原因：\n"
                       f"   1. API配置不完整（需要真实的API密钥）\n"
                       f"   2. 网络连接问题\n"
                       f"   3. 搜索关键词过于特殊\n\n"
                       f"🔧 建议：\n"
                       f"   - 检查SupportFunction.py中的API配置\n"
                       f"   - 尝试更通用的搜索关键词\n"
                       f"   - 确保网络连接正常")
            
            # 根据预算筛选商品
            budget_min = parsed_query.get('budget_min')
            budget_max = parsed_query.get('budget_max')
            
            # 如果有单一预算值，转换为上限
            if parsed_query.get('budget') and not budget_min and not budget_max:
                try:
                    budget_value = int(parsed_query['budget'])
                    budget_max = budget_value
                except (ValueError, TypeError):
                    pass
            
            # 筛选符合预算的商品
            if budget_min or budget_max:
                original_count = len(products)
                products = filter_products_by_budget(products, budget_min, budget_max)
                
                if len(products) < original_count:
                    print(f"💰 已根据预算筛选，从{original_count}个商品中筛选出{len(products)}个符合预算的商品")
            
            response = f"🤖 购物助手为您服务！\n\n"
            response += f"📊 查询分析：\n"
            response += f"   商品: {parsed_query['product']}\n"
            response += f"   地点: {parsed_query['location']}\n"
            
            if parsed_query['budget']:
                response += f"   预算: {parsed_query['budget']}元\n"
            
            response += f"\n{format_product_results(products)}"
            
            # 下载第一个商品的图片（如果有）
            if products and products[0].image_url:
                try:
                    image_result = self.tools[2].func(products[0].image_url)
                    response += f"\n📷 {image_result}"
                except Exception as e:
                    print(f"⚠️ 图片下载失败: {e}")
            
            # 如果经过预算筛选后没有商品，给出建议
            if not products and (budget_min or budget_max):
                response += f"\n💡 预算筛选后无匹配商品，建议：\n"
                response += f"   - 适当调整预算范围\n"
                response += f"   - 尝试不同的商品关键词\n"
                response += f"   - 查看其他电商平台"
            
            return response
            
        except Exception as e:
            return f"❌ 处理查询时出错: {str(e)}\n💡 请检查网络连接和API配置"
    
    def run_interactive(self):
        """运行交互式购物助手"""
        print("🛍️ 欢迎使用智能购物助手！")
        print("💡 您可以说：'我想在北京买一部手机'、'帮我找找深圳的笔记本电脑'等")
        print("📝 输入 'quit' 或 'exit' 退出\n")
        
        while True:
            try:
                user_input = input("👤 您: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 谢谢使用，再见！")
                    break
                
                if not user_input:
                    continue
                
                # 处理查询
                response = asyncio.run(self.process_query(user_input))
                print(f"\n🤖 购物助手: {response}\n")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 程序已退出，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")


def main():
    """主函数"""
    print("🛍️ 智能购物助手 v1.0")
    print("基于 LangChain + MCP 架构\n")
    
    try:
        # 创建购物助手
        assistant = ShoppingAssistantAgent()
        
        # 设置API
        assistant.setup_api_keys()
        
        print("\n" + "="*50)
        
        # 运行交互式助手
        assistant.run_interactive()
        
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
