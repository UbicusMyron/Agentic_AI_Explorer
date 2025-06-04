# 📋 API配置完整指南

本文档详细说明如何配置各个电商平台的API密钥，以获取真实的商品数据。

## 🎯 概览

购物助手支持以下电商平台：
- 🟠 **淘宝** (taobao.com) - 中国最大的C2C电商平台
- 🔴 **京东** (jd.com) - 中国知名的B2C电商平台  
- 🟡 **亚马逊** (amazon.com) - 全球最大的电商平台

## 🔧 配置步骤

### 1. 淘宝开放平台配置

#### 1.1 注册淘宝开放平台账号
1. 访问 [淘宝开放平台](https://open.taobao.com/)
2. 使用淘宝账号登录
3. 完成开发者认证

#### 1.2 创建应用
1. 进入"应用管理" → "创建应用"
2. 选择"淘宝客应用"
3. 填写应用信息并提交审核

#### 1.3 获取API密钥
审核通过后，在应用详情页获取：
- **App Key**: 应用标识
- **App Secret**: 应用密钥
- **Session**: 授权令牌

#### 1.4 配置到代码
在 `SupportFunction.py` 中找到 `taobao_api_config`，替换为真实值：

```python
self.taobao_api_config = {
    'app_key': 'your_real_app_key',        # 替换为真实 App Key
    'app_secret': 'your_real_app_secret',  # 替换为真实 App Secret
    'session': 'your_real_session_key',    # 替换为真实 Session Key
    'base_url': 'https://eco.taobao.com/router/rest'
}
```

### 2. 京东联盟配置

#### 2.1 注册京东联盟账号
1. 访问 [京东联盟](https://union.jd.com/)
2. 注册成为京东联盟推广者
3. 完成身份认证

#### 2.2 申请API权限
1. 进入"工具中心" → "API申请"
2. 申请"商品查询API"权限
3. 等待审核通过

#### 2.3 获取API密钥
在联盟后台获取：
- **App Key**: 应用Key
- **App Secret**: 应用密钥
- **Union ID**: 联盟ID

#### 2.4 配置到代码
在 `SupportFunction.py` 中找到 `jd_api_config`，替换为真实值：

```python
self.jd_api_config = {
    'app_key': 'your_real_jd_app_key',        # 替换为真实 App Key
    'app_secret': 'your_real_jd_app_secret',  # 替换为真实 App Secret
    'base_url': 'https://api.jd.com/routerjson'
}
```

### 3. 亚马逊产品广告API配置

#### 3.1 注册亚马逊开发者账号
1. 访问 [亚马逊产品广告API](https://webservices.amazon.com/paapi5/)
2. 注册为Amazon Associate
3. 申请产品广告API访问权限

#### 3.2 获取API凭证
在Amazon Associates后台获取：
- **Access Key**: AWS访问密钥
- **Secret Key**: AWS私有密钥
- **Partner Tag**: 合作伙伴标签

#### 3.3 配置到代码
在 `SupportFunction.py` 中找到 `amazon_api_config`，替换为真实值：

```python
self.amazon_api_config = {
    'access_key': 'your_real_access_key',    # 替换为真实 Access Key
    'secret_key': 'your_real_secret_key',    # 替换为真实 Secret Key  
    'partner_tag': 'your_real_partner_tag',  # 替换为真实 Partner Tag
    'marketplace': 'www.amazon.com',
    'region': 'us-east-1',
    'base_url': 'https://webservices.amazon.com/paapi5/searchitems'
}
```

## ⚠️ 重要注意事项

### API使用限制
- **淘宝**: 每日API调用次数有限制，需要根据应用等级确定
- **京东**: 根据联盟等级有不同的调用频率限制
- **亚马逊**: 有严格的请求频率和每日请求数量限制

### 数据合规性
- 确保遵守各平台的API使用协议
- 不要滥用API或进行恶意爬取
- 遵守相关法律法规和平台规则

### 错误处理
- API调用可能因为网络、权限、配额等问题失败
- 系统已实现了优雅的错误处理和降级机制
- 如果某个平台API失败，会自动尝试其他平台

## 🔍 配置验证

配置完成后，运行以下命令验证：

```bash
python final_test.py
```

该脚本会检查：
- ✅ API密钥是否已正确配置
- ✅ 网络连接是否正常
- ✅ API调用是否成功
- ✅ 数据解析是否正确

## 🆘 常见问题

### Q: API调用返回认证错误
**A**: 检查API密钥是否正确，确保没有多余的空格或特殊字符。

### Q: 搜索返回空结果
**A**: 可能的原因：
- API配额已用完
- 搜索关键词过于特殊
- 网络连接问题
- API服务临时不可用

### Q: 如何获得更高的API调用限额
**A**: 
- **淘宝**: 提升应用等级，增加调用量
- **京东**: 提高联盟等级，增加权限
- **亚马逊**: 联系Amazon Developer Support申请

### Q: 是否支持其他电商平台
**A**: 当前支持淘宝、京东、亚马逊。未来计划支持：
- 拼多多 (PDD)
- 苏宁易购 (Suning)
- 唯品会 (VIP)

## 📞 技术支持

如果在配置过程中遇到问题：

1. 查看 `final_test.py` 的测试结果
2. 检查网络连接和防火墙设置
3. 确认API密钥的有效性和权限
4. 查看系统日志中的详细错误信息

---

**⚡ 配置完成后，您就能享受真实、准确的商品搜索体验了！** 