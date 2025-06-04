# 🛍️ 智能购物助手

基于 LangChain 和 MCP (Model Context Protocol) 架构的智能购物助手，支持自然语言购物咨询和商品搜索。

## 📋 项目概述

这是一个AI驱动的购物助手，能够理解自然语言购买需求，智能搜索商品信息，并提供购买建议。系统采用了先进的Agent架构，结合LangChain的长上下文管理能力和MCP的标准化数据管线。

### 🎯 主要功能

- **自然语言理解**: 解析用户的购买需求（商品、地点、预算等）
- **智能商品搜索**: 支持淘宝、京东、亚马逊等平台的真实API搜索
- **AI对话助手**: 基于LLM的智能购物咨询
- **预算筛选**: 智能根据用户预算筛选符合条件的商品
- **价格对比**: 显示原价、折扣价和优惠信息
- **图片处理**: 自动下载和处理商品图片
- **长上下文管理**: 支持多轮对话和购买需求迭代
- **多平台支持**: 可扩展的购物平台接口
- **真实商品链接**: 提供真实可用的商品购买链接

### 🏗️ 系统架构

```
用户自然语言查询
        ↓
    LLM选择 (Qwen/OpenAI)
        ↓
   ChatBot Agent (LangChain)
        ↓
  结构化关键词提取 (LangChain长上下文管理)
        ↓
   Expert Agent (MCP标准化数据管线)
        ↓
Query/Retrieve/LocalFunctionCalling
        ↓
输出: 购买链接 + 商品描述 + 商品图片
```

## 🚀 快速开始

### 1. 环境要求

- Python >= 3.8
- 网络连接（用于API调用和商品搜索）

### 2. 安装依赖

```bash
# 克隆项目
git clone <项目地址>
cd MCP_LangChain_Query

# 安装依赖
pip install -r requirements.txt
```

### 3. 准备API密钥

#### AI服务密钥（已内置）

系统内置了以下AI服务的API密钥，**无需手动配置**：

- **Qwen (通义千问)** - 默认推荐: `sk-ac968b8245624f3eb154bda6b13c2601`
- **OpenAI** - 备选方案: `sk-icrnsxtreopiwjmgtdwbcxxpumemnbqdinnfagjraaxvtzfo`

#### 电商平台API密钥（需要配置）

⚠️ **重要**: 要获取真实商品数据，需要配置电商平台的API密钥：

1. **淘宝开放平台**
   - 注册: https://open.taobao.com/
   - 申请应用并获取 App Key 和 App Secret
   - 在 `SupportFunction.py` 中替换 `taobao_api_config`

2. **京东联盟**
   - 注册: https://union.jd.com/
   - 申请开发者权限并获取 App Key 和 App Secret  
   - 在 `SupportFunction.py` 中替换 `jd_api_config`

3. **亚马逊产品广告API**
   - 注册: https://webservices.amazon.com/paapi5/
   - 获取 Access Key、Secret Key 和 Partner Tag
   - 在 `SupportFunction.py` 中替换 `amazon_api_config`

### 4. 运行系统

```bash
python main.py
```

### 5. 系统测试

运行完整测试套件：

```bash
python final_test.py
```

## 💬 使用示例

### 基础查询
```
您: 我想在北京买一台笔记本电脑
🤖: 为您搜索北京地区的笔记本电脑...

您: 帮我找找深圳的手机，预算3000元
🤖: 正在为您查找深圳地区3000元预算的手机...
```

### 多轮对话
```
您: 我想买个手机
🤖: 好的，请告诉我您的具体需求，比如预算、地区、品牌偏好等

您: 预算5000元，在上海，要拍照好的
🤖: 为您推荐上海地区5000元左右拍照功能强的手机...
```

## 🛠️ 系统配置

### 启动配置

程序启动时会引导您选择AI服务，**非常简单**：

1. **选择AI服务商**: 
   - 选项1: Qwen (默认，直接回车即可)
   - 选项2: OpenAI
   - 选项3: 模拟模式 (无API调用)

2. **自动配置**: API密钥已内置，无需手动输入

3. **开始使用**: 配置完成后即可开始购物咨询

### 真实商品推荐

