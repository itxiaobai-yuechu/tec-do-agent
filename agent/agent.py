# seo agent
import asyncio
import json
import re
from typing import Optional, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import time
import random


class SEOState(BaseModel):
    url: str
    title: Optional[str] = None
    price: Optional[str] = None
    original_price: Optional[str] = None
    discount: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    sold_count: Optional[int] = None
    shop_name: Optional[str] = None
    category: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


async def scrape_product_information(state: SEOState):
    """
    爬取Shopee商品信息
    """
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # 添加随机延迟，避免被反爬
        await asyncio.sleep(random.uniform(1, 3))

        # 发送请求
        response = requests.get(state.url, headers=headers, timeout=30)
        response.raise_for_status()

        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取商品信息
        state.title = extract_title(soup)
        state.price = extract_price(soup)
        state.original_price = extract_original_price(soup)
        state.discount = extract_discount(soup)
        state.description = extract_description(soup)
        state.images = extract_images(soup)
        state.rating = extract_rating(soup)
        state.review_count = extract_review_count(soup)
        state.sold_count = extract_sold_count(soup)
        state.shop_name = extract_shop_name(soup)
        state.category = extract_category(soup)
        state.attributes = extract_attributes(soup)

        print(f"成功爬取商品信息: {state.title}")

    except Exception as e:
        state.error = f"爬取失败: {str(e)}"
        print(f"爬取失败: {str(e)}")

    return state


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """提取商品标题"""
    try:
        # 尝试多种选择器
        selectors = [
            'h1[data-testid="product-title"]',
            '.product-title',
            'h1',
            '[class*="title"]',
            'title'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 5:
                    return title

        # 如果选择器都失败，尝试从页面标题提取
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # 清理标题，移除网站名称等
            title = re.sub(r'[-|] Shopee.*$', '', title)
            return title.strip()

    except Exception as e:
        print(f"提取标题失败: {e}")

    return None


def extract_price(soup: BeautifulSoup) -> Optional[str]:
    """提取商品价格"""
    try:
        # 尝试多种价格选择器
        selectors = [
            '[data-testid="product-price"]',
            '.product-price',
            '[class*="price"]',
            '.price',
            '[class*="current-price"]'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # 提取价格数字
                price_match = re.search(r'[\d,]+\.?\d*', price_text)
                if price_match:
                    return price_match.group()

        # 尝试从JSON数据中提取
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'price' in script.string.lower():
                # 查找价格相关的JSON数据
                price_match = re.search(
                    r'"price"\s*:\s*([\d,]+\.?\d*)', script.string)
                if price_match:
                    return price_match.group(1)

    except Exception as e:
        print(f"提取价格失败: {e}")

    return None


def extract_original_price(soup: BeautifulSoup) -> Optional[str]:
    """提取原价"""
    try:
        selectors = [
            '[class*="original-price"]',
            '.original-price',
            '[class*="old-price"]',
            '.old-price'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text)
                if price_match:
                    return price_match.group()

    except Exception as e:
        print(f"提取原价失败: {e}")

    return None


def extract_discount(soup: BeautifulSoup) -> Optional[str]:
    """提取折扣信息"""
    try:
        selectors = [
            '[class*="discount"]',
            '.discount',
            '[class*="sale"]',
            '.sale'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                discount_text = element.get_text(strip=True)
                # 提取折扣百分比
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    return f"{discount_match.group(1)}%"

    except Exception as e:
        print(f"提取折扣失败: {e}")

    return None


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    """提取商品描述"""
    try:
        selectors = [
            '[data-testid="product-description"]',
            '.product-description',
            '[class*="description"]',
            '.description'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                if description and len(description) > 10:
                    return description

    except Exception as e:
        print(f"提取描述失败: {e}")

    return None


def extract_images(soup: BeautifulSoup) -> Optional[List[str]]:
    """提取商品图片"""
    try:
        images = []

        # 查找商品图片
        img_selectors = [
            '[data-testid="product-image"] img',
            '.product-image img',
            '[class*="product"] img',
            '.gallery img'
        ]

        for selector in img_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src and src.startswith('http'):
                    images.append(src)

        # 去重并返回
        return list(set(images)) if images else None

    except Exception as e:
        print(f"提取图片失败: {e}")

    return None


def extract_rating(soup: BeautifulSoup) -> Optional[float]:
    """提取商品评分"""
    try:
        selectors = [
            '[data-testid="rating"]',
            '.rating',
            '[class*="rating"]',
            '[class*="score"]'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                rating_text = element.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    return float(rating_match.group(1))

    except Exception as e:
        print(f"提取评分失败: {e}")

    return None


def extract_review_count(soup: BeautifulSoup) -> Optional[int]:
    """提取评论数量"""
    try:
        selectors = [
            '[class*="review"]',
            '.review-count',
            '[class*="comment"]'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                count_text = element.get_text(strip=True)
                count_match = re.search(r'(\d+)', count_text)
                if count_match:
                    return int(count_match.group(1))

    except Exception as e:
        print(f"提取评论数失败: {e}")

    return None


def extract_sold_count(soup: BeautifulSoup) -> Optional[int]:
    """提取销量"""
    try:
        selectors = [
            '[class*="sold"]',
            '.sold-count',
            '[class*="sales"]'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                count_text = element.get_text(strip=True)
                count_match = re.search(r'(\d+)', count_text)
                if count_match:
                    return int(count_match.group(1))

    except Exception as e:
        print(f"提取销量失败: {e}")

    return None


def extract_shop_name(soup: BeautifulSoup) -> Optional[str]:
    """提取店铺名称"""
    try:
        selectors = [
            '[data-testid="shop-name"]',
            '.shop-name',
            '[class*="shop"]',
            '.seller-name'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                shop_name = element.get_text(strip=True)
                if shop_name and len(shop_name) > 1:
                    return shop_name

    except Exception as e:
        print(f"提取店铺名失败: {e}")

    return None


def extract_category(soup: BeautifulSoup) -> Optional[str]:
    """提取商品分类"""
    try:
        selectors = [
            '[class*="breadcrumb"]',
            '.breadcrumb',
            '[class*="category"]',
            '.category'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                category_text = element.get_text(strip=True)
                if category_text and len(category_text) > 3:
                    return category_text

    except Exception as e:
        print(f"提取分类失败: {e}")

    return None


def extract_attributes(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """提取商品属性"""
    try:
        attributes = {}

        # 查找属性表格或列表
        attr_selectors = [
            '[class*="attribute"]',
            '.attribute',
            '[class*="specification"]',
            '.specification'
        ]

        for selector in attr_selectors:
            elements = soup.select(selector)
            for element in elements:
                # 尝试提取键值对
                key_elements = element.find_all(['dt', 'th', 'strong'])
                value_elements = element.find_all(['dd', 'td', 'span'])

                for i, key_elem in enumerate(key_elements):
                    if i < len(value_elements):
                        key = key_elem.get_text(strip=True)
                        value = value_elements[i].get_text(strip=True)
                        if key and value:
                            attributes[key] = value

        return attributes if attributes else None

    except Exception as e:
        print(f"提取属性失败: {e}")

    return None


# 构建工作流
seo_workflow = StateGraph(SEOState)
seo_workflow.add_node("scrape", scrape_product_information)
seo_workflow.set_entry_point("scrape")
seo_workflow.set_finish_point("scrape")
