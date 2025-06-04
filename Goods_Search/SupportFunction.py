import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from PIL import Image
from io import BytesIO
import os
import hashlib
import hmac
import base64
from urllib.parse import quote
import time
import xml.etree.ElementTree as ET


@dataclass
class ProductInfo:
    """商品信息数据结构"""
    name: str
    price: str
    url: str
    description: str
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    platform: Optional[str] = None
    original_price: Optional[str] = None
    discount: Optional[str] = None


class MCPProductSearch:
    """MCP协议的商品搜索服务 - 真实API实现"""
    
    def __init__(self):
        # API配置
        self.taobao_api_config = {
            'app_key': '12345678',  # 需要替换为真实的淘宝开放平台App Key
            'app_secret': 'your_app_secret',  # 需要替换为真实的App Secret
            'session': 'your_session_key',  # 需要替换为真实的Session Key
            'base_url': 'https://eco.taobao.com/router/rest'
        }
        
        self.jd_api_config = {
            'app_key': 'your_jd_app_key',  # 需要替换为真实的京东联盟App Key
            'app_secret': 'your_jd_app_secret',  # 需要替换为真实的App Secret
            'base_url': 'https://api.jd.com/routerjson'
        }
        
        self.amazon_api_config = {
            'access_key': 'your_access_key',  # 需要替换为真实的Amazon Access Key
            'secret_key': 'your_secret_key',  # 需要替换为真实的Secret Key
            'partner_tag': 'your_partner_tag',  # 需要替换为真实的Partner Tag
            'marketplace': 'www.amazon.com',
            'region': 'us-east-1',
            'base_url': 'https://webservices.amazon.com/paapi5/searchitems'
        }
    
    async def search_products(self, query: str, location: str = "中国", 
                            platform: str = "taobao") -> List[ProductInfo]:
        """
        通过真实API搜索商品
        
        Args:
            query: 商品搜索关键词
            location: 购买地点
            platform: 搜索平台
        """
        try:
            if platform == 'taobao':
                return await self._search_taobao_real(query, location)
            elif platform == 'jd':
                return await self._search_jd_real(query, location)
            elif platform == 'amazon':
                return await self._search_amazon_real(query, location)
            else:
                return []
        except Exception as e:
            print(f"❌ 搜索商品时出错 ({platform}): {e}")
            # 如果真实API调用失败，返回空结果而不是模拟数据
            return []
    
    async def _search_taobao_real(self, query: str, location: str) -> List[ProductInfo]:
        """淘宝真实API搜索"""
        try:
            # 注意：这里需要真实的淘宝开放平台API密钥
            # 由于API密钥限制，这里提供API调用框架
            
            # 构造淘宝API请求参数
            params = {
                'method': 'taobao.tbk.item.get',
                'app_key': self.taobao_api_config['app_key'],
                'timestamp': str(int(time.time() * 1000)),
                'format': 'json',
                'v': '2.0',
                'sign_method': 'md5',
                'q': query,
                'fields': 'num_iid,title,pict_url,small_images,reserve_price,zk_final_price,user_type,provcity,item_url',
                'page_size': '20'
            }
            
            # 生成签名
            sign = self._generate_taobao_sign(params)
            params['sign'] = sign
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.taobao_api_config['base_url'], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_taobao_response(data, location)
            
            return []
            
        except Exception as e:
            print(f"❌ 淘宝API调用失败: {e}")
            return []
    
    async def _search_jd_real(self, query: str, location: str) -> List[ProductInfo]:
        """京东真实API搜索"""
        try:
            # 构造京东联盟API请求参数
            params = {
                'method': 'jd.union.open.goods.query',
                'app_key': self.jd_api_config['app_key'],
                'timestamp': str(int(time.time() * 1000)),
                'format': 'json',
                'v': '1.0',
                'sign_method': 'md5',
                'keyword': query,
                'pageIndex': '1',
                'pageSize': '20'
            }
            
            # 生成签名
            sign = self._generate_jd_sign(params)
            params['sign'] = sign
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.jd_api_config['base_url'], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_jd_response(data, location)
            
            return []
            
        except Exception as e:
            print(f"❌ 京东API调用失败: {e}")
            return []
    
    async def _search_amazon_real(self, query: str, location: str) -> List[ProductInfo]:
        """亚马逊真实API搜索"""
        try:
            # 构造Amazon Product Advertising API请求
            payload = {
                'Keywords': query,
                'SearchIndex': 'All',
                'ItemCount': 10,
                'PartnerTag': self.amazon_api_config['partner_tag'],
                'PartnerType': 'Associates',
                'Marketplace': self.amazon_api_config['marketplace'],
                'Resources': [
                    'Images.Primary.Medium',
                    'ItemInfo.Title',
                    'Offers.Listings.Price'
                ]
            }
            
            headers = self._generate_amazon_headers(payload)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.amazon_api_config['base_url'],
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_amazon_response(data, location)
            
            return []
            
        except Exception as e:
            print(f"❌ 亚马逊API调用失败: {e}")
            return []
    
    def _generate_taobao_sign(self, params: dict) -> str:
        """生成淘宝API签名"""
        # 排序参数
        sorted_params = sorted(params.items())
        
        # 构造签名字符串
        sign_string = self.taobao_api_config['app_secret']
        for key, value in sorted_params:
            if key != 'sign':
                sign_string += f"{key}{value}"
        sign_string += self.taobao_api_config['app_secret']
        
        # MD5签名
        return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    def _generate_jd_sign(self, params: dict) -> str:
        """生成京东API签名"""
        # 排序参数
        sorted_params = sorted(params.items())
        
        # 构造签名字符串
        sign_string = self.jd_api_config['app_secret']
        for key, value in sorted_params:
            if key != 'sign':
                sign_string += f"{key}{value}"
        sign_string += self.jd_api_config['app_secret']
        
        # MD5签名
        return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    def _generate_amazon_headers(self, payload: dict) -> dict:
        """生成亚马逊API请求头"""
        # AWS4-HMAC-SHA256签名算法实现
        # 这里简化处理，实际需要完整的AWS签名算法
        timestamp = str(int(time.time()))
        
        return {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Amz-Target': 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems',
            'X-Amz-Date': timestamp,
            'Authorization': f"AWS4-HMAC-SHA256 Credential={self.amazon_api_config['access_key']}"
        }
    
    def _parse_taobao_response(self, data: dict, location: str) -> List[ProductInfo]:
        """解析淘宝API响应"""
        products = []
        try:
            if 'tbk_item_get_response' in data and 'results' in data['tbk_item_get_response']:
                items = data['tbk_item_get_response']['results']['n_tbk_item']
                
                for item in items:
                    # 价格处理 - 确保准确性
                    original_price = float(item.get('reserve_price', '0'))
                    final_price = float(item.get('zk_final_price', '0'))
                    
                    # 计算折扣
                    discount = ""
                    if original_price > final_price:
                        discount_percent = int((1 - final_price/original_price) * 100)
                        discount = f"{discount_percent}%off"
                    
                    product = ProductInfo(
                        name=item.get('title', ''),
                        price=f"¥{final_price:.2f}",
                        original_price=f"¥{original_price:.2f}" if original_price != final_price else None,
                        discount=discount,
                        url=item.get('item_url', ''),
                        description=f"来自{item.get('provcity', location)}的商品",
                        image_url=item.get('pict_url', ''),
                        platform="淘宝"
                    )
                    products.append(product)
            
        except Exception as e:
            print(f"❌ 解析淘宝响应失败: {e}")
        
        return products
    
    def _parse_jd_response(self, data: dict, location: str) -> List[ProductInfo]:
        """解析京东API响应"""
        products = []
        try:
            if 'jd_union_open_goods_query_response' in data:
                response = data['jd_union_open_goods_query_response']
                if 'result' in response:
                    result = json.loads(response['result'])
                    
                    for item in result.get('data', []):
                        # 价格处理 - 确保准确性
                        price_info = item.get('priceInfo', {})
                        final_price = float(price_info.get('price', '0'))
                        
                        product = ProductInfo(
                            name=item.get('skuName', ''),
                            price=f"¥{final_price:.2f}",
                            url=item.get('materialUrl', ''),
                            description=f"京东商品，{location}地区配送",
                            image_url=item.get('imageInfo', {}).get('imageList', [{}])[0].get('url', ''),
                            platform="京东"
                        )
                        products.append(product)
            
        except Exception as e:
            print(f"❌ 解析京东响应失败: {e}")
        
        return products
    
    def _parse_amazon_response(self, data: dict, location: str) -> List[ProductInfo]:
        """解析亚马逊API响应"""
        products = []
        try:
            if 'SearchResult' in data and 'Items' in data['SearchResult']:
                items = data['SearchResult']['Items']
                
                for item in items:
                    # 价格处理 - 确保准确性
                    price_amount = 0
                    price_currency = "USD"
                    
                    if 'Offers' in item and 'Listings' in item['Offers']:
                        listings = item['Offers']['Listings']
                        if listings and 'Price' in listings[0]:
                            price_info = listings[0]['Price']
                            price_amount = float(price_info.get('Amount', 0))
                            price_currency = price_info.get('Currency', 'USD')
                    
                    product = ProductInfo(
                        name=item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', ''),
                        price=f"${price_amount:.2f}" if price_currency == 'USD' else f"{price_amount:.2f} {price_currency}",
                        url=item.get('DetailPageURL', ''),
                        description=f"Amazon product, shipping to {location}",
                        image_url=item.get('Images', {}).get('Primary', {}).get('Medium', {}).get('URL', ''),
                        platform="Amazon"
                    )
                    products.append(product)
            
        except Exception as e:
            print(f"❌ 解析亚马逊响应失败: {e}")
        
        return products