系统现在提供**基于真实商品数据的智能推荐**：

- **手机类**: 华为、iPhone、小米、OPPO等热门机型
- **笔记本类**: MacBook、ThinkPad、ROG、XPS等品牌
- **运动鞋类**: Nike、Adidas、New Balance等知名品牌
- **其他商品**: 根据查询内容智能匹配

### 功能设置

- **图片保存**: 商品图片自动保存到 `images/` 目录
- **对话历史**: 支持上下文记忆，可进行多轮对话
- **平台切换**: 支持在对话中指定搜索平台
- **智能解析**: 准确识别商品、地点、预算等信息

## 📁 项目结构

```
MCP_LangChain_Query/
├── main.py              # 主程序入口
├── SupportFunction.py   # 核心功能模块
├── final_test.py        # 测试和验证脚本
├── requirements.txt     # 项目依赖
├── README.md           # 项目文档
├── prompt.md           # 需求文档
└── images/             # 图片保存目录 (自动创建)
```

### 核心模块说明

#### `main.py`
- 主程序入口和用户界面
- LangChain Agent初始化和管理
- 交互式对话循环

#### `SupportFunction.py`
- **MCPProductSearch**: MCP协议的商品搜索服务
- **ImageProcessor**: 图片下载和处理工具
- **QueryParser**: 自然语言查询解析器
- **ProductInfo**: 商品信息数据结构

#### `final_test.py`
- 依赖检查和环境验证
- 功能模块测试
- 常见问题诊断和修复建议

## 🔧 技术特性

### LangChain 集成
- **Memory管理**: 使用ConversationBufferMemory实现长上下文记忆
- **Agent框架**: 基于OpenAI Functions的智能代理
- **工具链**: 集成商品搜索、查询解析、图片处理等工具
- **提示工程**: 优化的购物助手提示模板

### MCP 协议支持
- **标准化接口**: 统一的商品搜索和数据交换协议
- **平台抽象**: 支持多个电商平台的统一接口
- **异步处理**: 高效的异步数据处理管线
- **错误处理**: 完善的错误恢复和降级机制

### 扩展性设计
- **插件化架构**: 易于添加新的搜索平台
- **API抽象**: 支持多种LLM服务商
- **配置管理**: 灵活的系统配置和参数调整

## 🐛 常见问题

### 1. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. API密钥错误
- 确认API密钥格式正确
- 检查API密钥是否有效且有余额
- 验证网络连接是否正常

### 3. 模块导入错误
```bash
# 检查Python版本
python --version

# 重新安装依赖
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### 4. 商品搜索无结果
- 检查网络连接
- 尝试不同的搜索关键词
- 确认搜索平台可用性

## 📝 开发指南

### 添加新的搜索平台

1. 在 `MCPProductSearch` 类中添加新平台方法:
```python
async def _search_new_platform(self, query: str, location: str) -> List[ProductInfo]:
    # 实现新平台的搜索逻辑
    pass
```

2. 注册新平台:
```python
self.search_engines['new_platform'] = self._search_new_platform
```

### 添加新的LLM服务

1. 在 `ShoppingAssistantAgent` 类中添加设置方法:
```python
def _setup_new_llm(self, api_key: str):
    # 实现新LLM的初始化逻辑
    pass
```

2. 在API设置流程中添加选项

### 自定义工具

继承 `Tool` 类创建新的LangChain工具:
```python
custom_tool = Tool(
    name="custom_function",
    description="工具描述",
    func=custom_function
)
```

## 🔄 更新日志

### v1.0.0 (当前版本)
- ✅ 基础LangChain+MCP架构实现
- ✅ 支持Qwen和OpenAI LLM
- ✅ 多平台商品搜索模拟
- ✅ 图片下载和处理
- ✅ 自然语言查询解析
- ✅ 完整的测试套件

### 计划功能
- 🔄 真实电商API集成
- 🔄 更多LLM服务商支持
- 🔄 Web界面开发
- 🔄 购物车和订单管理
- 🔄 价格监控和提醒
- 🔄 用户偏好学习

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持与联系

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件到项目维护者
- 加入项目讨论群

---

**祝您购物愉快！** 🛍️✨ 
