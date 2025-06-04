#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购物助手功能演示脚本
"""

import asyncio
from SupportFunction import QueryParser, MCPProductSearch, format_product_results


async def demo_query_parsing():
    """演示查询解析功能"""
    print("🔍 查询解析功能演示")
    print("=" * 40)
    
    parser = QueryParser()
    test_queries = [
        "我想在北京买一部手机",
        "帮我找找深圳的笔记本电脑，预算5000元",
        "上海的运动鞋",
        "想要购买广州的iPhone，预算8000元左右",
        "需要一台游戏本，在杭州"
    ]
    
    for query in test_queries:
        result = parser.parse_query(query)
        print(f"查询: {query}")
        print(f"  - 商品: {result['product']}")
        print(f"  - 地点: {result['location']}")
        print(f"  - 预算: {result['budget'] or '未指定'}")
        print()


async def demo_product_search():
    """演示商品搜索功能"""
    print("🛍️ 商品搜索功能演示")
    print("=" * 40)
    
    mcp_search = MCPProductSearch()
    
    # 测试不同类型的商品搜索
    search_tests = [
        ("手机", "北京", "taobao"),
        ("笔记本", "上海", "jd"),
        ("运动鞋", "深圳", "taobao"),
    ]
    
    for query, location, platform in search_tests:
        print(f"\n🔎 搜索: {query} (地点: {location}, 平台: {platform})")
        print("-" * 30)
        
        products = await mcp_search.search_products(query, location, platform)
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name}")
            print(f"   💰 价格: {product.price}")
            print(f"   📝 描述: {product.description}")
            print(f"   🔗 链接: {product.url}")
            print()


async def demo_complete_workflow():
    """演示完整工作流程"""
    print("🚀 完整工作流程演示")
    print("=" * 40)
    
    parser = QueryParser()
    mcp_search = MCPProductSearch()
    
    user_query = "我想在北京买一部手机，预算6000元"
    
    print(f"用户查询: {user_query}")
    print()
    
    # 步骤1: 解析查询
    parsed = parser.parse_query(user_query)
    print("🔍 查询解析结果:")
    print(f"  商品: {parsed['product']}")
    print(f"  地点: {parsed['location']}")
    print(f"  预算: {parsed['budget']}元")
    print()
    
    # 步骤2: 搜索商品
    print("🛍️ 商品搜索结果:")
    products = await mcp_search.search_products(
        parsed['product'], 
        parsed['location'], 
        'taobao'
    )
    
    # 步骤3: 格式化输出
    formatted_results = format_product_results(products)
    print(formatted_results)
    
    # 步骤4: 预算筛选
    budget = int(parsed['budget']) if parsed['budget'] else float('inf')
    print("💰 预算筛选结果:")
    suitable_products = []
    
    for product in products:
        # 简单的价格提取（实际项目中需要更复杂的解析）
        price_str = product.price.replace('¥', '').replace(',', '')
        try:
            price = int(price_str)
            if price <= budget:
                suitable_products.append(product)
                print(f"✅ {product.name} - {product.price} (符合预算)")
            else:
                print(f"❌ {product.name} - {product.price} (超出预算)")
        except:
            print(f"⚠️ {product.name} - {product.price} (价格解析失败)")
    
    print(f"\n🎯 找到 {len(suitable_products)} 个符合预算的商品!")


async def main():
    """主演示函数"""
    print("🛍️ 智能购物助手 - 功能演示")
    print("基于 LangChain + MCP 架构")
    print("=" * 50)
    
    # 演示1: 查询解析
    await demo_query_parsing()
    
    print("\n" + "=" * 50)
    
    # 演示2: 商品搜索
    await demo_product_search()
    
    print("\n" + "=" * 50)
    
    # 演示3: 完整工作流程
    await demo_complete_workflow()
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print("💡 运行 'python main.py' 开始完整的购物助手体验")


if __name__ == "__main__":
    asyncio.run(main()) 