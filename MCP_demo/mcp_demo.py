import os
import json
import csv
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any, Optional
from http import HTTPStatus
import re
from bs4 import BeautifulSoup
import difflib

# 导入AI API包，并处理不同版本
try:
    import openai
    # 检查OpenAI版本
    OPENAI_NEW_VERSION = hasattr(openai, '__version__') and openai.__version__ >= '1.0.0'
    if OPENAI_NEW_VERSION:
        from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OPENAI_NEW_VERSION = False

try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

# 导入本地函数模块 - 可替换为其他功能模块
from tax_calculator import (
    calculate_monthly_tax_from_salary,
    calculate_yearly_tax_from_salary,
    calculate_individual_income_tax_from_salary
)

class MCPDemo:
    """MCP Demo主类 - 可扩展的AI助手框架"""
    
    def __init__(self):
        """初始化配置"""
        self.openai_api_key = "sk-icrnsxtreopiwjmgtdwbcxxpumemnbqdinnfagjraaxvtzfo"
        self.qwen_api_key = "sk-ac968b8245624f3eb154bda6b13c2601"
        self.selected_model = None
        self.openai_client = None
        
        # 香港天文台API设置 - 可替换为其他天气数据源
        self.hko_base_url = "https://www.hko.gov.hk"
        
        # 本地数据文件路径 - 可替换为其他数据源
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.token_csv_path = os.path.join(script_dir, "token_price.csv")
        self.token_json_path = os.path.join(script_dir, "token_price.json")
        
        # 加载本地数据库到内存（提高查询效率）
        self.token_data = self._load_token_data()
    
    def _load_token_data(self) -> Optional[pd.DataFrame]:
        """加载token价格数据到内存 - 可替换为其他数据加载方式"""
        try:
            if os.path.exists(self.token_csv_path):
                df = pd.read_csv(self.token_csv_path)
                df['datetime'] = pd.to_datetime(df['datetime'])
                print(f"✅ 已加载 {len(df)} 条token价格数据")
                return df
            else:
                print("⚠️  未找到token价格数据文件")
                return None
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            return None
    
    def select_model(self) -> str:
        """让用户选择AI模型"""
        available_models = []
        
        if OPENAI_AVAILABLE:
            available_models.append(("1", "OpenAI GPT"))
        if DASHSCOPE_AVAILABLE:
            available_models.append(("2", "阿里云通义千问 (Qwen)"))
        
        if not available_models:
            print("⚠️  没有可用的AI模型，将使用本地智能分析")
            return "offline"
        
        print("\n🤖 请选择AI模型:")
        for choice, name in available_models:
            print(f"{choice}. {name}")
        print("3. 离线模式 (仅使用本地功能)")
        
        while True:
            choice = input("\n请输入选择: ").strip()
            
            if choice == "1" and OPENAI_AVAILABLE:
                try:
                    if OPENAI_NEW_VERSION:
                        self.openai_client = OpenAI(api_key=self.openai_api_key)
                    else:
                        openai.api_key = self.openai_api_key
                    self.selected_model = "openai"
                    print("✅ 已选择 OpenAI GPT 模型")
                    return "openai"
                except Exception as e:
                    print(f"❌ OpenAI初始化失败: {e}")
                    print("将切换到离线模式")
                    self.selected_model = "offline"
                    return "offline"
                    
            elif choice == "2" and DASHSCOPE_AVAILABLE:
                try:
                    dashscope.api_key = self.qwen_api_key
                    self.selected_model = "qwen"
                    print("✅ 已选择 通义千问 模型")
                    return "qwen"
                except Exception as e:
                    print(f"❌ 通义千问初始化失败: {e}")
                    print("将切换到离线模式")
                    self.selected_model = "offline"
                    return "offline"
                    
            elif choice == "3":
                self.selected_model = "offline"
                print("✅ 已选择离线模式")
                return "offline"
            else:
                print("❌ 无效选择，请重新输入")
    
    def get_ai_response(self, prompt: str, context: str = "") -> str:
        """调用AI模型获取响应 - 可扩展支持更多模型"""
        if self.selected_model == "offline":
            return self._get_offline_response(prompt, context)
        
        full_prompt = f"{context}\n\n用户问题: {prompt}" if context else prompt
        
        try:
            if self.selected_model == "openai" and OPENAI_AVAILABLE:
                if OPENAI_NEW_VERSION and self.openai_client:
                    # 使用新版本的OpenAI API
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "你是一个专业的AI助手，可以帮助用户处理各种问题。请用中文回答。"},
                            {"role": "user", "content": full_prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                else:
                    # 使用旧版本的OpenAI API
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "你是一个专业的AI助手，可以帮助用户处理各种问题。请用中文回答。"},
                            {"role": "user", "content": full_prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                
            elif self.selected_model == "qwen" and DASHSCOPE_AVAILABLE:
                response = Generation.call(
                    model="qwen-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个专业的AI助手，可以帮助用户处理各种问题。请用中文回答。"},
                        {"role": "user", "content": full_prompt}
                    ],
                    result_format='message'
                )
                if response.status_code == HTTPStatus.OK:
                    return response.output.choices[0].message.content
                else:
                    raise Exception(f"API调用失败: {response.message}")
                    
        except Exception as e:
            print(f"⚠️  AI API调用失败: {e}")
            print("🔄 切换到本地智能分析...")
            return self._get_offline_response(prompt, context)
    
    def _get_offline_response(self, prompt: str, context: str = "") -> str:
        """本地智能分析（当AI API不可用时）"""
        # 基于关键词的简单规则分析
        prompt_lower = prompt.lower()
        
        if any(keyword in prompt_lower for keyword in ["天气", "温度", "下雨", "穿什么", "雨伞"]):
            return """根据当前天气信息分析：
            
🌤️ 天气状况：多云，有几阵骤雨
🌡️ 温度：24-28°C，比较温暖
💧 湿度：75-90%，较高
            
👔 穿衣建议：
- 建议穿轻便的长袖衬衫或薄外套
- 选择透气性好的服装
- 穿舒适的鞋子，避免穿凉鞋

☂️ 必需品：
- 一定要带雨伞！天气预报显示有阵雨
- 可以考虑带轻便的雨衣
- 带个小包保护手机等电子设备

总结：今天天气温暖但有雨，做好防雨准备很重要。"""

        elif any(keyword in prompt_lower for keyword in ["价格", "token", "币", "投资"]):
            return """根据价格数据分析：
            
📈 市场分析：
- 数据库中包含了多种token的历史价格数据
- 价格波动较大，投资需谨慎
- 建议关注长期趋势而非短期波动

💡 投资建议：
- 分散投资，降低风险
- 定期关注市场动态
- 理性投资，不要盲目跟风

注：以上仅为数据分析，不构成投资建议。"""

        elif any(keyword in prompt_lower for keyword in ["税", "工资", "计算", "个税"]):
            return """关于税务计算：
            
💰 个人所得税说明：
- 目前使用的是中国大陆个税计算方式
- 起征点为5000元/月
- 采用七级超额累进税率
- 可扣除五险一金和专项附加扣除

📊 建议：
- 合理规划专项附加扣除可以减税
- 了解税率结构有助于薪酬谈判
- 如需精确计算，请使用本系统的税务计算功能"""

        else:
            return f"""基于本地分析的回复：

您的问题：{prompt}

🤖 分析结果：
这是一个综合性问题。基于当前可用的功能，我建议：

1. 如果涉及具体计算，可以使用本地函数功能
2. 如果需要数据查询，可以搜索本地数据库
3. 如果需要更智能的分析，建议检查网络连接后使用AI功能

💡 提示：当前处于离线模式，功能有限。如需完整的AI分析，请确保网络连接正常。"""

    # ==================== 功能模块 1: 本地函数调用 ==================== 
    # 可替换为其他本地计算功能
    
    def calculate_tax(self, gross_salary: float, social_insurance: float = 0, 
                     special_deduction: float = 0, period: str = "monthly") -> Dict[str, Any]:
        """调用本地税务计算函数"""
        try:
            result = calculate_individual_income_tax_from_salary(
                gross_salary, social_insurance, special_deduction, period
            )
            
            # 格式化输出
            formatted_result = {
                "计算结果": f"月工资 ¥{gross_salary:,.2f} 的个人所得税",
                "应缴税额": f"¥{result['tax_due']:,.2f} ({period})",
                "实际税率": f"{result['effective_rate']:.2f}%",
                "边际税率": f"{result['marginal_rate']:.1f}%",
                "扣除项目": {
                    "年度起征点": f"¥{result['deductions']['annual_threshold']:,.2f}",
                    "年度五险一金": f"¥{result['deductions']['annual_social_insurance']:,.2f}",
                    "年度专项附加扣除": f"¥{result['deductions']['annual_special_deduction']:,.2f}"
                }
            }
            return formatted_result
        except Exception as e:
            return {"错误": f"税务计算失败: {e}"}
    
    # ==================== 功能模块 2: 天气查询 ==================== 
    # 可替换为其他网站数据抓取功能
    
    def get_hk_weather(self) -> Dict[str, Any]:
        """查询香港天文台实时天气信息"""
        try:
            # 香港天文台官方API
            api_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 查询当前天气报告
            current_weather_params = {
                'dataType': 'rhrread',  # 本港地区天气报告
                'lang': 'sc'           # 简体中文
            }
            
            response = requests.get(api_url, params=current_weather_params, headers=headers, timeout=15)
            response.raise_for_status()  # 如果状态码不是200会抛出异常
            
            weather_data = response.json()
            
            # 解析温度数据
            temperature_info = []
            if 'temperature' in weather_data and 'data' in weather_data['temperature']:
                temp_data = weather_data['temperature']['data']
                if temp_data:
                    # 获取前几个主要地区的温度
                    for i, temp_record in enumerate(temp_data[:5]):
                        temperature_info.append(f"{temp_record['place']}: {temp_record['value']}°C")
            
            # 解析湿度数据
            humidity_value = "N/A"
            if 'humidity' in weather_data and 'data' in weather_data['humidity']:
                humidity_data = weather_data['humidity']['data']
                if humidity_data:
                    humidity_value = f"{humidity_data[0]['value']}%"
            
            # 解析紫外线指数
            uv_info = "N/A"
            if 'uvindex' in weather_data and 'data' in weather_data['uvindex']:
                uv_data = weather_data['uvindex']['data']
                if uv_data:
                    uv_info = f"{uv_data[0]['value']} ({uv_data[0]['desc']})"
            
            # 解析警告信息
            warnings = []
            if 'warningMessage' in weather_data and weather_data['warningMessage']:
                warnings = weather_data['warningMessage']
            
            # 获取本港地区天气预报
            forecast_params = {
                'dataType': 'flw',  # 本港地区天气预报
                'lang': 'sc'
            }
            
            forecast_response = requests.get(api_url, params=forecast_params, headers=headers, timeout=15)
            forecast_response.raise_for_status()
            
            forecast_data = forecast_response.json()
            
            # 组装天气信息
            weather_info = {
                "查询时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "数据源": "香港天文台官方API",
                "数据更新时间": weather_data.get('updateTime', 'N/A'),
                "温度分布": temperature_info if temperature_info else ["数据获取中"],
                "相对湿度": humidity_value,
                "紫外线指数": uv_info,
                "天气概况": forecast_data.get('generalSituation', 'N/A'),
                "今日预报": forecast_data.get('forecastDesc', 'N/A'),
                "明日展望": forecast_data.get('outlook', 'N/A'),
                "天气警告": warnings if warnings else ["当前无天气警告"],
                "火灾危险": forecast_data.get('fireDangerWarning', 'N/A')
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
        except requests.exceptions.Timeout:
            raise Exception("请求超时，香港天文台服务器响应缓慢")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP错误: {e}")
        except KeyError as e:
            raise Exception(f"数据解析失败，API返回格式异常: {e}")
        except Exception as e:
            raise Exception(f"天气数据获取失败: {e}")
    
    # ==================== 功能模块 3: AI驱动的本地数据库查询 ==================== 
    # 使用AI API解析自然语言，生成结构化查询，本地执行
    
    def search_token_price(self, query: str) -> Dict[str, Any]:
        """AI驱动的智能数据库查询：自然语言→结构化查询→本地执行"""
        if self.token_data is None:
            return {"错误": "token数据未加载"}
        
        try:
            print(f"🤖 正在使用AI解析自然语言查询: '{query}'")
            
            # 步骤1：AI解析自然语言，生成结构化查询
            structured_query = self._ai_parse_to_structured_query(query)
            print(f"📋 AI生成的结构化查询: {structured_query}")
            
            # 步骤2：本地执行结构化查询
            results = self._execute_structured_query(structured_query)
            
            # 步骤3：AI生成智能总结
            summary = self._ai_generate_result_summary(query, structured_query, results)
            
            return {
                "原始查询": query,
                "AI解析过程": structured_query,
                "查询结果": results[:10],  # 限制显示条数
                "AI智能总结": summary,
                "技术说明": "AI解析→本地查询→AI总结"
            }
            
        except Exception as e:
            return {"错误": f"AI驱动查询失败: {e}"}
    
    def _ai_parse_to_structured_query(self, natural_query: str) -> Dict[str, Any]:
        """使用AI将自然语言转换为结构化查询语言"""
        
        # 构建AI提示词，定义结构化查询语言
        ai_prompt = f"""
你是一个专业的数据库查询解析器。请将用户的自然语言查询转换为结构化的JSON格式。

可用的数据字段：
- coin_id: 币种标识符 (aixbt, vaderai-by-virtuals, luna-by-virtuals)
- datetime: 时间戳
- price_usd: 美元价格
- market_cap_usd: 市值
- volume_24h_usd: 24小时交易量

币种别名映射：
- "ai"、"ai币"、"智能" → aixbt
- "vaderai"、"vader"、"虚拟" → vaderai-by-virtuals  
- "luna"、"露娜"、"月亮" → luna-by-virtuals

时间数据范围：2025-01-01 到 2025-01-03

请将以下查询转换为JSON格式：
用户查询: "{natural_query}"

返回格式（只返回JSON，不要其他文字）：
{{
    "coins": ["coin_id1", "coin_id2"],  // 空数组表示所有币种
    "time_filter": {{
        "type": "exact_date|date_range|relative|latest",
        "value": "具体值"
    }},
    "conditions": {{
        "price_range": {{"min": null, "max": null}},
        "order_by": "datetime|price_usd|market_cap_usd|volume_24h_usd",
        "order_direction": "asc|desc",
        "limit": 10
    }},
    "query_type": "price|trend|comparison|extreme_values|general",
    "confidence": 0.0-1.0
}}
"""
        
        try:
            if self.selected_model == "offline":
                # 离线模式的简单解析
                return self._simple_offline_parse(natural_query)
            
            # 调用AI API
            ai_response = self.get_ai_response(ai_prompt)
            
            # 尝试解析AI返回的JSON
            import json
            try:
                # 提取JSON部分（AI可能返回额外的文字）
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = ai_response[json_start:json_end]
                    structured_query = json.loads(json_str)
                else:
                    raise ValueError("未找到有效JSON")
                
                # 验证和修正结构
                structured_query = self._validate_structured_query(structured_query)
                
                return structured_query
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ AI返回格式解析失败: {e}")
                print(f"AI原始回复: {ai_response}")
                # 降级到简单解析
                return self._simple_offline_parse(natural_query)
                
        except Exception as e:
            print(f"⚠️ AI解析失败: {e}")
            return self._simple_offline_parse(natural_query)
    
    def _simple_offline_parse(self, query: str) -> Dict[str, Any]:
        """简单的离线解析作为备用方案"""
        query_lower = query.lower()
        
        # 简单的币种识别
        coins = []
        if any(word in query_lower for word in ["ai", "aixbt"]):
            coins.append("aixbt")
        if any(word in query_lower for word in ["vaderai", "vader", "虚拟"]):
            coins.append("vaderai-by-virtuals")
        if any(word in query_lower for word in ["luna", "露娜", "月亮"]):
            coins.append("luna-by-virtuals")
        
        # 简单的时间识别
        time_filter = {"type": "latest", "value": ""}
        if "2025-01-03" in query:
            time_filter = {"type": "exact_date", "value": "2025-01-03"}
        elif "昨天" in query or "昨日" in query:
            time_filter = {"type": "relative", "value": "yesterday"}
        elif "今天" in query or "今日" in query:
            time_filter = {"type": "relative", "value": "today"}
        
        return {
            "coins": coins,
            "time_filter": time_filter,
            "conditions": {
                "price_range": {"min": None, "max": None},
                "order_by": "datetime",
                "order_direction": "desc",
                "limit": 10
            },
            "query_type": "general",
            "confidence": 0.6,
            "source": "offline_fallback"
        }
    
    def _validate_structured_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """验证和修正AI生成的结构化查询"""
        # 设置默认值
        defaults = {
            "coins": [],
            "time_filter": {"type": "latest", "value": ""},
            "conditions": {
                "price_range": {"min": None, "max": None},
                "order_by": "datetime",
                "order_direction": "desc", 
                "limit": 10
            },
            "query_type": "general",
            "confidence": 0.8
        }
        
        # 合并默认值
        for key, default_value in defaults.items():
            if key not in query:
                query[key] = default_value
            elif key == "conditions" and isinstance(query[key], dict):
                for sub_key, sub_default in default_value.items():
                    if sub_key not in query[key]:
                        query[key][sub_key] = sub_default
        
        # 验证币种名称
        valid_coins = ["aixbt", "vaderai-by-virtuals", "luna-by-virtuals"]
        query["coins"] = [coin for coin in query["coins"] if coin in valid_coins]
        
        return query
    
    def _execute_structured_query(self, structured_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据结构化查询在本地执行数据库查询"""
        df = self.token_data.copy()
        
        # 1. 币种过滤
        if structured_query["coins"]:
            df = df[df['coin_id'].isin(structured_query["coins"])]
        
        # 2. 时间过滤
        time_filter = structured_query.get("time_filter", {})
        if time_filter.get("type") == "exact_date":
            target_date = pd.to_datetime(time_filter["value"]).date()
            df = df[df['datetime'].dt.date == target_date]
        elif time_filter.get("type") == "relative":
            if time_filter["value"] == "today":
                today = datetime.now().date()
                df = df[df['datetime'].dt.date == today]
            elif time_filter["value"] == "yesterday":
                yesterday = (datetime.now() - timedelta(days=1)).date()
                df = df[df['datetime'].dt.date == yesterday]
        
        # 3. 价格范围过滤
        conditions = structured_query.get("conditions", {})
        price_range = conditions.get("price_range", {})
        if price_range.get("min") is not None:
            df = df[df['price_usd'] >= price_range["min"]]
        if price_range.get("max") is not None:
            df = df[df['price_usd'] <= price_range["max"]]
        
        # 4. 排序
        order_by = conditions.get("order_by", "datetime")
        order_direction = conditions.get("order_direction", "desc")
        ascending = (order_direction == "asc")
        df = df.sort_values(order_by, ascending=ascending)
        
        # 5. 限制结果数量
        limit = min(conditions.get("limit", 10), 50)  # 最多50条
        df = df.head(limit)
        
        # 6. 格式化结果
        results = []
        for _, row in df.iterrows():
            results.append({
                "时间": row['datetime'].strftime("%Y-%m-%d %H:%M:%S"),
                "币种": row['coin_id'],
                "价格": f"${row['price_usd']:.6f}",
                "市值": f"${row['market_cap_usd']:,.2f}",
                "24h交易量": f"${row['volume_24h_usd']:,.2f}"
            })
        
        return results
    
    def _ai_generate_result_summary(self, original_query: str, structured_query: Dict, results: List[Dict]) -> str:
        """使用AI生成查询结果的智能总结"""
        if self.selected_model == "offline":
            return f"查询完成，找到{len(results)}条相关数据记录。"
        
        try:
            summary_prompt = f"""
基于以下信息，生成一个简洁专业的数据查询总结：

用户原始查询: {original_query}
结构化查询: {structured_query}
查询结果数量: {len(results)}

前3条结果示例:
{results[:3] if results else "无结果"}

请生成一个简洁的总结，包括：
1. 查询解释（你理解了什么）
2. 数据概况（找到什么）
3. 关键发现（如果有的话）

回复应该简洁专业，2-3句话即可。
"""
            
            summary = self.get_ai_response(summary_prompt)
            return summary.strip()
            
        except Exception as e:
            return f"查询成功完成，找到{len(results)}条数据记录。AI总结生成失败: {e}"
    
    # ==================== 主要交互流程 ====================
    
    def show_menu(self) -> str:
        """显示功能菜单"""
        print("\n🔧 请选择需要的功能:")
        print("1. 📊 调用本地函数 (税务计算)")
        print("2. 🌤️  查询香港天气")
        print("3. 💰 查询本地数据库 (token价格)")
        print("4. 🤖 智能综合处理 (结合多功能)")
        print("5. ❌ 退出程序")
        
        while True:
            choice = input("\n请输入选择 (1-5): ").strip()
            if choice in ["1", "2", "3", "4", "5"]:
                return choice
            else:
                print("❌ 无效选择，请重新输入")
    
    def handle_tax_calculation(self):
        """处理税务计算请求"""
        print("\n📊 税务计算功能")
        try:
            gross_salary = float(input("请输入月工资总额（元）: "))
            social_insurance = float(input("请输入月五险一金（元，默认0）: ") or 0)
            special_deduction = float(input("请输入月专项附加扣除（元，默认0）: ") or 0)
            
            result = self.calculate_tax(gross_salary, social_insurance, special_deduction)
            
            print("\n💰 计算结果:")
            for key, value in result.items():
                if isinstance(value, dict):
                    print(f"{key}:")
                    for sub_key, sub_value in value.items():
                        print(f"  - {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
                    
        except ValueError:
            print("❌ 输入格式错误，请输入数字")
        except Exception as e:
            print(f"❌ 处理失败: {e}")
    
    def handle_weather_query(self):
        """处理天气查询请求"""
        print("\n🌤️ 正在查询香港天气...")
        try:
            weather_info = self.get_hk_weather()
            
            print("\n🌈 香港天气信息:")
            for key, value in weather_info.items():
                if isinstance(value, list):
                    print(f"  {key}:")
                    for item in value:
                        print(f"    - {item}")
                else:
                    print(f"  {key}: {value}")
                
        except Exception as e:
            print(f"\n❌ 天气查询失败: {e}")
            print("⚠️ 可能的原因:")
            print("  - 网络连接问题")
            print("  - 香港天文台服务器繁忙")
            print("  - API限制或维护中")
    
    def handle_database_query(self):
        """处理数据库查询请求"""
        print("\n💰 本地数据库查询功能")
        print("例如: '查询最接近2025-01-10 0点时的aixbt的价格'")
        
        query = input("请输入查询内容: ").strip()
        if not query:
            print("❌ 查询内容不能为空")
            return
            
        result = self.search_token_price(query)
        
        print("\n📈 查询结果:")
        for key, value in result.items():
            if key == "查询结果" and isinstance(value, list):
                print(f"{key}:")
                for i, item in enumerate(value, 1):
                    print(f"  {i}. {item}")
            else:
                print(f"  {key}: {value}")
    
    def handle_smart_processing(self):
        """处理智能综合功能请求"""
        print("\n🤖 智能综合处理功能")
        if self.selected_model == "offline":
            print("💡 当前为离线模式，将使用本地智能分析")
        print("示例: '帮我查一查香港的天气，然后决定我出门穿什么，要不要带伞'")
        
        user_query = input("请描述您的需求: ").strip()
        if not user_query:
            print("❌ 需求描述不能为空")
            return
        
        # 分析查询内容，决定调用哪些功能
        context_data = []
        
        # 检查是否需要天气信息
        if any(keyword in user_query.lower() for keyword in ["天气", "温度", "下雨", "穿什么", "雨伞"]):
            print("🔍 检测到天气相关查询，获取天气信息...")
            try:
                weather_info = self.get_hk_weather()
                context_data.append(f"当前香港天气信息: {weather_info}")
            except Exception as e:
                print(f"⚠️ 天气数据获取失败: {e}")
                context_data.append(f"天气数据获取失败: {e}")
        
        # 检查是否需要价格数据
        if any(keyword in user_query.lower() for keyword in ["价格", "token", "币", "aixbt", "luna", "vaderai"]):
            print("🔍 检测到价格查询，搜索相关数据...")
            try:
                price_result = self.search_token_price(user_query)
                context_data.append(f"价格查询结果: {price_result}")
            except Exception as e:
                print(f"⚠️ 价格数据查询失败: {e}")
                context_data.append(f"价格数据查询失败: {e}")
        
        # 检查是否需要税务计算
        if any(keyword in user_query.lower() for keyword in ["税", "工资", "计算", "个税"]):
            print("🔍 检测到税务相关查询...")
            context_data.append("税务计算功能可用，如需计算请提供具体工资数额")
        
        # 组合上下文信息
        context = "\n".join(context_data) if context_data else ""
        
        # 调用AI生成智能回答
        if self.selected_model == "offline":
            print("🤖 本地智能分析中...")
        else:
            print("🤖 AI正在分析和处理...")
        
        try:
            ai_response = self.get_ai_response(user_query, context)
            print("\n💡 智能建议:")
            print(ai_response)
        except Exception as e:
            print(f"\n❌ AI处理失败: {e}")
            print("🔄 切换到基础回复模式...")
            print("\n💡 基础建议:")
            print("抱歉，AI分析暂时不可用。请直接使用其他具体功能模块获取信息。")
    
    def run(self):
        """运行主程序"""
        print("=" * 60)
        print("🚀 欢迎使用 Model Context Protocol (MCP) Demo")
        print("=" * 60)
        print(f"🔧 OpenAI 可用: {'✅' if OPENAI_AVAILABLE else '❌'}")
        print(f"🔧 Dashscope 可用: {'✅' if DASHSCOPE_AVAILABLE else '❌'}")
        
        # 选择AI模型
        self.select_model()
        
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.handle_tax_calculation()
            elif choice == "2":
                self.handle_weather_query()
            elif choice == "3":
                self.handle_database_query()
            elif choice == "4":
                self.handle_smart_processing()
            elif choice == "5":
                print("\n👋 感谢使用，再见！")
                break
            
            # 询问是否继续
            continue_choice = input("\n是否继续使用？(y/n): ").strip().lower()
            if continue_choice in ['n', 'no', '否']:
                print("\n👋 感谢使用，再见！")
                break

# ==================== 程序入口 ====================

if __name__ == "__main__":
    try:
        demo = MCPDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序已被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        print("请检查配置和依赖包是否正确安装")
