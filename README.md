# Agentic_AI_Explorer

## 🚀 项目概述

Agentic_AI_Explorer 是一个全面的智能代理系统探索平台，旨在研究、开发和评估各种AI代理技术。本项目提供了完整的代理系统开发生态，包括数据管理、性能评估、上下文管理和实际演示等核心模块。

## 📁 项目架构

```
Agentic_AI_Explorer/
├── 📊 Agentic_Data/           # 数据管理模块
├── 📈 Agentic_Evaluation/     # 评估测试模块  
├── 🧠 Context_Management/     # 上下文管理模块
├── 🎯 Langchain_demo/         # LangChain演示
├── ⚙️ Function_Calling_demo/  # FunctionCalling演示
├── ✍️ Dify                    # 极低代码的可视化agent开源搭建平台的操作指南
├── 🧩 Coze                    # 初学者友好的可视化agent闭源agent搭建平台操作指南
├── 🤖 MCP_demo                # MCP演示，各API通用
└── 📖 README.md               # 项目文档
```

## 🔧 核心模块

### 📊 Agentic_Data
**智能代理数据管理系统**
- 多源数据收集与聚合
- 实时数据流处理
- 数据预处理与质量控制
- 统一数据访问接口
- 支持结构化和非结构化数据

[详细文档](./Agentic_Data/README.md)

### 📈 Agentic_Evaluation  
**智能代理评估与测试框架**
- 多维度性能评估体系
- 自动化测试流程
- 基准测试和比较分析
- 伦理安全评估
- 可视化评估报告

[详细文档](./Agentic_Evaluation/README.md)

### 🧠 Context_Management
**上下文管理与记忆系统**
- 多轮对话上下文维护
- 智能记忆管理
- 会话状态持久化
- 多模态上下文处理
- 上下文压缩与优化

[详细文档](./Context_Management/README.md)

### 🎯 Langchain_demo
**LangChain集成演示**
- 基于Qwen模型的智能代理
- 工具调用和推理演示
- 交互式命令行界面
- OpenAI兼容API集成

## 🛠️ 技术栈

- **语言**: Python 3.10+
- **AI框架**: LangChain, OpenAI API
- **模型**: Qwen系列大语言模型
- **数据处理**: 支持多种数据格式和存储后端
- **评估**: 自定义评估指标和基准测试

## 🚀 快速开始

### 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd Agentic_AI_Explorer

# 安装依赖
pip install langchain langchain-community openai
```

### 运行演示
```bash
# 运行LangChain演示
cd "Langchain_demo "
python LangChain_Demo.py
```

### API配置
- 演示中使用的是Qwen个人API密钥
- 可以替换为任何兼容的LLM API
- 使用前请检查对应SDK的兼容性

## 🎯 使用场景

- **🔬 研究开发**: 智能代理算法研究和原型开发
- **📊 性能分析**: 代理系统性能评估和优化
- **🏭 生产部署**: 企业级代理系统部署和监控
- **📚 教育学习**: AI代理技术学习和实验

## 🔄 开发流程

1. **数据准备** → 使用 `Agentic_Data` 模块管理训练和测试数据
2. **代理开发** → 基于 `Langchain_demo` 开发自定义代理
3. **上下文管理** → 集成 `Context_Management` 实现记忆功能
4. **性能评估** → 通过 `Agentic_Evaluation` 评估代理性能

## 🤝 贡献指南

我们欢迎各种形式的贡献！

- 🐛 报告问题和Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码改进

### 开发分支
- `main`: 主分支，稳定版本
- `weicwang`: 开发分支，最新功能

## 📄 许可证

本项目采用开源许可证，具体信息请查看 LICENSE 文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 演示中的API密钥为个人密钥，请在使用前替换为您自己的API密钥。使用任何LLM API前，请确认其SDK兼容性。