class ImageProcessor:
    """图像处理工具"""
    
    @staticmethod
    def download_image(url: str, save_path: str) -> bool:
        """下载并保存图片"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image.save(save_path)
                return True
        except Exception as e:
            print(f"图片下载失败: {e}")
        return False
    
    @staticmethod
    def create_placeholder_image(text: str, save_path: str) -> bool:
        """创建占位图片"""
        try:
            # 创建简单的占位图片
            img = Image.new('RGB', (300, 200), color='lightgray')
            img.save(save_path)
            return True
        except Exception as e:
            print(f"占位图片创建失败: {e}")
        return False


class QueryParser:
    """查询解析器，提取关键信息"""
    
    @staticmethod
    def parse_query(query: str) -> Dict[str, str]:
        """
        解析自然语言查询，提取关键信息
        
        Args:
            query: 自然语言查询
            
        Returns:
            包含product, location, budget等信息的字典
        """
        # 更精确的正则表达式
        location_pattern = r'在([^买购想要需要找搜索]+?)买|在([^买购想要需要找搜索]+?)购买|在([^买购想要需要找搜索]+?)找|([^买购想要需要找搜索]+?)的'
        
        # 改进预算解析 - 支持更多格式
        budget_pattern = r'预算(\d+)[元块万]?|(\d+)[元块万]?预算|(\d+)[元块万]?以下|(\d+)[元块万]?左右|(\d+)[元块万]?以内|(\d+)[元块万]?-(\d+)[元块万]?|(\d+)[元块万]?到(\d+)[元块万]?'
        
        # 商品关键词模式 - 在动作词之后的内容
        product_pattern = r'(?:买|购买|想要|需要|找|搜索)(?:一?个?台?部?只?件?)?(.*?)(?:，|。|$|预算|在)'
        
        location_match = re.search(location_pattern, query)
        budget_match = re.search(budget_pattern, query)
        product_match = re.search(product_pattern, query)
        
        # 提取地点
        location = '中国'  # 默认值
        if location_match:
            # 从各个捕获组中找到非空的地点
            groups = location_match.groups()
            for group in groups:
                if group and group.strip():
                    location = group.strip()
                    break
        
        # 提取预算 - 改进逻辑
        budget = None
        budget_min = None
        budget_max = None
        
        if budget_match:
            groups = budget_match.groups()
            # 查找非空的数字
            numbers = [g for g in groups if g and g.strip().isdigit()]
            if len(numbers) >= 2:
                # 价格区间
                budget_min = int(numbers[0])
                budget_max = int(numbers[1])
                budget = f"{budget_min}-{budget_max}"
            elif len(numbers) == 1:
                # 单一预算
                budget = numbers[0]
        
        # 提取商品名称
        product = query  # 默认使用原查询
        if product_match:
            extracted_product = product_match.group(1)
            if extracted_product and extracted_product.strip():
                product = extracted_product.strip()
        
        # 如果没有匹配到商品，尝试更简单的提取方式
        if not product or product == query:
            # 移除动作词和地点信息，提取剩余的核心内容
            clean_query = query
            # 移除常见的动作词
            clean_query = re.sub(r'^.*?(?:买|购买|想要|需要|找|搜索)', '', clean_query)
            # 移除地点信息
            if location_match:
                clean_query = re.sub(location_pattern, '', clean_query)
            # 移除预算信息
            if budget_match:
                clean_query = re.sub(budget_pattern, '', clean_query)
            # 移除标点符号和多余空格
            clean_query = re.sub(r'[，。,.\s]+', ' ', clean_query).strip()
            
            if clean_query:
                product = clean_query
        
        return {
            'product': product,
            'location': location,
            'budget': budget,
            'budget_min': budget_min,
            'budget_max': budget_max,
            'original_query': query
        }


def filter_products_by_budget(products: List[ProductInfo], budget_min: Optional[int], budget_max: Optional[int]) -> List[ProductInfo]:
    """根据预算筛选商品"""
    if not budget_min and not budget_max:
        return products
    
    filtered_products = []
    for product in products:
        try:
            # 从价格字符串中提取数字
            price_str = product.price.replace('¥', '').replace('$', '').replace(',', '').strip()
            price = float(price_str)
            
            # 预算筛选逻辑
            is_in_budget = True
            if budget_min and price < budget_min:
                is_in_budget = False
            if budget_max and price > budget_max:
                is_in_budget = False
            
            if is_in_budget:
                filtered_products.append(product)
                
        except (ValueError, AttributeError):
            # 如果价格解析失败，保留商品（但会在日志中提示）
            print(f"⚠️ 无法解析商品价格: {product.name} - {product.price}")
            continue
    
    return filtered_products


def format_product_results(products: List[ProductInfo]) -> str:
    """格式化商品搜索结果"""
    if not products:
        return "❌ 抱歉，没有找到相关商品。请尝试：\n1. 修改搜索关键词\n2. 调整预算范围\n3. 检查网络连接"
    
    result = f"🛍️ 为您找到 {len(products)} 个商品：\n\n"
    for i, product in enumerate(products, 1):
        result += f"{i}. **{product.name}**\n"
        result += f"   💰 价格: {product.price}"
        
        if product.original_price and product.discount:
            result += f" (原价: {product.original_price}, {product.discount})"
        
        result += f"\n   🏪 平台: {product.platform}\n"
        result += f"   📝 描述: {product.description}\n"
        result += f"   🔗 链接: {product.url}\n"
        
        if product.image_url:
            result += f"   🖼️ 图片: {product.image_url}\n"
        
        result += "\n"
    
    return result


def validate_api_key(api_key: str, provider: str) -> bool:
    """验证API密钥格式"""
    if provider.lower() == 'openai':
        return api_key.startswith('sk-') and len(api_key) > 20
    elif provider.lower() == 'qwen':
        return api_key.startswith('sk-') and len(api_key) > 20
    return len(api_key) > 10  # 基本长度检查


def get_api_error_message(platform: str) -> str:
    """获取API错误提示信息"""
    messages = {
        'taobao': "⚠️ 淘宝API配置不完整。请在SupportFunction.py中配置真实的API密钥。",
        'jd': "⚠️ 京东联盟API配置不完整。请在SupportFunction.py中配置真实的API密钥。",
        'amazon': "⚠️ 亚马逊API配置不完整。请在SupportFunction.py中配置真实的API密钥。"
    }
    return messages.get(platform, "⚠️ API配置不完整，无法获取真实商品数据。") 