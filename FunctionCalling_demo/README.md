这是Function Calling的Demo文件夹。在本demo中，将使用个人所得税计算器作为示例函数。Function Calling可以被视为一个使用LLM作为ChatBot的自然语言调用函数。请注意：

- 替换LLM时请查阅对应API文档，确定SDK版本依赖情况（例如，Qwen不支持OpenAI 1.0以下版本）
- 你可以添加其他函数到函数库中，Function Calling性能高度依赖被调用函数。 **需要在主程序中明确被调用函数库的路径（推荐函数库放在主程序的根目录下）**
